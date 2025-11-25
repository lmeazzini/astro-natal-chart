"""
Birth chart endpoints for creating and managing natal charts.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.i18n import translate as _
from app.core.i18n.messages import ChartMessages
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.repositories.chart_repository import ChartRepository
from app.schemas.chart import (
    BirthChartCreate,
    BirthChartList,
    BirthChartRead,
    BirthChartUpdate,
    ChartStatusResponse,
    PDFDownloadResponse,
    PDFDownloadURLResponse,
)
from app.services import chart_service
from app.services.s3_service import s3_service
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
        # Check chart limit for unverified users
        if not current_user.email_verified:
            chart_repo = ChartRepository(db)
            chart_count = await chart_repo.count_by_user(UUID(str(current_user.id)))
            if chart_count >= settings.UNVERIFIED_USER_CHART_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=_(
                        ChartMessages.UNVERIFIED_CHART_LIMIT,
                        limit=settings.UNVERIFIED_USER_CHART_LIMIT,
                    ),
                )

        # Create initial chart record (no calculations yet)
        chart = await chart_service.create_birth_chart_async(
            db=db,
            user_id=UUID(str(current_user.id)),
            chart_data=chart_data,
        )

        # Dispatch Celery task to process in background
        generate_birth_chart_task.delay(str(chart.id))

        return chart  # type: ignore[return-value]
    except HTTPException:
        raise
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
    description="Get a specific birth chart by ID. Admins can access any chart.",
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

    Admins can access any chart in the system.

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
            is_admin=current_user.is_admin,
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
        # Block PDF generation for unverified users
        if not current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_(ChartMessages.UNVERIFIED_PDF_BLOCKED),
            )

        # Verify chart exists and user has access
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Verify chart has calculated data
        if not chart.chart_data or chart.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart must be fully calculated before generating PDF. Wait for chart calculations to complete.",
            )

        # Check if PDF is already being generated (prevent concurrent generation)
        if chart.pdf_generating:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"PDF is already being generated for this chart. Task ID: {chart.pdf_task_id}. Please wait for the current generation to complete.",
            )

        # Dispatch Celery task to generate PDF in background
        task = generate_chart_pdf_task.delay(str(chart_id))

        # Mark chart as generating and save task ID
        chart.pdf_generating = True
        chart.pdf_task_id = task.id
        await db.commit()

        return {
            "message": "PDF generation started",
            "chart_id": str(chart_id),
            "task_id": task.id,
        }

    except HTTPException:
        raise
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
    response_model=PDFDownloadResponse,
    summary="Get PDF generation status and download URL",
    description="Check the status of PDF generation and get presigned download URL if ready.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_pdf_status(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PDFDownloadResponse:
    """
    Get PDF generation status and download URL for a birth chart.

    **Workflow:**
    1. After calling POST /charts/{id}/generate-pdf, poll this endpoint
    2. Check status field: 'ready', 'generating', 'failed', or 'not_found'
    3. If status is 'ready', use download_url to download (expires in 1 hour for S3)

    **S3 Integration:**
    - If PDF is stored in S3, returns a presigned URL (valid for 1 hour)
    - If PDF is stored locally, returns local file path
    - Presigned URLs are regenerated on each request

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDF status with download URL and metadata
    """
    from app.core.config import settings

    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Check if PDF exists
        if not chart.pdf_url:
            # No PDF generated yet
            if chart.error_message and "PDF generation failed" in chart.error_message:
                return PDFDownloadResponse(
                    status="failed",
                    message=chart.error_message,
                )
            else:
                return PDFDownloadResponse(
                    status="generating",
                    message="PDF generation is in progress. Please check back in a few moments.",
                )

        # PDF exists - determine download URL
        download_url = None
        expires_in = None

        if chart.pdf_url.startswith("s3://"):
            # S3 URL - generate presigned URL
            download_url = s3_service.generate_presigned_url(
                s3_url=chart.pdf_url,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
            )

            if download_url:
                expires_in = settings.S3_PRESIGNED_URL_EXPIRATION
            else:
                # Failed to generate presigned URL
                return PDFDownloadResponse(
                    status="failed",
                    message="Failed to generate download URL. Please try again.",
                    generated_at=chart.pdf_generated_at,
                )
        else:
            # Local file path - return as-is
            download_url = chart.pdf_url

        return PDFDownloadResponse(
            status="ready",
            download_url=download_url,
            expires_in=expires_in,
            generated_at=chart.pdf_generated_at,
            message="PDF is ready for download.",
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
    "/{chart_id}/download-pdf",
    response_model=PDFDownloadURLResponse,
    summary="Get PDF download URL",
    description="Get the presigned download URL for a birth chart PDF.",
)
@limiter.limit(RateLimits.CHART_READ)
async def download_chart_pdf(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
) -> PDFDownloadURLResponse:
    """
    Get presigned URL for PDF download.

    **Prerequisites:**
    1. Chart must be fully calculated (status='completed')
    2. PDF must have been generated (call POST /charts/{id}/generate-pdf first)
    3. PDF generation must be complete (poll /charts/{id}/pdf-status)

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session
        response: FastAPI response object for setting headers

    Returns:
        PDFDownloadURLResponse with presigned URL or local file URL
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

        # Generate filename
        filename = f"natal_chart_{chart.person_name}_{chart_id}.pdf".replace(" ", "_")

        # Set cache-control headers to prevent browser caching
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, private, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        # Handle S3 URLs - return presigned URL as JSON
        if chart.pdf_url.startswith("s3://"):
            # Generate presigned URL for S3 download
            download_url = s3_service.generate_presigned_url(
                s3_url=chart.pdf_url,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
            )

            if not download_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate download URL from S3. Please try again.",
                )

            # Return presigned URL in JSON response
            return PDFDownloadURLResponse(
                download_url=download_url,
                filename=filename,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
                content_type="application/pdf",
            )

        # Handle local files - for now, just return the path as-is
        # Frontend will need to construct full URL
        return PDFDownloadURLResponse(
            download_url=chart.pdf_url,
            filename=filename,
            expires_in=None,  # Local files don't expire
            content_type="application/pdf",
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
# RECALCULATE ENDPOINT
# ============================================================


@router.post(
    "/{chart_id}/recalculate",
    response_model=BirthChartRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recalculate birth chart",
    description="Force recalculation of all chart data and interpretations.",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def recalculate_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Force recalculation of a birth chart.

    This endpoint triggers a full recalculation of the chart data,
    including all planetary positions, houses, aspects, dignities,
    sect analysis, and other traditional calculations.

    Use this when you want to regenerate the chart with potentially
    updated calculation logic or to refresh cached data.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated birth chart with recalculated data
    """
    try:
        # Verify access and get the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            is_admin=current_user.is_admin,
        )

        # Update status to processing
        chart.status = "processing"
        chart.progress = 0
        await db.commit()
        await db.refresh(chart)

        # Dispatch Celery task to recalculate in background
        generate_birth_chart_task.delay(str(chart_id))

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
