"""
Astrological chart generation Celery tasks for async processing.
"""

import asyncio
from typing import TYPE_CHECKING
from uuid import UUID

from loguru import logger

from app.core.celery_app import celery_app

if TYPE_CHECKING:
    from celery import Task
from app.core.database import AsyncSessionLocal
from app.repositories.chart_repository import ChartRepository
from app.services.astro_service import calculate_birth_chart
from app.services.interpretation_service_rag import InterpretationServiceRAG


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
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries)) from exc


async def _generate_birth_chart_async(task_id: str, chart_id: str) -> dict[str, str]:
    """Async implementation of birth chart generation."""
    async with AsyncSessionLocal() as db:
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

            # Step 1: Calculate astrological data (fast ~100-200ms)
            chart.progress = 20
            await db.commit()
            logger.info(f"Calculating planetary positions for {chart_id}")

            calculated_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system,
            )

            # Step 2: Save calculated data
            chart.chart_data = calculated_data
            chart.progress = 30
            await db.commit()
            logger.info(f"Chart calculations completed for {chart_id}")

            # Step 3: Generate AI interpretations (slow ~20-30 seconds)
            # This will progress from 40% to 90% incrementally
            chart.progress = 40
            await db.commit()
            logger.info(f"Preparing AI interpretations for {chart_id}")

            # Generate RAG-enhanced interpretations
            rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)
            await rag_service.generate_all_rag_interpretations(
                chart=chart,
                chart_data=calculated_data,
            )

            # Step 4: Mark as completed
            chart.status = "completed"
            chart.progress = 100
            chart.error_message = None
            await db.commit()

            logger.info(f"Chart {chart_id} generation completed successfully")
            return {"status": "completed", "message": "Chart generated successfully"}

        except Exception as e:
            # Mark as failed
            chart.status = "failed"
            chart.error_message = str(e)
            await db.commit()

            logger.error(f"Chart {chart_id} generation failed: {e}")
            raise  # Re-raise to trigger Celery retry
