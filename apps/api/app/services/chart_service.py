"""
Birth Chart service for CRUD operations.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart
from app.repositories.audit_repository import AuditRepository
from app.repositories.chart_repository import ChartRepository
from app.schemas.chart import BirthChartCreate, BirthChartUpdate
from app.services.astro_service import calculate_birth_chart
from app.services.interpretation_service_rag import InterpretationServiceRAG


class ChartNotFoundError(Exception):
    """Raised when chart is not found."""

    pass


class UnauthorizedAccessError(Exception):
    """Raised when user tries to access chart they don't own."""

    pass


async def create_birth_chart(
    db: AsyncSession,
    user_id: UUID,
    chart_data: BirthChartCreate,
    generate_interpretations: bool = True,
) -> BirthChart:
    """
    Create a new birth chart with astrological calculations (SYNCHRONOUS - for backwards compatibility).

    **WARNING**: This is the old synchronous endpoint. New code should use create_birth_chart_async.

    Args:
        db: Database session
        user_id: User ID creating the chart
        chart_data: Birth chart data
        generate_interpretations: Whether to automatically generate AI interpretations

    Returns:
        Created birth chart
    """
    chart_repo = ChartRepository(db)

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
        status="completed",  # Immediately completed since sync
        progress=100,
        visibility="private",
    )

    created_chart = await chart_repo.create(chart)

    # Generate AI interpretations automatically using RAG
    if generate_interpretations:
        try:
            rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)
            await rag_service.generate_all_rag_interpretations(
                chart=created_chart,
                chart_data=calculated_data,
            )
            logger.info(f"Generated RAG interpretations for chart {created_chart.id}")
        except Exception as e:
            # Log error but don't fail chart creation
            logger.error(f"Failed to generate RAG interpretations for chart {created_chart.id}: {e}")

    return created_chart


async def create_birth_chart_async(
    db: AsyncSession,
    user_id: UUID,
    chart_data: BirthChartCreate,
) -> BirthChart:
    """
    Create a new birth chart for async processing (returns immediately, calculations run in background).

    **Async Flow:**
    1. Creates initial chart record with status='processing' (no chart_data yet)
    2. Celery task will populate chart_data and interpretations
    3. Client polls GET /charts/{id}/status to track progress

    Args:
        db: Database session
        user_id: User ID creating the chart
        chart_data: Birth chart data

    Returns:
        Created birth chart with status='processing' (no calculations yet)
    """
    chart_repo = ChartRepository(db)

    # Create chart record WITHOUT calculations (will be done by Celery task)
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
        chart_data=None,  # Will be populated by Celery task
        status="processing",
        progress=0,
        visibility="private",
    )

    created_chart = await chart_repo.create(chart)
    logger.info(f"Created chart {created_chart.id} for async processing")

    return created_chart


async def get_user_charts(
    db: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100, include_deleted: bool = False
) -> list[BirthChart]:
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
    chart_repo = ChartRepository(db)
    return await chart_repo.get_all_by_user(
        user_id=user_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
    )


async def get_chart_by_id(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    is_admin: bool = False,
) -> BirthChart:
    """
    Get a birth chart by ID.

    Args:
        db: Database session
        chart_id: Chart ID
        user_id: User ID (for authorization)
        is_admin: If True, bypasses ownership check (admin access)

    Returns:
        Birth chart

    Raises:
        ChartNotFoundError: If chart not found
        UnauthorizedAccessError: If user doesn't own chart (and not admin)
    """
    chart_repo = ChartRepository(db)

    if is_admin:
        # Admin can access any chart
        chart = await chart_repo.get_by_id(chart_id)
    else:
        chart = await chart_repo.get_by_id_and_user(chart_id, user_id)

    if not chart:
        raise ChartNotFoundError(f"Chart {chart_id} not found")

    return chart


def _needs_recalculation(update_data: BirthChartUpdate, chart: BirthChart) -> bool:
    """
    Check if chart update requires recalculation.

    Recalculation is needed when any of these fields change:
    - birth_datetime
    - birth_timezone
    - latitude
    - longitude
    - house_system
    - zodiac_type
    - node_type

    Args:
        update_data: The update data
        chart: Current chart

    Returns:
        True if recalculation is needed
    """
    recalc_fields = [
        "birth_datetime",
        "birth_timezone",
        "latitude",
        "longitude",
        "house_system",
        "zodiac_type",
        "node_type",
    ]

    update_dict = update_data.model_dump(exclude_unset=True)

    for field in recalc_fields:
        if field in update_dict:
            current_value = getattr(chart, field)
            new_value = update_dict[field]
            if current_value != new_value:
                logger.info(f"Field {field} changed: {current_value} -> {new_value}")
                return True

    return False


async def update_birth_chart(
    db: AsyncSession, chart_id: UUID, user_id: UUID, update_data: BirthChartUpdate
) -> BirthChart:
    """
    Update a birth chart with optional recalculation.

    If birth data (datetime, timezone, lat/lon) or technical settings (house_system,
    zodiac_type, node_type) change, the chart will be recalculated.

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
    chart_repo = ChartRepository(db)
    chart = await get_chart_by_id(db, chart_id, user_id)

    # Check if recalculation is needed BEFORE updating fields
    needs_recalc = _needs_recalculation(update_data, chart)

    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)

    for field, value in update_dict.items():
        setattr(chart, field, value)

    # Recalculate chart data if needed
    if needs_recalc:
        logger.info(f"Recalculating chart {chart_id} due to birth data changes")

        calculated_data = calculate_birth_chart(
            birth_datetime=chart.birth_datetime,
            timezone=chart.birth_timezone,
            latitude=chart.latitude,
            longitude=chart.longitude,
            house_system=chart.house_system,
        )

        chart.chart_data = calculated_data

        # Regenerate RAG-enhanced interpretations for recalculated chart
        try:
            rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)
            await rag_service.generate_all_rag_interpretations(
                chart=chart,
                chart_data=calculated_data,
            )
            logger.info(f"Regenerated RAG interpretations for chart {chart.id}")
        except Exception as e:
            # Log error but don't fail update
            logger.error(f"Failed to regenerate RAG interpretations for chart {chart.id}: {e}")

    chart.updated_at = datetime.now(UTC)

    updated_chart = await chart_repo.update(chart)

    # Create audit log entry for chart update (LGPD compliance)
    audit_repo = AuditRepository(db)
    await audit_repo.create_log(
        user_id=user_id,
        action="update_chart",
        resource_type="chart",
        resource_id=chart_id,
        extra_data={
            "fields_updated": list(update_dict.keys()),
            "recalculated": needs_recalc,
        },
    )

    return updated_chart


async def delete_birth_chart(
    db: AsyncSession, chart_id: UUID, user_id: UUID, soft_delete: bool = True
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
    chart_repo = ChartRepository(db)
    chart = await get_chart_by_id(db, chart_id, user_id)

    if soft_delete:
        await chart_repo.soft_delete(chart)
    else:
        await chart_repo.delete(chart)


async def count_user_charts(db: AsyncSession, user_id: UUID, include_deleted: bool = False) -> int:
    """
    Count total number of charts for a user.

    Args:
        db: Database session
        user_id: User ID
        include_deleted: Whether to include soft-deleted charts

    Returns:
        Total count
    """
    chart_repo = ChartRepository(db)
    return await chart_repo.count_by_user(
        user_id=user_id,
        include_deleted=include_deleted,
    )
