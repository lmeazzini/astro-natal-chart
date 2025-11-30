"""
Database storage adapter for interpretations.

This module implements the IInterpretationStorage interface using
the InterpretationRepository for database persistence.
"""

from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.interpretation_storage import IInterpretationStorage
from app.domain.interpretation import InterpretationResult
from app.models.interpretation import ChartInterpretation
from app.repositories.interpretation_repository import InterpretationRepository


class DatabaseInterpretationStorage(IInterpretationStorage):
    """
    Database adapter implementing IInterpretationStorage.

    This adapter wraps the InterpretationRepository to provide
    domain-layer access to database-persisted interpretations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize database storage adapter.

        Args:
            db: SQLAlchemy async database session
        """
        self.repo = InterpretationRepository(db)
        self.db = db

    async def get_by_chart(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str = "pt-BR",
    ) -> list[InterpretationResult]:
        """
        Fetch interpretations from database and convert to domain models.

        Args:
            chart_id: Chart UUID to retrieve interpretations for
            interpretation_type: Optional filter by type
            language: Language code for interpretations

        Returns:
            List of InterpretationResult domain objects
        """
        try:
            # Query database based on filter
            if interpretation_type:
                records = await self.repo.get_by_chart_and_type(chart_id, interpretation_type)
            else:
                records = await self.repo.get_by_chart_id(chart_id)

            # Filter by language (defensive check for legacy data)
            records = [r for r in records if getattr(r, "language", "pt-BR") == language]

            # Convert database models to domain models
            return [self._to_domain_model(r) for r in records]

        except Exception as e:
            logger.error(f"Error fetching interpretations from DB for chart {chart_id}: {e}")
            raise

    async def save(
        self,
        chart_id: UUID,
        interpretation: InterpretationResult,
        language: str = "pt-BR",
    ) -> None:
        """
        Save interpretation to database.

        Args:
            chart_id: Chart UUID the interpretation belongs to
            interpretation: InterpretationResult to save
            language: Language code for interpretation
        """
        try:
            # Create database model from domain model
            db_interpretation = ChartInterpretation(
                chart_id=chart_id,
                interpretation_type=interpretation.interpretation_type,
                subject=interpretation.subject,
                content=interpretation.content,
                openai_model=interpretation.openai_model,
                prompt_version=interpretation.prompt_version,
                language=language,
                rag_sources=interpretation.rag_sources,
            )

            await self.repo.create(db_interpretation)
            await self.db.flush()

            logger.debug(
                f"Saved interpretation to DB: {interpretation.interpretation_type}:"
                f"{interpretation.subject} (chart: {chart_id}, language: {language})"
            )

        except Exception as e:
            logger.error(f"Error saving interpretation to DB for chart {chart_id}: {e}")
            raise

    async def delete(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str | None = None,
    ) -> int:
        """
        Delete interpretations from database.

        Args:
            chart_id: Chart UUID to delete interpretations for
            interpretation_type: Optional filter to delete only specific type
            language: Optional filter to delete only specific language

        Returns:
            Number of interpretations deleted
        """
        try:
            if interpretation_type or language:
                # Selective deletion - fetch then delete
                records = await self.repo.get_by_chart_id(chart_id)

                # Apply filters
                to_delete = []
                for record in records:
                    if interpretation_type and record.interpretation_type != interpretation_type:
                        continue
                    if language and getattr(record, "language", "pt-BR") != language:
                        continue
                    to_delete.append(record)

                # Delete filtered records
                for record in to_delete:
                    await self.repo.delete(record)

                await self.db.flush()
                deleted_count = len(to_delete)

            else:
                # Delete all interpretations for chart
                deleted_count = await self.repo.delete_by_chart_id(chart_id)
                await self.db.flush()

            logger.debug(f"Deleted {deleted_count} interpretations from DB for chart {chart_id}")

            return deleted_count

        except Exception as e:
            logger.error(f"Error deleting interpretations from DB for chart {chart_id}: {e}")
            raise

    async def get_single(
        self,
        interpretation_type: str,
        parameters: dict[str, Any],
        model: str,
        version: str,
        language: str,
    ) -> InterpretationResult | None:
        """
        Get single interpretation by parameters.

        Note: Database storage doesn't support parameter-based lookups.
        This method returns None (cache storage handles this).

        Args:
            interpretation_type: Type of interpretation
            parameters: Parameters dict (not used for DB)
            model: OpenAI model identifier (not used for DB)
            version: Prompt version (not used for DB)
            language: Language code (not used for DB)

        Returns:
            None (database doesn't support parameter-based lookups)
        """
        # Database storage doesn't support parameter hashing lookups
        # This is handled by CacheInterpretationStorage
        return None

    def _to_domain_model(self, record: ChartInterpretation) -> InterpretationResult:
        """
        Convert database model to domain model.

        Args:
            record: ChartInterpretation database model

        Returns:
            InterpretationResult domain model
        """
        return InterpretationResult(
            content=record.content,
            subject=record.subject,
            interpretation_type=record.interpretation_type,
            source="database",
            rag_sources=record.rag_sources,
            prompt_version=record.prompt_version,
            is_outdated=False,  # Determined by fetcher service
            cached=True,
            generated_at=record.created_at,
            openai_model=record.openai_model,
        )
