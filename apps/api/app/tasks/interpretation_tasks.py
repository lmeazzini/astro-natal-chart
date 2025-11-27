"""
Celery tasks for interpretation operations.

This module contains background tasks for asynchronous interpretation
operations, primarily cache-to-database backfilling.
"""

import asyncio
from typing import Any
from uuid import UUID

from loguru import logger

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.interpretation import ChartInterpretation
from app.repositories.interpretation_repository import InterpretationRepository


@celery_app.task(
    name="backfill_interpretation",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def backfill_interpretation_task(
    self: Any,
    chart_id: str,
    interpretation_data: dict[str, Any],
    language: str = "pt-BR",
) -> dict[str, Any]:
    """
    Celery task to backfill cached interpretation to database.

    This task runs asynchronously after a cache hit to persist
    interpretations to the database for future retrieval, avoiding
    the need to regenerate or lookup in cache.

    Flow:
    1. Check if interpretation already exists in DB
    2. If not, create new ChartInterpretation record
    3. Commit to database

    Args:
        self: Celery task instance (bind=True)
        chart_id: Chart UUID string
        interpretation_data: Serialized InterpretationResult dict
        language: Language code ('pt-BR' or 'en-US')

    Returns:
        Task result metadata with status and details

    Raises:
        Exception: Retries up to 3 times on failure
    """

    async def _backfill() -> dict[str, Any]:
        """
        Async function to perform the backfill operation.

        Returns:
            Result metadata
        """
        async with AsyncSessionLocal() as db:
            try:
                repo = InterpretationRepository(db)

                # Check if already exists
                existing = await repo.get_by_chart_and_subject(
                    chart_id=UUID(chart_id),
                    subject=interpretation_data["subject"],
                )

                # Skip if exists with same language
                if existing and getattr(existing, "language", "pt-BR") == language:
                    logger.info(
                        f"Backfill skipped (already exists): "
                        f"{interpretation_data['interpretation_type']}:{interpretation_data['subject']} "
                        f"(chart: {chart_id}, language: {language})"
                    )
                    return {
                        "status": "skipped",
                        "reason": "already_exists",
                        "interpretation_type": interpretation_data["interpretation_type"],
                        "subject": interpretation_data["subject"],
                    }

                # Create new interpretation record
                interpretation = ChartInterpretation(
                    chart_id=UUID(chart_id),
                    interpretation_type=interpretation_data["interpretation_type"],
                    subject=interpretation_data["subject"],
                    content=interpretation_data["content"],
                    openai_model=interpretation_data.get("openai_model", "gpt-4o-mini-rag"),
                    prompt_version=interpretation_data["prompt_version"],
                    language=language,
                    rag_sources=interpretation_data.get("rag_sources"),
                )

                await repo.create(interpretation)
                await db.commit()

                logger.info(
                    f"Backfill successful: "
                    f"{interpretation_data['interpretation_type']}:{interpretation_data['subject']} "
                    f"(chart: {chart_id}, language: {language})"
                )

                return {
                    "status": "success",
                    "interpretation_type": interpretation_data["interpretation_type"],
                    "subject": interpretation_data["subject"],
                    "chart_id": chart_id,
                    "language": language,
                }

            except Exception as e:
                logger.error(
                    f"Backfill error for chart {chart_id}: {e}",
                    exc_info=True,
                )
                await db.rollback()
                raise

    try:
        # Run async function in event loop
        return asyncio.run(_backfill())

    except Exception as exc:
        # Log error and retry
        logger.error(
            f"Backfill task failed (attempt {self.request.retries + 1}/3): {exc}",
            exc_info=True,
        )
        raise self.retry(exc=exc) from exc
