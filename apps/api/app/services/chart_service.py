"""
Birth Chart service for CRUD operations.
"""

from datetime import datetime
from uuid import UUID, uuid4
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart
from app.schemas.chart import BirthChartCreate, BirthChartUpdate
from app.services.astro_service import calculate_birth_chart


class ChartNotFoundError(Exception):
    """Raised when chart is not found."""
    pass


class UnauthorizedAccessError(Exception):
    """Raised when user tries to access chart they don't own."""
    pass


async def create_birth_chart(
    db: AsyncSession,
    user_id: UUID,
    chart_data: BirthChartCreate
) -> BirthChart:
    """
    Create a new birth chart with astrological calculations.

    Args:
        db: Database session
        user_id: User ID creating the chart
        chart_data: Birth chart data

    Returns:
        Created birth chart
    """
    # Calculate astrological data
    calculated_data = calculate_birth_chart(
        birth_datetime=chart_data.birth_datetime,
        timezone=chart_data.birth_timezone,
        latitude=chart_data.latitude,
        longitude=chart_data.longitude,
        house_system=chart_data.house_system,
    )

    # Create chart record
    chart = BirthChart(
        id=uuid4(),
        user_id=user_id,
        person_name=chart_data.person_name,
        gender=chart_data.gender,
        birth_datetime=chart_data.birth_datetime,
        birth_timezone=chart_data.birth_timezone,
        latitude=chart_data.latitude,
        longitude=chart_data.longitude,
        city=chart_data.city,
        country=chart_data.country,
        notes=chart_data.notes,
        tags=chart_data.tags or [],
        house_system=chart_data.house_system,
        zodiac_type=chart_data.zodiac_type,
        node_type=chart_data.node_type,
        chart_data=calculated_data,
        visibility="private",
    )

    db.add(chart)
    await db.commit()
    await db.refresh(chart)

    return chart


async def get_user_charts(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False
) -> List[BirthChart]:
    """
    Get all birth charts for a user.

    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        include_deleted: Whether to include soft-deleted charts

    Returns:
        List of birth charts
    """
    conditions = [BirthChart.user_id == user_id]

    if not include_deleted:
        conditions.append(BirthChart.deleted_at.is_(None))

    stmt = (
        select(BirthChart)
        .where(and_(*conditions))
        .order_by(BirthChart.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_chart_by_id(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID
) -> BirthChart:
    """
    Get a birth chart by ID.

    Args:
        db: Database session
        chart_id: Chart ID
        user_id: User ID (for authorization)

    Returns:
        Birth chart

    Raises:
        ChartNotFoundError: If chart not found
        UnauthorizedAccessError: If user doesn't own chart
    """
    stmt = select(BirthChart).where(
        BirthChart.id == chart_id,
        BirthChart.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    chart = result.scalar_one_or_none()

    if not chart:
        raise ChartNotFoundError(f"Chart {chart_id} not found")

    if chart.user_id != user_id:
        raise UnauthorizedAccessError("You don't have access to this chart")

    return chart


async def update_birth_chart(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    update_data: BirthChartUpdate
) -> BirthChart:
    """
    Update a birth chart.

    Args:
        db: Database session
        chart_id: Chart ID
        user_id: User ID (for authorization)
        update_data: Updated chart data

    Returns:
        Updated birth chart

    Raises:
        ChartNotFoundError: If chart not found
        UnauthorizedAccessError: If user doesn't own chart
    """
    chart = await get_chart_by_id(db, chart_id, user_id)

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(chart, field, value)

    chart.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(chart)

    return chart


async def delete_birth_chart(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    soft_delete: bool = True
) -> None:
    """
    Delete a birth chart.

    Args:
        db: Database session
        chart_id: Chart ID
        user_id: User ID (for authorization)
        soft_delete: If True, soft delete (set deleted_at), else hard delete

    Raises:
        ChartNotFoundError: If chart not found
        UnauthorizedAccessError: If user doesn't own chart
    """
    chart = await get_chart_by_id(db, chart_id, user_id)

    if soft_delete:
        chart.deleted_at = datetime.utcnow()
        await db.commit()
    else:
        await db.delete(chart)
        await db.commit()


async def count_user_charts(
    db: AsyncSession,
    user_id: UUID,
    include_deleted: bool = False
) -> int:
    """
    Count total number of charts for a user.

    Args:
        db: Database session
        user_id: User ID
        include_deleted: Whether to include soft-deleted charts

    Returns:
        Total count
    """
    conditions = [BirthChart.user_id == user_id]

    if not include_deleted:
        conditions.append(BirthChart.deleted_at.is_(None))

    stmt = select(BirthChart).where(and_(*conditions))
    result = await db.execute(stmt)
    charts = result.scalars().all()

    return len(list(charts))
