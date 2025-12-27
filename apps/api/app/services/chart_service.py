"""
Birth Chart service for CRUD operations.

This module provides a ChartService class with dependency injection for better
testability and maintainability. Backward-compatible module-level functions
are kept for gradual migration.
"""

import warnings
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.chart import BirthChart
from app.repositories.audit_repository import AuditRepository
from app.repositories.chart_repository import ChartRepository
from app.repositories.interpretation_repository import InterpretationRepository
from app.schemas.chart import BirthChartCreate, BirthChartUpdate
from app.services.astro_service import calculate_birth_chart
from app.services.interpretation_service_rag import InterpretationServiceRAG
from app.tasks.astro_tasks import generate_birth_chart_task


class ChartNotFoundError(Exception):
    """Raised when chart is not found."""

    pass


class UnauthorizedAccessError(Exception):
    """Raised when user tries to access chart they don't own."""

    pass


class ChartService:
    """
    Service for birth chart operations with dependency injection.

    This class provides CRUD operations for birth charts with repositories
    injected at construction time, making it easier to test and mock.

    Usage:
        # With FastAPI dependency injection
        @router.post("/")
        async def create(
            chart_service: ChartService = Depends(get_chart_service),
        ):
            return await chart_service.create_birth_chart(...)

        # Direct instantiation (e.g., in Celery tasks)
        chart_service = ChartService(db)
        chart = await chart_service.get_chart_by_id(chart_id, user_id)
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize ChartService with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db
        self.chart_repo = ChartRepository(db)
        self.interp_repo = InterpretationRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_birth_chart(
        self,
        user_id: UUID,
        chart_data: BirthChartCreate,
        generate_interpretations: bool = True,
    ) -> BirthChart:
        """
        Create a new birth chart with astrological calculations (SYNCHRONOUS).

        **WARNING**: This is the old synchronous endpoint. New code should use
        create_birth_chart_async.

        Args:
            user_id: User ID creating the chart
            chart_data: Birth chart data
            generate_interpretations: Whether to automatically generate AI interpretations

        Returns:
            Created birth chart
        """
        # Calculate astrological data in BOTH languages
        # This ensures users can switch languages without recalculation
        from app.translations import SUPPORTED_LANGUAGES

        chart_data_by_lang: dict[str, Any] = {}
        for language in SUPPORTED_LANGUAGES:
            logger.info(f"Calculating {language} chart data")
            chart_data_by_lang[language] = calculate_birth_chart(
                birth_datetime=chart_data.birth_datetime,
                timezone=chart_data.birth_timezone,
                latitude=chart_data.latitude,
                longitude=chart_data.longitude,
                house_system=chart_data.house_system,
                language=language,
            )

        # Create chart record with language-keyed chart_data
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
            chart_data=chart_data_by_lang,
            status="completed",  # Immediately completed since sync
            progress=100,
            visibility="private",
        )

        created_chart = await self.chart_repo.create(chart)

        # Generate AI interpretations automatically using RAG
        if generate_interpretations:
            try:
                rag_service = InterpretationServiceRAG(self.db, use_cache=True, use_rag=True)
                # Pass language-keyed chart_data - service will extract language-specific data
                await rag_service.generate_all_rag_interpretations(
                    chart=created_chart,
                    chart_data=chart_data_by_lang,
                )
                logger.info(f"Generated RAG interpretations for chart {created_chart.id}")
            except Exception as e:
                # Log error but don't fail chart creation
                logger.error(
                    f"Failed to generate RAG interpretations for chart {created_chart.id}: {e}"
                )

        return created_chart

    async def create_birth_chart_async(
        self,
        user_id: UUID,
        chart_data: BirthChartCreate,
    ) -> BirthChart:
        """
        Create a new birth chart for async processing.

        Returns immediately, calculations run in background via Celery.

        **Async Flow:**
        1. Creates initial chart record with status='processing' (no chart_data yet)
        2. Celery task will populate chart_data and interpretations
        3. Client polls GET /charts/{id}/status to track progress

        Args:
            user_id: User ID creating the chart
            chart_data: Birth chart data

        Returns:
            Created birth chart with status='processing' (no calculations yet)
        """
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

        created_chart = await self.chart_repo.create(chart)
        logger.info(f"Created chart {created_chart.id} for async processing")

        return created_chart

    async def get_user_charts(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[BirthChart]:
        """
        Get all birth charts for a user.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted charts

        Returns:
            List of birth charts
        """
        return await self.chart_repo.get_all_by_user(
            user_id=user_id,
            skip=skip,
            limit=limit,
            include_deleted=include_deleted,
        )

    async def get_chart_by_id(
        self,
        chart_id: UUID,
        user_id: UUID | None = None,
        is_admin: bool = False,
    ) -> BirthChart:
        """
        Get a birth chart by ID.

        Args:
            chart_id: Chart ID
            user_id: User ID (for authorization). Required if not admin.
            is_admin: If True, bypasses ownership check (admin access)

        Returns:
            Birth chart

        Raises:
            ChartNotFoundError: If chart not found
            UnauthorizedAccessError: If user doesn't own chart (and not admin)
        """
        if is_admin:
            # Admin can access any chart
            chart = await self.chart_repo.get_by_id(chart_id)
        else:
            if user_id is None:
                raise UnauthorizedAccessError("user_id required for non-admin access")
            chart = await self.chart_repo.get_by_id_and_user(chart_id, user_id)

        if not chart:
            raise ChartNotFoundError(f"Chart {chart_id} not found")

        return chart

    @staticmethod
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
        self,
        chart_id: UUID,
        user_id: UUID,
        update_data: BirthChartUpdate,
    ) -> BirthChart:
        """
        Update a birth chart with optional recalculation.

        If birth data (datetime, timezone, lat/lon) or technical settings
        (house_system, zodiac_type, node_type) change, the chart will be recalculated.

        Args:
            chart_id: Chart ID
            user_id: User ID (for authorization)
            update_data: Updated chart data

        Returns:
            Updated birth chart

        Raises:
            ChartNotFoundError: If chart not found
            UnauthorizedAccessError: If user doesn't own chart
        """
        chart = await self.get_chart_by_id(chart_id, user_id)

        # Check if recalculation is needed BEFORE updating fields
        needs_recalc = self._needs_recalculation(update_data, chart)

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(chart, field, value)

        # Recalculate chart data if needed
        if needs_recalc:
            logger.info(f"Recalculating chart {chart_id} due to birth data changes")

            # Clear all existing interpretations since birth data changed
            deleted_count = await self.interp_repo.delete_by_chart_id(chart_id)
            logger.info(
                f"Cleared {deleted_count} interpretations for chart {chart_id} due to recalculation"
            )

            # Clear chart_data so it will be fully regenerated by the Celery task
            chart.chart_data = None

            # Set status back to processing so frontend shows progress bar
            chart.status = "processing"
            chart.progress = 0

        chart.updated_at = datetime.now(UTC)

        updated_chart = await self.chart_repo.update(chart)

        # Create audit log entry for chart update (LGPD compliance)
        await self.audit_repo.create_log(
            user_id=user_id,
            action="update_chart",
            resource_type="chart",
            resource_id=chart_id,
            extra_data={
                "fields_updated": list(update_dict.keys()),
                "recalculated": needs_recalc,
            },
        )

        # Dispatch Celery task to recalculate chart and generate interpretations
        # This runs asynchronously and updates progress incrementally
        if needs_recalc:
            generate_birth_chart_task.delay(str(chart_id))
            logger.info(f"Dispatched chart regeneration task for {chart_id}")

        return updated_chart

    async def delete_birth_chart(
        self,
        chart_id: UUID,
        user_id: UUID,
        soft_delete: bool = True,
    ) -> None:
        """
        Delete a birth chart.

        Args:
            chart_id: Chart ID
            user_id: User ID (for authorization)
            soft_delete: If True, soft delete (set deleted_at), else hard delete

        Raises:
            ChartNotFoundError: If chart not found
            UnauthorizedAccessError: If user doesn't own chart
        """
        chart = await self.get_chart_by_id(chart_id, user_id)

        if soft_delete:
            await self.chart_repo.soft_delete(chart)
        else:
            await self.chart_repo.delete(chart)

    async def count_user_charts(
        self,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> int:
        """
        Count total number of charts for a user.

        Args:
            user_id: User ID
            include_deleted: Whether to include soft-deleted charts

        Returns:
            Total count
        """
        return await self.chart_repo.count_by_user(
            user_id=user_id,
            include_deleted=include_deleted,
        )


# =============================================================================
# FastAPI Dependency Injection
# =============================================================================


def get_chart_service(db: AsyncSession = Depends(get_db)) -> ChartService:
    """
    FastAPI dependency for ChartService.

    Usage:
        @router.post("/")
        async def create_chart(
            chart_service: ChartService = Depends(get_chart_service),
        ):
            ...
    """
    return ChartService(db)


# =============================================================================
# Backward-Compatible Module-Level Functions
# =============================================================================
# These functions are deprecated but kept for backward compatibility.
# New code should use ChartService directly via dependency injection.


async def create_birth_chart(
    db: AsyncSession,
    user_id: UUID,
    chart_data: BirthChartCreate,
    generate_interpretations: bool = True,
) -> BirthChart:
    """
    Deprecated: Use ChartService.create_birth_chart instead.

    Create a new birth chart with astrological calculations.
    """
    warnings.warn(
        "create_birth_chart() is deprecated, use ChartService.create_birth_chart() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.create_birth_chart(user_id, chart_data, generate_interpretations)


async def create_birth_chart_async(
    db: AsyncSession,
    user_id: UUID,
    chart_data: BirthChartCreate,
) -> BirthChart:
    """
    Deprecated: Use ChartService.create_birth_chart_async instead.

    Create a new birth chart for async processing.
    """
    warnings.warn(
        "create_birth_chart_async() is deprecated, use ChartService.create_birth_chart_async() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.create_birth_chart_async(user_id, chart_data)


async def get_user_charts(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    include_deleted: bool = False,
) -> list[BirthChart]:
    """
    Deprecated: Use ChartService.get_user_charts instead.

    Get all birth charts for a user.
    """
    warnings.warn(
        "get_user_charts() is deprecated, use ChartService.get_user_charts() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.get_user_charts(user_id, skip, limit, include_deleted)


async def get_chart_by_id(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    is_admin: bool = False,
) -> BirthChart:
    """
    Deprecated: Use ChartService.get_chart_by_id instead.

    Get a birth chart by ID.
    """
    warnings.warn(
        "get_chart_by_id() is deprecated, use ChartService.get_chart_by_id() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.get_chart_by_id(chart_id, user_id, is_admin)


async def update_birth_chart(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    update_data: BirthChartUpdate,
) -> BirthChart:
    """
    Deprecated: Use ChartService.update_birth_chart instead.

    Update a birth chart with optional recalculation.
    """
    warnings.warn(
        "update_birth_chart() is deprecated, use ChartService.update_birth_chart() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.update_birth_chart(chart_id, user_id, update_data)


async def delete_birth_chart(
    db: AsyncSession,
    chart_id: UUID,
    user_id: UUID,
    soft_delete: bool = True,
) -> None:
    """
    Deprecated: Use ChartService.delete_birth_chart instead.

    Delete a birth chart.
    """
    warnings.warn(
        "delete_birth_chart() is deprecated, use ChartService.delete_birth_chart() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.delete_birth_chart(chart_id, user_id, soft_delete)


async def count_user_charts(
    db: AsyncSession,
    user_id: UUID,
    include_deleted: bool = False,
) -> int:
    """
    Deprecated: Use ChartService.count_user_charts instead.

    Count total number of charts for a user.
    """
    warnings.warn(
        "count_user_charts() is deprecated, use ChartService.count_user_charts() instead",
        DeprecationWarning,
        stacklevel=2,
    )
    service = ChartService(db)
    return await service.count_user_charts(user_id, include_deleted)


# Keep helper function at module level (not part of class API)
def _needs_recalculation(update_data: BirthChartUpdate, chart: BirthChart) -> bool:
    """
    Deprecated: Use ChartService._needs_recalculation instead.

    Check if chart update requires recalculation.
    """
    warnings.warn(
        "_needs_recalculation() is deprecated, use ChartService._needs_recalculation() instead",
        DeprecationWarning,
        stacklevel=2,
    )
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
