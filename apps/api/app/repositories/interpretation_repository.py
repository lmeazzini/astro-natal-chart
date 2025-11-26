"""
Chart Interpretation repository.
"""

from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interpretation import ChartInterpretation
from app.repositories.base import BaseRepository


class InterpretationRepository(BaseRepository[ChartInterpretation]):
    """Repository for ChartInterpretation model."""

    def __init__(self, db: AsyncSession):
        """Initialize Interpretation repository."""
        super().__init__(ChartInterpretation, db)

    async def get_by_chart_id(
        self,
        chart_id: UUID,
    ) -> list[ChartInterpretation]:
        """
        Get all interpretations for a specific chart.

        Args:
            chart_id: Chart UUID

        Returns:
            List of interpretations ordered by type and subject
        """
        stmt = (
            select(ChartInterpretation)
            .where(ChartInterpretation.chart_id == chart_id)
            .order_by(
                ChartInterpretation.interpretation_type,
                ChartInterpretation.subject,
            )
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_chart_and_type(
        self,
        chart_id: UUID,
        interpretation_type: str,
    ) -> list[ChartInterpretation]:
        """
        Get interpretations by chart and type.

        Args:
            chart_id: Chart UUID
            interpretation_type: Type of interpretation ('planet', 'house', 'aspect')

        Returns:
            List of interpretations of specified type
        """
        stmt = (
            select(ChartInterpretation)
            .where(
                and_(
                    ChartInterpretation.chart_id == chart_id,
                    ChartInterpretation.interpretation_type == interpretation_type,
                )
            )
            .order_by(ChartInterpretation.subject)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_chart_and_subject(
        self,
        chart_id: UUID,
        subject: str,
    ) -> ChartInterpretation | None:
        """
        Get specific interpretation by chart and subject.

        Args:
            chart_id: Chart UUID
            subject: Subject of interpretation (e.g., 'Sun', '1', 'Sun-Trine-Moon')

        Returns:
            Interpretation instance or None if not found
        """
        stmt = select(ChartInterpretation).where(
            and_(
                ChartInterpretation.chart_id == chart_id,
                ChartInterpretation.subject == subject,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_chart_id(self, chart_id: UUID) -> int:
        """
        Delete all interpretations for a chart.

        Useful when regenerating interpretations or when chart is deleted.

        Args:
            chart_id: Chart UUID

        Returns:
            Number of interpretations deleted
        """
        stmt = delete(ChartInterpretation).where(ChartInterpretation.chart_id == chart_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def exists_for_chart(self, chart_id: UUID) -> bool:
        """
        Check if interpretations exist for a chart.

        Args:
            chart_id: Chart UUID

        Returns:
            True if at least one interpretation exists, False otherwise
        """
        stmt = (
            select(ChartInterpretation.id).where(ChartInterpretation.chart_id == chart_id).limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
