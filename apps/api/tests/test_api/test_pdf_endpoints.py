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
        # Create a test chart
        chart = await test_chart_factory(user=test_user)

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
        chart = await test_chart_factory(user=test_user)

        response = await client.post(
            f"/api/v1/charts/{chart.id}/generate-pdf",
        )

        assert response.status_code == 401

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
        other_chart = await test_chart_factory(user=other_user)

        # Try to generate PDF as test_user
        response = await client.post(
            f"/api/v1/charts/{other_chart.id}/generate-pdf",
            headers=auth_headers,
        )

        assert response.status_code == 404  # Chart not found for this user

    async def test_generate_pdf_no_chart_data(
        self,
        client: AsyncClient,
        test_user: User,
        test_chart_factory,
        auth_headers: dict[str, str],
    ):
        """Test PDF generation with chart that has no calculated data."""
        # Create chart without chart_data
        chart = await test_chart_factory(user=test_user, chart_data=None)

        with patch("app.api.v1.endpoints.charts.generate_chart_pdf_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="test-task-id")

            response = await client.post(
                f"/api/v1/charts/{chart.id}/generate-pdf",
                headers=auth_headers,
            )

            # Should still trigger task - task will handle the error
            assert response.status_code == 202  # HTTP_202_ACCEPTED


@pytest.mark.asyncio
class TestPDFStatusEndpoint:
    """Tests for GET /api/v1/charts/{chart_id}/pdf-status endpoint."""

    async def test_pdf_status_idle(
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
        assert data["chart_id"] == str(chart.id)
        assert data["pdf_status"] == "idle"
        assert data["pdf_url"] is None
        assert data["pdf_generated_at"] is None
        assert data["error_message"] is None

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
        assert data["pdf_status"] == "completed"
        assert data["pdf_url"] == f"/media/pdfs/chart_{chart.id}.pdf"
        assert data["pdf_generated_at"] is not None

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
        assert data["pdf_status"] == "failed"
        assert "LaTeX compilation error" in data["error_message"]

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

        assert response.status_code == 401


@pytest.mark.asyncio
class TestDownloadPDFEndpoint:
    """Tests for GET /api/v1/charts/{chart_id}/download-pdf endpoint."""

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

        chart = await test_chart_factory(user=test_user)

        # Create a fake PDF file
        pdf_dir = tmp_path / "media" / "pdfs"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = pdf_dir / f"chart_{chart.id}.pdf"
        pdf_path.write_bytes(b"%PDF-1.4 fake pdf content")

        # Update chart with PDF URL
        chart.pdf_url = f"/media/pdfs/chart_{chart.id}.pdf"
        chart.pdf_generated_at = datetime.now(UTC)
        await db_session.commit()

        with patch("app.api.v1.endpoints.charts.Path") as mock_path:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_file.read_bytes.return_value = b"%PDF-1.4 fake pdf content"
            mock_path.return_value = mock_file

            response = await client.get(
                f"/api/v1/charts/{chart.id}/download-pdf",
                headers=auth_headers,
            )

            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert "attachment" in response.headers["content-disposition"]
            assert b"fake pdf content" in response.content

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
        assert "not been generated" in response.json()["detail"].lower()

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

        with patch("app.api.v1.endpoints.charts.Path") as mock_path:
            mock_file = MagicMock()
            mock_file.exists.return_value = False
            mock_path.return_value = mock_file

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

        assert response.status_code == 401
