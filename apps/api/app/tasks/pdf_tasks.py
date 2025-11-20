"""
Celery tasks for PDF generation.
"""

import subprocess
import tempfile
from pathlib import Path
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.services.interpretation_service import InterpretationService
from app.services.pdf_service import PDFService


@celery_app.task(
    name="generate_chart_pdf",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def generate_chart_pdf_task(self: celery_app.Task, chart_id_str: str) -> dict[str, str]:  # type: ignore[name-defined]
    """
    Generate PDF report for a birth chart (Celery task).

    This task:
    1. Fetches chart data from database
    2. Auto-generates interpretations if missing (using OpenAI)
    3. Optionally renders chart wheel image (SVG→PNG)
    4. Generates LaTeX source from template
    5. Compiles PDF using pdflatex (2 passes)
    6. Updates database with PDF URL and timestamp
    7. Cleans up temporary files

    Args:
        chart_id_str: Chart UUID as string

    Returns:
        Dictionary with pdf_url and status

    Raises:
        Exception: If PDF generation fails after retries
    """
    chart_id = UUID(chart_id_str)
    logger.info(f"Starting PDF generation for chart {chart_id}")

    try:
        # Run async operations with manually managed event loop
        # This avoids event loop conflicts in Celery workers
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(_generate_pdf_async(chart_id))
            return result
        finally:
            # Give pending tasks time to complete
            loop.run_until_complete(asyncio.sleep(0.1))
            # Close the loop
            loop.close()

    except Exception as exc:
        logger.error(f"PDF generation failed for chart {chart_id}: {exc}")
        # Retry task with exponential backoff
        raise self.retry(exc=exc)


async def _generate_pdf_async(chart_id: UUID) -> dict[str, str]:
    """
    Internal async function for PDF generation.

    Args:
        chart_id: Chart UUID

    Returns:
        Dictionary with pdf_url and status
    """
    # Create fresh async engine to avoid event loop issues in Celery workers
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.core.config import settings

    engine = create_async_engine(
        str(settings.DATABASE_URL),
        echo=False,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=0,
    )

    SessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    pdf_service = PDFService()

    try:
        async with SessionLocal() as db:
            # 1. Fetch chart from database
            logger.info(f"Fetching chart {chart_id} from database")
            stmt = select(BirthChart).where(BirthChart.id == chart_id)
            result = await db.execute(stmt)
            chart = result.scalar_one_or_none()

            if not chart:
                logger.error(f"Chart {chart_id} not found")
                raise ValueError(f"Chart {chart_id} not found")

            if not chart.chart_data:
                logger.error(f"Chart {chart_id} has no calculated data")
                raise ValueError(f"Chart {chart_id} has no calculated data")

            # 2. Check interpretations, generate if missing
            logger.info(f"Checking interpretations for chart {chart_id}")
            interpretation_service = InterpretationService(db)
            interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

            # Check if we need to generate interpretations
            has_planet_interps = bool(interpretations.get('planets'))
            has_house_interps = bool(interpretations.get('houses'))
            has_aspect_interps = bool(interpretations.get('aspects'))

            if not (has_planet_interps and has_house_interps and has_aspect_interps):
                logger.info(f"Generating missing interpretations for chart {chart_id}")
                await interpretation_service.generate_all_interpretations(
                    chart_id=chart_id,
                    chart_data=chart.chart_data,
                )
                # Re-fetch interpretations
                interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)
                logger.info("Interpretations generated successfully")

            # 3. Optionally generate chart wheel image
            # TODO: Implement chart SVG generation from chart_data
            # For now, skip image generation
            chart_image_path = None

            # 4. Prepare template data
            logger.info(f"Preparing template data for chart {chart_id}")
            template_data = pdf_service.prepare_template_data(
                chart_data={
                    **chart.chart_data,
                    'person_name': chart.person_name,
                    'birth_datetime': chart.birth_datetime,
                    'city': chart.city,
                    'country': chart.country,
                    'latitude': float(chart.latitude),
                    'longitude': float(chart.longitude),
                    'house_system': chart.house_system,
                    'zodiac_type': chart.zodiac_type,
                },
                interpretations=interpretations,
                chart_image_path=chart_image_path,
            )

            # 5. Render LaTeX template
            logger.info(f"Rendering LaTeX template for chart {chart_id}")
            latex_source = pdf_service.render_template(template_data)

            # 6. Compile PDF using pdflatex
            logger.info(f"Compiling PDF for chart {chart_id}")
            pdf_path = pdf_service.generate_pdf_path(chart_id)

            # Use temporary directory for LaTeX compilation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                tex_file = temp_path / "document.tex"
                tex_file.write_text(latex_source, encoding='utf-8')

                # Run pdflatex twice (for TOC and cross-references)
                for pass_num in [1, 2]:
                    logger.info(f"Running pdflatex pass {pass_num}/2")
                    process = subprocess.run(
                        [
                            'pdflatex',
                            '-interaction=nonstopmode',
                            '-output-directory', str(temp_path),
                            str(tex_file),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=120,  # 2 minutes timeout
                    )

                    if process.returncode != 0:
                        logger.error(f"pdflatex failed on pass {pass_num}")
                        logger.error(f"stdout: {process.stdout}")
                        logger.error(f"stderr: {process.stderr}")

                        # Only fail on the first pass, second pass errors might be warnings
                        if pass_num == 1:
                            raise RuntimeError(
                                f"PDF compilation failed: {process.stderr[:500]}"
                            )

                # Copy generated PDF to final location
                temp_pdf = temp_path / "document.pdf"
                if not temp_pdf.exists():
                    raise RuntimeError("PDF file was not generated by pdflatex")

                temp_pdf.rename(pdf_path)
                logger.info(f"PDF generated successfully: {pdf_path}")

            # 7. Update database with PDF URL and timestamp
            from datetime import datetime, timezone

            pdf_url = f"/media/pdfs/{pdf_path.name}"
            chart.pdf_url = pdf_url
            chart.pdf_generated_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(f"PDF generation complete for chart {chart_id}: {pdf_url}")

            return {
                'pdf_url': pdf_url,
                'status': 'completed',
            }
    finally:
        # Clean up database engine
        await engine.dispose()


async def _mark_pdf_failed(chart_id: UUID, error_message: str) -> None:
    """
    Mark PDF generation as failed in database.

    Args:
        chart_id: Chart UUID
        error_message: Error message
    """
    async with AsyncSessionLocal() as db:
        stmt = select(BirthChart).where(BirthChart.id == chart_id)
        result = await db.execute(stmt)
        chart = result.scalar_one_or_none()

        if chart:
            chart.error_message = f"PDF generation failed: {error_message[:500]}"
            await db.commit()
            logger.error(f"Marked chart {chart_id} PDF generation as failed")
