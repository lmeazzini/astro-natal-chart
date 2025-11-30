"""
Chart Interpretation repository.
"""

from typing import Any
from uuid import UUID

from loguru import logger
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
        interpretation_type: str | None = None,
        language: str | None = None,
    ) -> ChartInterpretation | None:
        """
        Get specific interpretation by chart and subject.

        Args:
            chart_id: Chart UUID
            subject: Subject of interpretation (e.g., 'Sun', '1', 'Sun-Trine-Moon')
            interpretation_type: Optional type filter ('planet', 'house', 'aspect', 'growth')
            language: Optional language filter (e.g., 'pt-BR', 'en-US')

        Returns:
            Interpretation instance or None if not found
        """
        conditions = [
            ChartInterpretation.chart_id == chart_id,
            ChartInterpretation.subject == subject,
        ]

        if interpretation_type:
            conditions.append(ChartInterpretation.interpretation_type == interpretation_type)

        if language:
            conditions.append(ChartInterpretation.language == language)

        stmt = select(ChartInterpretation).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_interpretation(
        self,
        chart_id: UUID | Any,  # Accept both uuid.UUID and SQLAlchemy UUID
        interpretation_type: str,
        subject: str,
        content: str,
        language: str,
        openai_model: str,
        prompt_version: str,
    ) -> ChartInterpretation:
        """
        Create or update an interpretation (upsert pattern).

        This method handles the unique constraint gracefully:
        - If interpretation exists, updates it
        - If not, creates new one

        Args:
            chart_id: Chart UUID
            interpretation_type: Type ('planet', 'house', 'aspect', 'growth', etc.)
            subject: Subject identifier
            content: Interpretation text
            language: Language code ('pt-BR', 'en-US')
            openai_model: Model used for generation
            prompt_version: Prompt version identifier

        Returns:
            Created or updated interpretation instance
        """
        # Try to find existing interpretation
        existing = await self.get_by_chart_and_subject(
            chart_id=chart_id,
            subject=subject,
            interpretation_type=interpretation_type,
            language=language,
        )

        if existing:
            # Update existing
            existing.content = content
            existing.openai_model = openai_model
            existing.prompt_version = prompt_version
            await self.db.flush()
            logger.debug(
                f"Updated interpretation: {interpretation_type}/{subject} for chart {chart_id}"
            )
            return existing
        else:
            # Create new
            new_interpretation = ChartInterpretation(
                chart_id=chart_id,
                interpretation_type=interpretation_type,
                subject=subject,
                content=content,
                openai_model=openai_model,
                prompt_version=prompt_version,
                language=language,
            )
            self.db.add(new_interpretation)
            await self.db.flush()
            logger.debug(
                f"Created interpretation: {interpretation_type}/{subject} for chart {chart_id}"
            )
            return new_interpretation

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

    async def get_growth_interpretations(
        self,
        chart_id: UUID,
        language: str = "pt-BR",
    ) -> dict[str, ChartInterpretation]:
        """
        Fetch all growth interpretations for a chart.

        Growth interpretations consist of 4 components: points, challenges,
        opportunities, and purpose. This method implements all-or-nothing
        validation: if any component is missing, returns empty dict.

        Args:
            chart_id: Chart UUID
            language: Language code for interpretations (default: "pt-BR")

        Returns:
            Dict with keys: 'points', 'challenges', 'opportunities', 'purpose'
            Empty dict if any component is missing (all-or-nothing).
        """
        stmt = select(ChartInterpretation).where(
            and_(
                ChartInterpretation.chart_id == chart_id,
                ChartInterpretation.interpretation_type == "growth",
                ChartInterpretation.language == language,
            )
        )
        result = await self.db.execute(stmt)
        interpretations = result.scalars().all()

        # Build dict by subject
        growth_dict = {interp.subject: interp for interp in interpretations}

        # Validate all 4 components exist
        required_subjects = {"points", "challenges", "opportunities", "purpose"}
        if set(growth_dict.keys()) != required_subjects:
            logger.warning(
                f"Incomplete growth data for chart {chart_id}: "
                f"found {set(growth_dict.keys())}, expected {required_subjects}"
            )
            return {}  # Return empty if incomplete

        return growth_dict
