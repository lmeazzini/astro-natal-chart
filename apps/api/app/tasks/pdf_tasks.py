"""
Celery tasks for PDF generation.
"""

import shutil
import subprocess
import tempfile
from datetime import UTC
from pathlib import Path
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.services.interpretation_service_rag import InterpretationServiceRAG
from app.services.pdf_service import PDFService
from app.services.s3_service import s3_service


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
        raise self.retry(exc=exc) from exc


async def _generate_pdf_async(chart_id: UUID) -> dict[str, str]:
    """
    Internal async function for PDF generation.

    Args:
        chart_id: Chart UUID

    Returns:
        Dictionary with pdf_url and status
    """
    # Create fresh async engine to avoid event loop issues in Celery workers
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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

            # 1.5. Log if replacing existing PDF (no deletion needed, will overwrite)
            if chart.pdf_url:
                logger.info(f"Will overwrite existing PDF: {chart.pdf_url}")

            # 2. Check interpretations, generate if missing using RAG
            logger.info(f"Checking interpretations for chart {chart_id}")
            from sqlalchemy import select as sql_select

            from app.models.interpretation import ChartInterpretation

            # Check if interpretations exist
            interp_stmt = sql_select(ChartInterpretation).where(ChartInterpretation.chart_id == chart_id)
            interp_result = await db.execute(interp_stmt)
            existing_interps = interp_result.scalars().all()

            # Build interpretations dict from existing records
            interpretations: dict[str, dict[str, str]] = {
                'planets': {},
                'houses': {},
                'aspects': {},
                'arabic_parts': {},
            }
            for interp in existing_interps:
                if interp.interpretation_type in interpretations:
                    interpretations[interp.interpretation_type][interp.subject] = interp.content or ""

            # Check if we need to generate interpretations
            has_planet_interps = bool(interpretations.get('planets'))
            has_house_interps = bool(interpretations.get('houses'))
            has_aspect_interps = bool(interpretations.get('aspects'))

            if not (has_planet_interps and has_house_interps and has_aspect_interps):
                logger.info(f"Generating missing interpretations for chart {chart_id}")
                rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)
                interpretations = await rag_service.generate_all_rag_interpretations(
                    chart=chart,
                    chart_data=chart.chart_data,
                )
                logger.info("RAG interpretations generated successfully")

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

                # Copy macros.tex to temp directory (required by template)
                templates_dir = Path(__file__).parent.parent / "report_templates"
                macros_file = templates_dir / "macros.tex"
                if macros_file.exists():
                    (temp_path / "macros.tex").write_text(
                        macros_file.read_text(encoding='utf-8'),
                        encoding='utf-8'
                    )

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

                    # Check if PDF was generated (LaTeX can return non-zero exit codes with warnings)
                    temp_pdf = temp_path / "document.pdf"

                    if process.returncode != 0:
                        logger.warning(f"pdflatex pass {pass_num} completed with warnings")
                        logger.debug(f"stdout: {process.stdout[-1000:]}")  # Last 1000 chars
                        logger.debug(f"stderr: {process.stderr[-500:]}")    # Last 500 chars

                        # Check if PDF was actually generated despite warnings
                        if not temp_pdf.exists() and pass_num == 1:
                            logger.error(f"pdflatex failed on pass {pass_num} - no PDF generated")
                            logger.error(f"stdout: {process.stdout}")
                            logger.error(f"stderr: {process.stderr}")
                            raise RuntimeError(
                                f"PDF compilation failed: {process.stderr[:500]}"
                            )
                    else:
                        logger.info(f"pdflatex pass {pass_num} completed successfully")

                # Verify PDF was generated after both passes
                temp_pdf = temp_path / "document.pdf"
                if not temp_pdf.exists():
                    raise RuntimeError("PDF file was not generated by pdflatex")

                # Use copy2 instead of rename for cross-filesystem compatibility
                shutil.copy2(temp_pdf, pdf_path)
                logger.info(f"PDF generated successfully: {pdf_path}")

            # 7. Upload PDF to S3 (if configured) or use local path
            from datetime import datetime

            s3_url = None
            if s3_service.enabled:
                # Use fixed filename (no timestamp) to enable overwriting
                filename = "full-report.pdf"

                # Upload to S3 (will overwrite if exists)
                s3_url = s3_service.upload_pdf(
                    file_path=pdf_path,
                    user_id=str(chart.user_id),
                    chart_id=str(chart_id),
                    filename=filename,
                )

                if s3_url:
                    logger.info(f"PDF uploaded to S3: {s3_url}")

                    # Clean up local file after successful upload
                    try:
                        pdf_path.unlink()
                        logger.info(f"Cleaned up local PDF: {pdf_path}")
                    except Exception as e:
                        logger.warning(f"Failed to clean up local PDF: {e}")
                else:
                    logger.warning("S3 upload failed, falling back to local storage")

            # Use S3 URL if available, otherwise use local path
            pdf_url = s3_url or f"/media/pdfs/{pdf_path.name}"

            # 8. Update database with PDF URL, timestamp, and clear generation flags
            chart.pdf_url = pdf_url
            chart.pdf_generated_at = datetime.now(UTC)
            chart.pdf_generating = False
            chart.pdf_task_id = None
            await db.commit()

            logger.info(f"PDF generation complete for chart {chart_id}: {pdf_url}")

            # Old PDF deletion removed - S3 upload now overwrites existing file automatically

            return {
                'pdf_url': pdf_url,
                'status': 'completed',
            }

    except Exception as exc:
        # Mark PDF generation as failed and clear flags
        logger.error(f"PDF generation failed for chart {chart_id}: {exc}")
        try:
            async with SessionLocal() as db:
                stmt = select(BirthChart).where(BirthChart.id == chart_id)
                result = await db.execute(stmt)
                chart = result.scalar_one_or_none()
                if chart:
                    chart.pdf_generating = False
                    chart.pdf_task_id = None
                    await db.commit()
                    logger.info(f"Cleared generation flags for chart {chart_id}")
        except Exception as db_error:
            logger.error(f"Failed to clear generation flags: {db_error}")
        raise exc

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
