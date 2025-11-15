"""
Birth chart endpoints for creating and managing natal charts.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.chart import (
    BirthChartCreate,
    BirthChartList,
    BirthChartRead,
    BirthChartUpdate,
)
from app.services import chart_service

router = APIRouter()


@router.post(
    "/",
    response_model=BirthChartRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create birth chart",
    description="Calculate and save a new birth chart with complete astrological data.",
)
async def create_chart(
    chart_data: BirthChartCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Create a new birth chart.

    Args:
        chart_data: Birth chart data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created birth chart with calculated astrological data
    """
    try:
        chart = await chart_service.create_birth_chart(
            db=db,
            user_id=current_user.id,
            chart_data=chart_data,
        )
        return chart
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating birth chart: {str(e)}",
        ) from e


@router.get(
    "/",
    response_model=BirthChartList,
    summary="List user's birth charts",
    description="Get all birth charts for the current user with pagination.",
)
async def list_charts(
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
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
    )

    total = await chart_service.count_user_charts(
        db=db,
        user_id=current_user.id,
    )

    return BirthChartList(
        charts=charts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{chart_id}",
    response_model=BirthChartRead,
    summary="Get birth chart",
    description="Get a specific birth chart by ID.",
)
async def get_chart(
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
            user_id=current_user.id,
        )
        return chart
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
async def update_chart(
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
            user_id=current_user.id,
            update_data=update_data,
        )
        return chart
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
async def delete_chart(
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
            user_id=current_user.id,
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
