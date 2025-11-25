"""
Birth Chart repository.
"""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation
from app.repositories.base import BaseRepository


class ChartRepository(BaseRepository[BirthChart]):
    """Repository for BirthChart model."""

    def __init__(self, db: AsyncSession):
        """Initialize Chart repository."""
        super().__init__(BirthChart, db)

    async def get_by_id_and_user(
        self,
        chart_id: UUID,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> BirthChart | None:
        """
        Get chart by ID and user ID (for authorization).

        Args:
            chart_id: Chart UUID
            user_id: User UUID
            include_deleted: Whether to include soft-deleted charts

        Returns:
            Chart instance or None if not found
        """
        conditions = [
            BirthChart.id == chart_id,
            BirthChart.user_id == user_id,
        ]

        if not include_deleted:
            conditions.append(BirthChart.deleted_at.is_(None))

        stmt = select(BirthChart).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> list[BirthChart]:
        """
        Get all charts for a user.

        Args:
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include soft-deleted charts

        Returns:
            List of charts
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

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: UUID,
        include_deleted: bool = False,
    ) -> int:
        """
        Count total charts for a user.

        Args:
            user_id: User UUID
            include_deleted: Whether to include soft-deleted charts

        Returns:
            Total count
        """
        conditions = [BirthChart.user_id == user_id]

        if not include_deleted:
            conditions.append(BirthChart.deleted_at.is_(None))

        stmt = select(func.count()).select_from(BirthChart).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def soft_delete(self, chart: BirthChart) -> BirthChart:
        """
        Soft delete a chart by setting deleted_at timestamp.

        Args:
            chart: Chart instance to soft delete

        Returns:
            Updated chart instance
        """
        chart.deleted_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(chart)
        return chart

    async def get_by_share_uuid(self, share_uuid: UUID) -> BirthChart | None:
        """
        Get chart by share UUID.

        Args:
            share_uuid: Share UUID

        Returns:
            Chart instance or None if not found
        """
        stmt = select(BirthChart).where(
            BirthChart.share_uuid == share_uuid,
            BirthChart.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        user_id: UUID,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BirthChart]:
        """
        Search charts by person name.

        Args:
            user_id: User UUID
            search_term: Search term for person name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching charts
        """
        stmt = (
            select(BirthChart)
            .where(
                BirthChart.user_id == user_id,
                BirthChart.person_name.ilike(f"%{search_term}%"),
                BirthChart.deleted_at.is_(None),
            )
            .order_by(BirthChart.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_tags(
        self,
        user_id: UUID,
        tags: list[str],
        skip: int = 0,
        limit: int = 100,
    ) -> list[BirthChart]:
        """
        Get charts by tags.

        Args:
            user_id: User UUID
            tags: List of tags to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of charts matching any of the tags
        """
        stmt = (
            select(BirthChart)
            .where(
                BirthChart.user_id == user_id,
                BirthChart.tags.overlap(tags),  # PostgreSQL array overlap operator
                BirthChart.deleted_at.is_(None),
            )
            .order_by(BirthChart.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_charts_without_interpretations(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[BirthChart]:
        """
        Get all charts that don't have any interpretations yet.

        Useful for batch generating interpretations for existing charts.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of charts without interpretations
        """
        # Subquery to get chart IDs that have interpretations
        subquery = select(ChartInterpretation.chart_id).distinct().subquery()

        # Main query to get charts NOT in the subquery
        stmt = (
            select(BirthChart)
            .where(
                BirthChart.deleted_at.is_(None),
                ~BirthChart.id.in_(select(subquery)),  # NOT IN subquery
            )
            .order_by(BirthChart.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())
