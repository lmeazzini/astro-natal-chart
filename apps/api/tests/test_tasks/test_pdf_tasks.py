"""
Tests for PDF generation Celery tasks.
"""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.tasks.pdf_tasks import _generate_pdf_async, generate_chart_pdf_task


@pytest.fixture
def sample_chart_in_db():
    """Mock chart object from database."""
    chart_id = uuid4()
    return MagicMock(
        id=chart_id,
        person_name="Test Person",
        birth_datetime=datetime(1990, 5, 15, 14, 30, tzinfo=UTC),
        birth_timezone="America/Sao_Paulo",
        city="São Paulo",
        country="Brazil",
        latitude=-23.5505,
        longitude=-46.6333,
        house_system="placidus",
        zodiac_type="tropical",
        chart_data={
            "planets": [
                {
                    "name": "Sun",
                    "longitude": 54.123,
                    "sign": "Taurus",
                    "degree": 24.123,
                    "house": 10,
                }
            ],
            "houses": [{"number": 1, "cusp": 123.456, "sign": "Leo"}],
            "aspects": [
                {
                    "planet1": "Sun",
                    "planet2": "Moon",
                    "aspect": "trine",
                    "angle": 120.0,
                }
            ],
            "chart_info": {"ascendant": 123.456, "mc": 234.567},
        },
        pdf_url=None,
        pdf_generated_at=None,
        error_message=None,
    )


@pytest.fixture
def sample_interpretations():
    """Mock interpretations from service."""
    return {
        "planets": [
            {
                "planet_name": "Sun",
                "sign": "Taurus",
                "house": 10,
                "interpretation": "The Sun in Taurus...",
            }
        ],
        "houses": [
            {"house_number": 1, "sign": "Leo", "interpretation": "The 1st house..."}
        ],
        "aspects": [
            {
                "planet1": "Sun",
                "planet2": "Moon",
                "aspect_type": "trine",
                "interpretation": "Sun trine Moon...",
            }
        ],
    }


class TestGenerateChartPDFTask:
    """Tests for generate_chart_pdf_task Celery task."""

    def test_task_success(self, sample_chart_in_db, sample_interpretations):
        """Test successful PDF generation task."""
        chart_id = sample_chart_in_db.id

        with patch("app.tasks.pdf_tasks.asyncio.new_event_loop") as mock_loop_factory:
            mock_loop = MagicMock()
            mock_loop_factory.return_value = mock_loop

            # Mock the async result
            mock_result = {
                "pdf_url": f"/media/pdfs/chart_{chart_id}.pdf",
                "status": "completed",
            }
            mock_loop.run_until_complete.return_value = mock_result

            result = generate_chart_pdf_task(str(chart_id))

            assert result["status"] == "completed"
            assert "pdf_url" in result
            mock_loop.close.assert_called_once()

    def test_task_retry_on_error(self):
        """Test task retry on error."""
        chart_id = uuid4()
        mock_task = MagicMock()

        with patch("app.tasks.pdf_tasks.asyncio.new_event_loop") as mock_loop_factory:
            mock_loop = MagicMock()
            mock_loop_factory.return_value = mock_loop
            mock_loop.run_until_complete.side_effect = Exception("Test error")

            # Bind the task instance
            task_func = generate_chart_pdf_task
            task_func.retry = mock_task.retry
            task_func.retry.side_effect = Exception("Retry triggered")

            with pytest.raises(Exception, match="Retry triggered"):
                task_func(str(chart_id))

            mock_task.retry.assert_called_once()


