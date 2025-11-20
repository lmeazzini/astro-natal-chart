"""
Birth chart endpoints for creating and managing natal charts.
"""

from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.chart import (
    BirthChartCreate,
    BirthChartList,
    BirthChartRead,
    BirthChartUpdate,
    ChartStatusResponse,
)
from app.services import chart_service
from app.tasks.astro_tasks import generate_birth_chart_task
from app.tasks.pdf_tasks import generate_chart_pdf_task

router = APIRouter()


@router.post(
    "/",
    response_model=BirthChartRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create birth chart (async)",
    description="Create a new birth chart. Calculations run in background. Poll /charts/{id}/status to check progress.",
)
@limiter.limit(RateLimits.CHART_CREATE)
async def create_chart(
    request: Request,
    response: Response,
    chart_data: BirthChartCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Create a new birth chart with async processing.

    **Async Flow:**
    1. Creates initial chart record with status='processing'
    2. Dispatches Celery task to calculate data in background
    3. Returns HTTP 202 Accepted immediately
    4. Client polls GET /charts/{id}/status to track progress

    **Benefits:**
    - Immediate response (no 20-30s wait)
    - Non-blocking user experience
    - Automatic retries on OpenAI failures
    - Scalable via Celery workers

    Args:
        chart_data: Birth chart data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created birth chart with status='processing' (no chart_data yet)
    """
    try:
        # Create initial chart record (no calculations yet)
        chart = await chart_service.create_birth_chart_async(
            db=db,
            user_id=UUID(str(current_user.id)),
            chart_data=chart_data,
        )

        # Dispatch Celery task to process in background
        generate_birth_chart_task.delay(str(chart.id))

        return chart  # type: ignore[return-value]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating birth chart: {str(e)}",
        ) from e


@router.get(
    "/",
    response_model=BirthChartList,
    summary="List user's birth charts",
    description="Get all birth charts for the current user with pagination.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def list_charts(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> BirthChartList:
    """
    List all birth charts for current user.

    Args:
        current_user: Current authenticated user
        db: Database session
        page: Page number (starts at 1)
        page_size: Number of items per page

    Returns:
        Paginated list of birth charts
    """
    skip = (page - 1) * page_size

    charts = await chart_service.get_user_charts(
        db=db,
        user_id=UUID(str(current_user.id)),
        skip=skip,
        limit=page_size,
    )

    total = await chart_service.count_user_charts(
        db=db,
        user_id=UUID(str(current_user.id)),
    )

    return BirthChartList(
        charts=charts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{chart_id}/status",
    response_model=ChartStatusResponse,
    summary="Get chart processing status",
    description="Check processing status of a birth chart. Use for polling while chart is being generated.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_chart_status(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartStatusResponse:
    """
    Get birth chart processing status.

    **Use for polling:**
    - After creating a chart (HTTP 202), poll this endpoint every 2-3 seconds
    - Check status: 'processing' → 'completed' or 'failed'
    - When completed, fetch full chart via GET /charts/{id}

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chart status information (status, progress, error_message)
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )
        return ChartStatusResponse(
            id=chart.id,
            status=chart.status,
            progress=chart.progress,
            error_message=chart.error_message,
            task_id=chart.task_id,
        )
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}",
    response_model=BirthChartRead,
    summary="Get birth chart",
    description="Get a specific birth chart by ID.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Get a birth chart by ID.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Birth chart data
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )
        return chart  # type: ignore[return-value]
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.put(
    "/{chart_id}",
    response_model=BirthChartRead,
    summary="Update birth chart",
    description="Update birth chart metadata (name, notes, tags, etc).",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def update_chart(
    request: Request,
    chart_id: UUID,
    update_data: BirthChartUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Update a birth chart.

    Args:
        chart_id: Birth chart UUID
        update_data: Updated chart data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated birth chart
    """
    try:
        chart = await chart_service.update_birth_chart(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            update_data=update_data,
        )
        return chart  # type: ignore[return-value]
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.delete(
    "/{chart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete birth chart",
    description="Delete a birth chart (soft delete by default).",
)
@limiter.limit(RateLimits.CHART_DELETE)
async def delete_chart(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    hard_delete: bool = Query(False, description="Permanently delete if true"),
) -> None:
    """
    Delete a birth chart.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session
        hard_delete: If true, permanently delete; otherwise soft delete
    """
    try:
        await chart_service.delete_birth_chart(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            soft_delete=not hard_delete,
        )
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


# ============================================================
# PDF EXPORT ENDPOINTS
# ============================================================

@router.post(
    "/{chart_id}/generate-pdf",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate PDF report",
    description="Generate a PDF report for the birth chart. Processing happens in background.",
)
@limiter.limit(RateLimits.CHART_CREATE)
async def generate_chart_pdf(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Generate PDF report for a birth chart (async).

    **Async Flow:**
    1. Verifies chart exists and user has access
    2. Dispatches Celery task to generate PDF in background
    3. Returns HTTP 202 Accepted immediately
    4. Client polls GET /charts/{id}/pdf-status to track progress

    **Auto-generates interpretations:**
    - If chart lacks AI interpretations, they will be generated automatically
    - This ensures complete PDF reports with all sections

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Message with task status
    """
    try:
        # Verify chart exists and user has access
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Verify chart has calculated data
        if not chart.chart_data or chart.status != 'completed':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart must be fully calculated before generating PDF. Wait for chart calculations to complete.",
            )

        # Dispatch Celery task to generate PDF in background
        task = generate_chart_pdf_task.delay(str(chart_id))

        return {
            "message": "PDF generation started",
            "chart_id": str(chart_id),
            "task_id": task.id,
        }

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}/pdf-status",
    summary="Get PDF generation status",
    description="Check the status of PDF generation for a birth chart.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_pdf_status(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str | None]:
    """
    Get PDF generation status for a birth chart.

    **Polling workflow:**
    1. After calling POST /charts/{id}/generate-pdf, poll this endpoint
    2. Check pdf_url field - if not null, PDF is ready
    3. Once ready, use GET /charts/{id}/download-pdf to download

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDF status information
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Determine status based on pdf_url presence
        if chart.pdf_url:
            pdf_status = "completed"
        elif chart.error_message and "PDF generation failed" in chart.error_message:
            pdf_status = "failed"
        else:
            pdf_status = "processing"

        return {
            "chart_id": str(chart_id),
            "pdf_status": pdf_status,
            "pdf_url": chart.pdf_url,
            "pdf_generated_at": chart.pdf_generated_at.isoformat() if chart.pdf_generated_at else None,
            "error_message": chart.error_message if pdf_status == "failed" else None,
        }

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}/download-pdf",
    response_class=FileResponse,
    summary="Download PDF report",
    description="Download the generated PDF report for a birth chart.",
)
@limiter.limit(RateLimits.CHART_READ)
async def download_chart_pdf(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FileResponse:
    """
    Download PDF report for a birth chart.

    **Prerequisites:**
    1. Chart must be fully calculated (status='completed')
    2. PDF must have been generated (call POST /charts/{id}/generate-pdf first)
    3. PDF generation must be complete (poll /charts/{id}/pdf-status)

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDF file download
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Check if PDF exists
        if not chart.pdf_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not generated yet. Call POST /charts/{id}/generate-pdf first.",
            )

        # Construct file path
        media_dir = Path(__file__).parent.parent.parent.parent / "media"
        pdf_path = media_dir / "pdfs" / chart.pdf_url.split('/')[-1]

        # Verify file exists on disk
        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF file not found on server. It may have been deleted or generation failed.",
            )

        # Return file for download
        filename = f"natal_chart_{chart.person_name}_{chart_id}.pdf".replace(" ", "_")
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=filename,
        )

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None
