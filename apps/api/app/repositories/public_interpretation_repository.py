"""
Public Chart Interpretation repository.
"""

from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.public_chart_interpretation import PublicChartInterpretation
from app.repositories.base import BaseRepository


class PublicInterpretationRepository(BaseRepository[PublicChartInterpretation]):
    """Repository for PublicChartInterpretation model."""

    def __init__(self, db: AsyncSession):
        """Initialize Public Interpretation repository."""
        super().__init__(PublicChartInterpretation, db)

    async def get_by_chart_and_subject(
        self,
        chart_id: UUID,
        subject: str,
        interpretation_type: str | None = None,
        language: str | None = None,
    ) -> PublicChartInterpretation | None:
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
            PublicChartInterpretation.chart_id == chart_id,
            PublicChartInterpretation.subject == subject,
        ]

        if interpretation_type:
            conditions.append(PublicChartInterpretation.interpretation_type == interpretation_type)

        if language:
            conditions.append(PublicChartInterpretation.language == language)

        stmt = select(PublicChartInterpretation).where(and_(*conditions))
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
    ) -> PublicChartInterpretation:
        """
        Create or update an interpretation (upsert pattern).

        This method handles updates gracefully:
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
                f"Updated public interpretation: {interpretation_type}/{subject} for chart {chart_id}"
            )
            return existing
        else:
            # Create new
            new_interpretation = PublicChartInterpretation(
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
                f"Created public interpretation: {interpretation_type}/{subject} for chart {chart_id}"
            )
            return new_interpretation
