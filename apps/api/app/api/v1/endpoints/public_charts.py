"""
Public Charts API endpoints.

Provides public access to famous people's natal charts for evaluating RAG interpretations.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.public_chart import (
    PUBLIC_CHART_CATEGORIES,
    PublicChartCreate,
    PublicChartDetail,
    PublicChartList,
    PublicChartPreview,
    PublicChartUpdate,
)
from app.services.public_chart_service import PublicChartService

router = APIRouter(prefix="/public-charts", tags=["public-charts"])


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================


@router.get(
    "",
    response_model=PublicChartList,
    summary="List public charts",
    description="Get a paginated list of public charts with optional filters. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def list_public_charts(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Annotated[str | None, Query(description="Filter by category")] = None,
    search: Annotated[str | None, Query(description="Search by name")] = None,
    sort: Annotated[
        str,
        Query(description="Sort order: name, date, views"),
    ] = "name",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=50, description="Items per page")] = 20,
) -> PublicChartList:
    """
    List all published public charts.

    - **category**: Filter by category (scientist, artist, leader, etc.)
    - **search**: Search term for name
    - **sort**: Sort order (name, date, views)
    - **page**: Page number (1-based)
    - **page_size**: Number of items per page (max 50)
    """
    service = PublicChartService(db)
    return await service.list_charts(
        category=category,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/featured",
    response_model=list[PublicChartPreview],
    summary="Get featured charts",
    description="Get a list of featured public charts. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_featured_charts(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=20, description="Maximum number of charts")] = 10,
) -> list[PublicChartPreview]:
    """Get featured public charts for homepage display."""
    service = PublicChartService(db)
    return await service.get_featured_charts(limit=limit)


@router.get(
    "/categories",
    response_model=list[dict],
    summary="Get categories with counts",
    description="Get all categories with chart counts. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_categories(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """Get all available categories with chart counts."""
    service = PublicChartService(db)
    categories = await service.get_categories_with_counts()

    # Add all possible categories even if empty
    existing = {c["category"] for c in categories}
    for cat in PUBLIC_CHART_CATEGORIES:
        if cat not in existing:
            categories.append({"category": cat, "count": 0})

    return sorted(categories, key=lambda x: x["count"], reverse=True)


@router.get(
    "/{slug}",
    response_model=PublicChartDetail,
    summary="Get public chart by slug",
    description="Get full details of a public chart including chart data. No authentication required.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_public_chart(
    request: Request,
    response: Response,
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicChartDetail:
    """
    Get a public chart by its slug.

    - **slug**: URL-friendly identifier (e.g., 'albert-einstein')

    Returns full chart details including calculated chart data and interpretations.
    Increments view count on each access.
    """
    service = PublicChartService(db)
    chart = await service.get_chart_detail(slug)

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Public chart '{slug}' not found",
        )

    return chart


# ============================================================================
# ADMIN ENDPOINTS (Require admin role)
# ============================================================================

admin_router = APIRouter(prefix="/admin/public-charts", tags=["admin-public-charts"])


@admin_router.get(
    "",
    response_model=PublicChartList,
    summary="List all public charts (admin)",
    description="Admin view of all public charts including unpublished ones.",
)
async def list_public_charts_admin(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    include_unpublished: Annotated[bool, Query(description="Include unpublished")] = True,
) -> PublicChartList:
    """Admin endpoint to list all public charts."""
    service = PublicChartService(db)
    return await service.list_charts_admin(
        page=page,
        page_size=page_size,
        include_unpublished=include_unpublished,
    )


@admin_router.post(
    "",
    response_model=PublicChartDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create public chart (admin)",
    description="Create a new public chart. Calculates chart data automatically.",
)
async def create_public_chart(
    data: PublicChartCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """
    Create a new public chart.

    Chart data will be calculated automatically based on birth information.
    """
    service = PublicChartService(db)

    try:
        chart = await service.create_chart(data)
        return PublicChartDetail.model_validate(chart)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get(
    "/{chart_id}",
    response_model=PublicChartDetail,
    summary="Get public chart by ID (admin)",
    description="Get any public chart by ID, including unpublished ones.",
)
async def get_public_chart_admin(
    chart_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """Admin endpoint to get any chart by ID."""
    service = PublicChartService(db)
    chart = await service.get_chart_by_id(chart_id)

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )

    return PublicChartDetail.model_validate(chart)


@admin_router.put(
    "/{chart_id}",
    response_model=PublicChartDetail,
    summary="Update public chart (admin)",
    description="Update a public chart. Recalculates chart data if birth info changes.",
)
async def update_public_chart(
    chart_id: UUID,
    data: PublicChartUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """
    Update a public chart.

    If birth data changes, chart will be recalculated automatically.
    """
    service = PublicChartService(db)

    try:
        chart = await service.update_chart(chart_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )

    return PublicChartDetail.model_validate(chart)


@admin_router.delete(
    "/{chart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete public chart (admin)",
    description="Permanently delete a public chart.",
)
async def delete_public_chart(
    chart_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> None:
    """Delete a public chart permanently."""
    service = PublicChartService(db)
    deleted = await service.delete_chart(chart_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )
