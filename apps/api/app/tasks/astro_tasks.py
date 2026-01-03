"""
Astrological chart generation Celery tasks for async processing.
"""

import asyncio
from typing import TYPE_CHECKING, Any
from uuid import UUID

from loguru import logger

from app.core.celery_app import celery_app

if TYPE_CHECKING:
    from celery import Task
from app.core.database import create_task_local_session
from app.repositories.chart_repository import ChartRepository
from app.services.astro_service import calculate_birth_chart
from app.services.interpretation_service_rag import InterpretationServiceRAG

# Primary language generated immediately, secondary languages deferred
PRIMARY_LANGUAGE = "pt-BR"


@celery_app.task(bind=True, name="astro.generate_birth_chart", max_retries=3)
def generate_birth_chart_task(self: "Task", chart_id: str) -> dict[str, str]:
    """
    Generate birth chart calculations and interpretations in background.

    **Background Processing Benefits**:
    - Immediate response (HTTP 202)
    - Non-blocking user experience
    - Automatic retries on OpenAI failures
    - Scalable via Celery workers

    Args:
        chart_id: UUID string of the birth chart to process

    Returns:
        Dict with status and message
    """
    try:
        # Store Celery task ID in the chart for tracking
        return asyncio.run(_generate_birth_chart_async(str(self.request.id), chart_id))
    except Exception as exc:
        # Retry with exponential backoff: 60s, 120s, 240s
        logger.error(f"Chart generation failed (attempt {self.request.retries + 1}): {exc}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries)) from exc


async def _generate_birth_chart_async(task_id: str, chart_id: str) -> dict[str, str]:
    """Async implementation of birth chart generation.

    Uses task-local database connections (NullPool) to avoid event loop conflicts
    when Celery runs multiple asyncio.run() calls.
    """
    # Create task-local session factory with NullPool
    TaskSessionLocal, task_engine = create_task_local_session()

    try:
        async with TaskSessionLocal() as db:
            chart_repo = ChartRepository(db)

            # Fetch the chart (should be in 'processing' status with minimal data)
            chart = await chart_repo.get_by_id(UUID(chart_id))

            if not chart:
                logger.error(f"Chart {chart_id} not found")
                return {"status": "failed", "message": "Chart not found"}

            try:
                # Update task_id and initial progress
                chart.task_id = task_id
                chart.progress = 10
                await db.commit()
                logger.info(f"Starting chart generation for {chart_id}")

                # Step 1: Calculate astrological data in BOTH languages (fast ~200-400ms)
                # This ensures users can switch languages without waiting for recalculation
                chart.progress = 20
                await db.commit()
                logger.info(f"Calculating planetary positions for {chart_id}")

                # Generate chart data for both supported languages
                from app.translations import SUPPORTED_LANGUAGES

                chart_data_by_lang: dict[str, Any] = {}
                for language in SUPPORTED_LANGUAGES:
                    logger.info(f"Calculating {language} chart data for {chart_id}")
                    chart_data_by_lang[language] = calculate_birth_chart(
                        birth_datetime=chart.birth_datetime,
                        timezone=chart.birth_timezone,
                        latitude=float(chart.latitude),
                        longitude=float(chart.longitude),
                        house_system=chart.house_system,
                        language=language,
                    )

                # Step 2: Save language-keyed chart data
                chart.chart_data = chart_data_by_lang
                chart.progress = 30
                await db.commit()
                logger.info(
                    f"Chart calculations completed for {chart_id} in {len(SUPPORTED_LANGUAGES)} languages"
                )

                # Step 3: Generate AI interpretations for PRIMARY language only
                # Secondary languages are deferred to background task for faster UX
                chart.progress = 40
                await db.commit()
                logger.info(
                    f"Generating primary language ({PRIMARY_LANGUAGE}) interpretations for {chart_id}"
                )

                # Generate RAG-enhanced interpretations for primary language only
                # Use same session factory for consistency
                async with TaskSessionLocal() as rag_db:
                    rag_service = InterpretationServiceRAG(
                        rag_db, use_cache=True, use_rag=True, language=PRIMARY_LANGUAGE
                    )
                    await rag_service.generate_all_rag_interpretations(
                        chart=chart,
                        chart_data=chart_data_by_lang,
                    )
                    await rag_db.commit()

                chart.progress = 70
                await db.commit()

                # Step 3.5: Generate growth interpretations for primary language only
                logger.info(
                    f"Generating primary language ({PRIMARY_LANGUAGE}) growth interpretations for {chart_id}"
                )
                from app.services.personal_growth_service import PersonalGrowthService

                async with TaskSessionLocal() as growth_db:
                    growth_service = PersonalGrowthService(language=PRIMARY_LANGUAGE, db=growth_db)
                    await growth_service.generate_growth_suggestions(
                        chart_data=chart_data_by_lang,
                        chart_id=UUID(chart_id),
                    )
                    await growth_db.commit()

                chart.progress = 90
                await db.commit()

                # Step 3.6: Queue secondary languages for background processing
                secondary_languages = [
                    lang for lang in SUPPORTED_LANGUAGES if lang != PRIMARY_LANGUAGE
                ]
                for language in secondary_languages:
                    logger.info(
                        f"Queueing secondary language ({language}) interpretations for {chart_id}"
                    )
                    generate_secondary_language_task.delay(chart_id, language)

                # Step 4: Mark as completed
                chart.status = "completed"
                chart.progress = 100
                chart.error_message = None
                await db.commit()

                logger.info(f"Chart {chart_id} generation completed successfully")
                return {"status": "completed", "message": "Chart generated successfully"}

            except Exception as e:
                # Mark as failed - use try/except for safe commit
                # Session might be in a bad state if a concurrent commit was in progress
                try:
                    chart.status = "failed"
                    chart.error_message = str(e)[:500]  # Truncate long error messages
                    await db.commit()
                except Exception as commit_error:
                    logger.warning(
                        f"Failed to commit error status for chart {chart_id}: {commit_error}"
                    )
                    try:
                        await db.rollback()
                    except Exception:
                        pass  # Session is in an unrecoverable state, let it close naturally

                logger.error(f"Chart {chart_id} generation failed: {e}")
                raise  # Re-raise to trigger Celery retry
    finally:
        # Always dispose the task-local engine to clean up connections
        await task_engine.dispose()


@celery_app.task(bind=True, name="astro.generate_secondary_language", max_retries=3)
def generate_secondary_language_task(self: "Task", chart_id: str, language: str) -> dict[str, str]:
    """
    Generate interpretations for a secondary language in background.

    This task is queued after the primary language generation completes,
    allowing users to see their chart ~50% faster while secondary languages
    generate in the background.

    Args:
        chart_id: UUID string of the birth chart
        language: Language code (e.g., 'en-US')

    Returns:
        Dict with status and message
    """
    try:
        return asyncio.run(_generate_secondary_language_async(chart_id, language))
    except Exception as exc:
        logger.error(
            f"Secondary language ({language}) generation failed for chart {chart_id} "
            f"(attempt {self.request.retries + 1}): {exc}"
        )
        # Retry with exponential backoff: 30s, 60s, 120s
        raise self.retry(exc=exc, countdown=30 * (2**self.request.retries)) from exc


async def _generate_secondary_language_async(chart_id: str, language: str) -> dict[str, str]:
    """Async implementation of secondary language generation.

    Uses task-local database connections (NullPool) to avoid event loop conflicts
    when Celery runs multiple asyncio.run() calls.
    """
    # Create task-local session factory with NullPool
    TaskSessionLocal, task_engine = create_task_local_session()

    try:
        async with TaskSessionLocal() as db:
            chart_repo = ChartRepository(db)

            # Fetch the chart
            chart = await chart_repo.get_by_id(UUID(chart_id))

            if not chart:
                logger.error(f"Chart {chart_id} not found for secondary language generation")
                return {"status": "failed", "message": "Chart not found"}

            if not chart.chart_data:
                logger.error(
                    f"Chart {chart_id} has no chart_data for secondary language generation"
                )
                return {"status": "failed", "message": "Chart data not available"}

            try:
                logger.info(
                    f"Starting secondary language ({language}) generation for chart {chart_id}"
                )

                # Generate RAG-enhanced interpretations for secondary language
                async with TaskSessionLocal() as rag_db:
                    rag_service = InterpretationServiceRAG(
                        rag_db, use_cache=True, use_rag=True, language=language
                    )
                    await rag_service.generate_all_rag_interpretations(
                        chart=chart,
                        chart_data=chart.chart_data,
                    )
                    await rag_db.commit()

                # Generate growth interpretations for secondary language
                from app.services.personal_growth_service import PersonalGrowthService

                async with TaskSessionLocal() as growth_db:
                    growth_service = PersonalGrowthService(language=language, db=growth_db)
                    await growth_service.generate_growth_suggestions(
                        chart_data=chart.chart_data,
                        chart_id=UUID(chart_id),
                    )
                    await growth_db.commit()

                logger.info(
                    f"Secondary language ({language}) generation completed for chart {chart_id}"
                )
                return {
                    "status": "completed",
                    "message": f"Secondary language ({language}) generated successfully",
                }

            except Exception as e:
                logger.error(
                    f"Secondary language ({language}) generation failed for chart {chart_id}: {e}"
                )
                raise  # Re-raise to trigger Celery retry
    finally:
        # Always dispose the task-local engine to clean up connections
        await task_engine.dispose()