@pytest.mark.asyncio
class TestGeneratePDFAsync:
    """Tests for _generate_pdf_async internal function."""

    async def test_generate_pdf_success(
        self, sample_chart_in_db, sample_interpretations, tmp_path
    ):
        """Test successful async PDF generation."""
        chart_id = sample_chart_in_db.id

        # Mock database session and query
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chart_in_db
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()

        # Mock SessionLocal context manager
        mock_session_local = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_db
        mock_session_local.return_value.__aexit__.return_value = None

        # Mock engine
        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        # Mock InterpretationService
        mock_interp_service = AsyncMock()
        mock_interp_service.get_interpretations_by_chart.return_value = (
            sample_interpretations
        )

        # Mock PDFService
        mock_pdf_service = MagicMock()
        mock_pdf_service.prepare_template_data.return_value = {
            "person_name": "Test",
            "planets": [],
        }
        mock_pdf_service.render_template.return_value = "\\documentclass{article}"
        pdf_path = tmp_path / "test.pdf"
        mock_pdf_service.generate_pdf_path.return_value = pdf_path

        # Create fake PDF file
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(b"%PDF-1.4")

        # Mock subprocess for pdflatex
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = ""
        mock_process.stderr = ""

        with (
            patch(
                "app.tasks.pdf_tasks.create_async_engine", return_value=mock_engine
            ),
            patch(
                "app.tasks.pdf_tasks.async_sessionmaker", return_value=mock_session_local
            ),
            patch(
                "app.tasks.pdf_tasks.InterpretationService",
                return_value=mock_interp_service,
            ),
            patch("app.tasks.pdf_tasks.PDFService", return_value=mock_pdf_service),
            patch("app.tasks.pdf_tasks.subprocess.run", return_value=mock_process),
            patch("app.tasks.pdf_tasks.tempfile.TemporaryDirectory") as mock_temp,
        ):
            # Setup temp directory mock
            mock_temp.return_value.__enter__.return_value = str(tmp_path)

            result = await _generate_pdf_async(chart_id)

            assert result["status"] == "completed"
            assert "/media/pdfs/" in result["pdf_url"]
            mock_engine.dispose.assert_called_once()

    async def test_generate_pdf_chart_not_found(self):
        """Test PDF generation when chart is not found."""
        chart_id = uuid4()

        # Mock database session returning None
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        mock_session_local = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_db
        mock_session_local.return_value.__aexit__.return_value = None

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        with (
            patch(
                "app.tasks.pdf_tasks.create_async_engine", return_value=mock_engine
            ),
            patch(
                "app.tasks.pdf_tasks.async_sessionmaker", return_value=mock_session_local
            ),
            pytest.raises(ValueError, match="not found"),
        ):
            await _generate_pdf_async(chart_id)

        mock_engine.dispose.assert_called_once()

    async def test_generate_pdf_no_chart_data(self, sample_chart_in_db):
        """Test PDF generation when chart has no calculated data."""
        chart_id = sample_chart_in_db.id
        sample_chart_in_db.chart_data = None

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chart_in_db
        mock_db.execute.return_value = mock_result

        mock_session_local = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_db
        mock_session_local.return_value.__aexit__.return_value = None

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        with (
            patch(
                "app.tasks.pdf_tasks.create_async_engine", return_value=mock_engine
            ),
            patch(
                "app.tasks.pdf_tasks.async_sessionmaker", return_value=mock_session_local
            ),
            pytest.raises(ValueError, match="no calculated data"),
        ):
            await _generate_pdf_async(chart_id)

        mock_engine.dispose.assert_called_once()

    async def test_generate_pdf_latex_compilation_error(
        self, sample_chart_in_db, sample_interpretations, tmp_path
    ):
        """Test PDF generation with LaTeX compilation error."""
        chart_id = sample_chart_in_db.id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chart_in_db
        mock_db.execute.return_value = mock_result

        mock_session_local = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_db
        mock_session_local.return_value.__aexit__.return_value = None

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        mock_interp_service = AsyncMock()
        mock_interp_service.get_interpretations_by_chart.return_value = (
            sample_interpretations
        )

        mock_pdf_service = MagicMock()
        mock_pdf_service.prepare_template_data.return_value = {"person_name": "Test"}
        mock_pdf_service.render_template.return_value = "\\documentclass{article}"
        mock_pdf_service.generate_pdf_path.return_value = tmp_path / "test.pdf"

        # Mock failed pdflatex compilation
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "LaTeX Error: Unknown command"

        with (
            patch(
                "app.tasks.pdf_tasks.create_async_engine", return_value=mock_engine
            ),
            patch(
                "app.tasks.pdf_tasks.async_sessionmaker", return_value=mock_session_local
            ),
            patch(
                "app.tasks.pdf_tasks.InterpretationService",
                return_value=mock_interp_service,
            ),
            patch("app.tasks.pdf_tasks.PDFService", return_value=mock_pdf_service),
            patch("app.tasks.pdf_tasks.subprocess.run", return_value=mock_process),
            patch("app.tasks.pdf_tasks.tempfile.TemporaryDirectory") as mock_temp,
            pytest.raises(RuntimeError, match="PDF compilation failed"),
        ):
            mock_temp.return_value.__enter__.return_value = str(tmp_path)
            await _generate_pdf_async(chart_id)

        mock_engine.dispose.assert_called_once()

    async def test_generate_pdf_with_interpretation_generation(
        self, sample_chart_in_db, tmp_path
    ):
        """Test PDF generation triggers interpretation generation when missing."""
        chart_id = sample_chart_in_db.id

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_chart_in_db
        mock_db.execute.return_value = mock_result
        mock_db.commit = AsyncMock()

        mock_session_local = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_db
        mock_session_local.return_value.__aexit__.return_value = None

        mock_engine = AsyncMock()
        mock_engine.dispose = AsyncMock()

        # Mock InterpretationService - first call returns empty, second returns full
        mock_interp_service = AsyncMock()
        empty_interps = {"planets": [], "houses": [], "aspects": []}
        full_interps = {
            "planets": [{"planet_name": "Sun", "interpretation": "Test"}],
            "houses": [{"house_number": 1, "interpretation": "Test"}],
            "aspects": [
                {"planet1": "Sun", "planet2": "Moon", "interpretation": "Test"}
            ],
        }
        mock_interp_service.get_interpretations_by_chart.side_effect = [
            empty_interps,
            full_interps,
        ]
        mock_interp_service.generate_all_interpretations = AsyncMock()

        mock_pdf_service = MagicMock()
        mock_pdf_service.prepare_template_data.return_value = {"person_name": "Test"}
        mock_pdf_service.render_template.return_value = "\\documentclass{article}"
        pdf_path = tmp_path / "test.pdf"
        mock_pdf_service.generate_pdf_path.return_value = pdf_path
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        pdf_path.write_bytes(b"%PDF-1.4")

        mock_process = MagicMock()
        mock_process.returncode = 0

        with (
            patch(
                "app.tasks.pdf_tasks.create_async_engine", return_value=mock_engine
            ),
            patch(
                "app.tasks.pdf_tasks.async_sessionmaker", return_value=mock_session_local
            ),
            patch(
                "app.tasks.pdf_tasks.InterpretationService",
                return_value=mock_interp_service,
            ),
            patch("app.tasks.pdf_tasks.PDFService", return_value=mock_pdf_service),
            patch("app.tasks.pdf_tasks.subprocess.run", return_value=mock_process),
            patch("app.tasks.pdf_tasks.tempfile.TemporaryDirectory") as mock_temp,
        ):
            mock_temp.return_value.__enter__.return_value = str(tmp_path)

            result = await _generate_pdf_async(chart_id)

            # Verify interpretations were generated
            mock_interp_service.generate_all_interpretations.assert_called_once_with(
                chart_id=chart_id,
                chart_data=sample_chart_in_db.chart_data,
            )

            assert result["status"] == "completed"
            mock_engine.dispose.assert_called_once()
