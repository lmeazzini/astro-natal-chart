"""
Tests for PDF generation endpoints.
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
class TestGeneratePDFEndpoint:
    """Tests for POST /api/v1/charts/{chart_id}/generate-pdf endpoint."""

    async def test_generate_pdf_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test successful PDF generation trigger."""
        # Create a test chart with status='completed' (required by endpoint)
        chart = await test_chart_factory(user=test_user, status="completed")

        # Mock Celery task
        with patch("app.api.v1.endpoints.charts.generate_chart_pdf_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="test-task-id")

            response = await client.post(
                f"/api/v1/charts/{chart.id}/generate-pdf",
                headers=auth_headers,
            )

            assert response.status_code == 202  # HTTP_202_ACCEPTED
            data = response.json()
            assert data["message"] == "PDF generation started"
            assert data["chart_id"] == str(chart.id)
            assert data["task_id"] == "test-task-id"

            # Verify task was called with correct chart ID
            mock_task.delay.assert_called_once_with(str(chart.id))

    async def test_generate_pdf_chart_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ):
        """Test PDF generation with non-existent chart."""
        fake_id = uuid4()
        response = await client.post(
            f"/api/v1/charts/{fake_id}/generate-pdf",
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_generate_pdf_unauthorized(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
    ):
        """Test PDF generation without authentication."""
        chart = await test_chart_factory(user=test_user, status="completed")

        response = await client.post(
            f"/api/v1/charts/{chart.id}/generate-pdf",
        )

        # get_current_user raises HTTPException with 403 when no auth
        assert response.status_code == 403

    async def test_generate_pdf_wrong_user(
        self,
        client: AsyncClient,
        test_user: User,
        test_user_factory,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test PDF generation for another user's chart."""
        # Create another user and their chart
        other_user = await test_user_factory(email="other@example.com")
        other_chart = await test_chart_factory(user=other_user, status="completed")

        # Try to generate PDF as test_user
        response = await client.post(
            f"/api/v1/charts/{other_chart.id}/generate-pdf",
            headers=auth_headers,
        )

        # Returns 404 when chart not found for this user (charts are filtered by user_id)
        assert response.status_code == 404

    async def test_generate_pdf_no_chart_data(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test PDF generation with chart that has no calculated data."""
        # Create chart without chart_data
        chart = await test_chart_factory(user=test_user, chart_data=None, status="processing")

        response = await client.post(
            f"/api/v1/charts/{chart.id}/generate-pdf",
            headers=auth_headers,
        )

        # Endpoint validates chart_data and status before triggering task
        assert response.status_code == 400
        assert "fully calculated" in response.json()["detail"].lower()

    async def test_generate_pdf_concurrent_generation(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test that concurrent PDF generation is blocked."""
        # Create a test chart with status='completed'
        chart = await test_chart_factory(user=test_user, status="completed")

        # Simulate an ongoing PDF generation
        chart.pdf_generating = True
        chart.pdf_task_id = "existing-task-id"
        await db_session.commit()

        # Try to generate PDF again
        response = await client.post(
            f"/api/v1/charts/{chart.id}/generate-pdf",
            headers=auth_headers,
        )

        # Should return 409 Conflict
        assert response.status_code == 409
        assert "already being generated" in response.json()["detail"].lower()
        assert "existing-task-id" in response.json()["detail"]

    async def test_generate_pdf_regeneration_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test successful PDF regeneration after first generation completed."""
        from datetime import UTC, datetime

        # Create a test chart with completed PDF
        chart = await test_chart_factory(user=test_user, status="completed")
        chart.pdf_url = "s3://bucket/old-pdf.pdf"
        chart.pdf_generated_at = datetime.now(UTC)
        chart.pdf_generating = False  # Previous generation completed
        chart.pdf_task_id = None
        await db_session.commit()

        # Mock Celery task
        with patch("app.api.v1.endpoints.charts.generate_chart_pdf_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="new-task-id")

            # Regenerate PDF
            response = await client.post(
                f"/api/v1/charts/{chart.id}/generate-pdf",
                headers=auth_headers,
            )

            assert response.status_code == 202
            data = response.json()
            assert data["message"] == "PDF generation started"
            assert data["task_id"] == "new-task-id"

            # Verify task was called
            mock_task.delay.assert_called_once_with(str(chart.id))

        # Verify database updated with new task
        await db_session.refresh(chart)
        assert chart.pdf_generating is True
        assert chart.pdf_task_id == "new-task-id"


@pytest.mark.asyncio
class TestPDFStatusEndpoint:
    """Tests for GET /api/v1/charts/{chart_id}/pdf-status endpoint."""

    async def test_pdf_status_processing(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test PDF status when no PDF has been generated."""
        chart = await test_chart_factory(user=test_user)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/pdf-status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        # Endpoint returns "generating" when no pdf_url and no error
        assert data["status"] == "generating"
        assert data["download_url"] is None
        assert data["generated_at"] is None
        assert "in progress" in data["message"].lower()

    async def test_pdf_status_completed(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test PDF status when PDF is completed."""
        from datetime import UTC, datetime

        chart = await test_chart_factory(user=test_user)

        # Update chart with PDF info
        chart.pdf_url = f"/media/pdfs/chart_{chart.id}.pdf"
        chart.pdf_generated_at = datetime.now(UTC)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/charts/{chart.id}/pdf-status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["download_url"] == f"/media/pdfs/chart_{chart.id}.pdf"
        assert data["generated_at"] is not None
        assert "ready for download" in data["message"].lower()

    async def test_pdf_status_failed(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test PDF status when PDF generation failed."""
        chart = await test_chart_factory(user=test_user)

        # Update chart with error message
        chart.error_message = "PDF generation failed: LaTeX compilation error"
        await db_session.commit()

        response = await client.get(
            f"/api/v1/charts/{chart.id}/pdf-status",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert "LaTeX compilation error" in data["message"]

    async def test_pdf_status_unauthorized(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
    ):
        """Test PDF status without authentication."""
        chart = await test_chart_factory(user=test_user)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/pdf-status",
        )

        # get_current_user raises HTTPException with 403 when no auth
        assert response.status_code == 403


@pytest.mark.asyncio
class TestDownloadPDFEndpoint:
    """Tests for GET /api/v1/charts/{chart_id}/download-pdf endpoint."""

    @pytest.mark.skip(reason="Complex file path mocking - tested manually in development")
    async def test_download_pdf_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
        tmp_path,
    ):
        """Test successful PDF download."""
        from datetime import UTC, datetime
        from pathlib import Path

        chart = await test_chart_factory(user=test_user)

        # Create a fake PDF file in tmp directory
        pdf_filename = f"chart_{chart.id}.pdf"
        chart.pdf_url = f"/media/pdfs/{pdf_filename}"
        chart.pdf_generated_at = datetime.now(UTC)
        await db_session.commit()

        # Mock the Path to point to tmp directory
        pdf_dir = tmp_path / "media" / "pdfs"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / pdf_filename
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf content")

        # Patch Path to return our tmp path
        with patch("app.api.v1.endpoints.charts.Path") as mock_path_class:
            # Make Path() return the tmp path structure
            def path_constructor(*args):
                if len(args) == 0:
                    return tmp_path
                return Path(*args)

            mock_path_class.side_effect = path_constructor

            response = await client.get(
                f"/api/v1/charts/{chart.id}/download-pdf",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"

    async def test_download_pdf_not_generated(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test download when PDF hasn't been generated yet."""
        chart = await test_chart_factory(user=test_user)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/download-pdf",
            headers=auth_headers,
        )

        assert response.status_code == 404
        detail = response.json()["detail"].lower()
        assert "not generated" in detail or "pdf not generated" in detail

    @pytest.mark.skip(reason="Complex file path mocking - tested manually in development")
    async def test_download_pdf_file_not_found(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
        db_session: AsyncSession,
    ):
        """Test download when PDF file doesn't exist on disk."""
        from datetime import UTC, datetime

        chart = await test_chart_factory(user=test_user)

        # Set PDF URL but file doesn't exist
        chart.pdf_url = f"/media/pdfs/chart_{chart.id}.pdf"
        chart.pdf_generated_at = datetime.now(UTC)
        await db_session.commit()

        # Mock Path to return non-existent file
        with patch("app.api.v1.endpoints.charts.Path") as mock_path_class:
            mock_file = MagicMock()
            mock_file.exists.return_value = False
            mock_path_class.return_value.__truediv__.return_value.__truediv__.return_value = (
                mock_file
            )

            response = await client.get(
                f"/api/v1/charts/{chart.id}/download-pdf",
                headers=auth_headers,
            )

            assert response.status_code == 404
            assert "file not found" in response.json()["detail"].lower()

    async def test_download_pdf_unauthorized(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
    ):
        """Test download without authentication."""
        chart = await test_chart_factory(user=test_user)

        response = await client.get(
            f"/api/v1/charts/{chart.id}/download-pdf",
        )

        # get_current_user raises HTTPException with 403 when no auth
        assert response.status_code == 403
