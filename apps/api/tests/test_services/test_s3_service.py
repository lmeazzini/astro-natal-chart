"""
Tests for S3Service - AWS S3 integration for PDF storage.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from botocore.exceptions import ClientError

from app.services.s3_service import S3Service


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client."""
    with patch("app.services.s3_service.boto3.client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_settings():
    """Mock settings with S3 enabled."""
    with patch("app.services.s3_service.settings") as mock:
        mock.S3_BUCKET_NAME = "test-bucket"
        mock.S3_PREFIX = "birth-charts"
        mock.AWS_REGION = "us-east-1"
        mock.AWS_ACCESS_KEY_ID = "test-key"
        mock.AWS_SECRET_ACCESS_KEY = "test-secret"
        mock.s3_enabled = True
        mock.S3_PRESIGNED_URL_EXPIRATION = 3600
        yield mock


@pytest.fixture
def s3_service_enabled(mock_s3_client, mock_settings):
    """S3Service instance with mocked client (enabled)."""
    service = S3Service()
    service.enabled = True
    service.client = mock_s3_client
    service.bucket_name = "test-bucket"
    service.prefix = "birth-charts"
    service.region = "us-east-1"
    return service


@pytest.fixture
def s3_service_disabled():
    """S3Service instance with S3 disabled (dev mode)."""
    with patch("app.services.s3_service.settings") as mock:
        mock.AWS_ACCESS_KEY_ID = None
        mock.s3_enabled = False
        service = S3Service()
        return service


class TestS3ServiceInitialization:
    """Test S3Service initialization."""

    def test_init_with_credentials(self, mock_settings, mock_s3_client):
        """Test initialization with valid AWS credentials."""
        service = S3Service()
        assert service.enabled is True
        assert service.bucket_name == "test-bucket"
        assert service.prefix == "birth-charts"
        assert service.region == "us-east-1"

    def test_init_without_credentials(self):
        """Test initialization without AWS credentials (dev mode)."""
        with patch("app.services.s3_service.settings") as mock:
            mock.AWS_ACCESS_KEY_ID = None
            mock.s3_enabled = False

            service = S3Service()
            assert service.enabled is False


class TestBuildKey:
    """Test S3 key building."""

    def test_build_key_with_prefix(self, s3_service_enabled):
        """Test building S3 key with prefix."""
        user_id = str(uuid4())
        chart_id = str(uuid4())
        filename = "report.pdf"

        key = s3_service_enabled._build_key(user_id, chart_id, filename)

        assert key == f"birth-charts/{user_id}/{chart_id}/report.pdf"

    def test_build_key_strips_path_from_filename(self, s3_service_enabled):
        """Test that path components are stripped from filename."""
        user_id = str(uuid4())
        chart_id = str(uuid4())
        filename = "/tmp/malicious/../report.pdf"

        key = s3_service_enabled._build_key(user_id, chart_id, filename)

        # Should only use the filename, not the path
        assert "tmp" not in key
        assert "malicious" not in key
        assert key.endswith("report.pdf")


class TestUploadPDF:
    """Test PDF upload to S3."""

    def test_upload_pdf_success(self, s3_service_enabled, tmp_path):
        """Test successful PDF upload."""
        # Create temporary PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\ntest content")

        user_id = str(uuid4())
        chart_id = str(uuid4())

        # Upload
        result = s3_service_enabled.upload_pdf(
            file_path=pdf_file,
            user_id=user_id,
            chart_id=chart_id,
        )

        # Verify
        assert result is not None
        assert result.startswith("s3://test-bucket/birth-charts/")
        assert user_id in result
        assert chart_id in result

        # Verify boto3 client was called
        s3_service_enabled.client.upload_file.assert_called_once()

    def test_upload_pdf_file_not_found(self, s3_service_enabled):
        """Test upload with non-existent file."""
        user_id = str(uuid4())
        chart_id = str(uuid4())

        result = s3_service_enabled.upload_pdf(
            file_path="/nonexistent/file.pdf",
            user_id=user_id,
            chart_id=chart_id,
        )

        assert result is None

    def test_upload_pdf_disabled(self, s3_service_disabled, tmp_path):
        """Test upload when S3 is disabled (dev mode)."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\ntest")

        result = s3_service_disabled.upload_pdf(
            file_path=pdf_file,
            user_id=str(uuid4()),
            chart_id=str(uuid4()),
        )

        # Should return local file path
        assert result is not None
        assert result.startswith("file://")
        assert str(pdf_file) in result

    def test_upload_pdf_client_error(self, s3_service_enabled, tmp_path):
        """Test upload with S3 client error."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\ntest")

        # Mock client error
        s3_service_enabled.client.upload_file.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
            "PutObject",
        )

        result = s3_service_enabled.upload_pdf(
            file_path=pdf_file,
            user_id=str(uuid4()),
            chart_id=str(uuid4()),
        )

        assert result is None


class TestUploadPDFFromBytes:
    """Test PDF upload from bytes."""

    def test_upload_pdf_from_bytes_success(self, s3_service_enabled):
        """Test successful PDF upload from bytes."""
        pdf_bytes = b"%PDF-1.4\ntest content"
        user_id = str(uuid4())
        chart_id = str(uuid4())
        filename = "report.pdf"

        result = s3_service_enabled.upload_pdf_from_bytes(
            pdf_bytes=pdf_bytes,
            user_id=user_id,
            chart_id=chart_id,
            filename=filename,
        )

        assert result is not None
        assert result.startswith("s3://test-bucket/birth-charts/")

        # Verify boto3 client was called
        s3_service_enabled.client.put_object.assert_called_once()

    def test_upload_pdf_from_bytes_disabled(self, s3_service_disabled):
        """Test upload from bytes when S3 is disabled."""
        pdf_bytes = b"%PDF-1.4\ntest"

        result = s3_service_disabled.upload_pdf_from_bytes(
            pdf_bytes=pdf_bytes,
            user_id=str(uuid4()),
            chart_id=str(uuid4()),
            filename="report.pdf",
        )

        # Should return memory indicator
        assert result is not None
        assert result.startswith("memory://")


class TestGeneratePresignedURL:
    """Test presigned URL generation."""

    def test_generate_presigned_url_success(self, s3_service_enabled):
        """Test successful presigned URL generation."""
        s3_url = "s3://test-bucket/birth-charts/user123/chart456/report.pdf"
        expected_url = "https://test-bucket.s3.amazonaws.com/path/to/file.pdf?signature=xyz"

        # Mock presigned URL generation
        s3_service_enabled.client.generate_presigned_url.return_value = expected_url

        result = s3_service_enabled.generate_presigned_url(s3_url, expires_in=3600)

        assert result == expected_url
        s3_service_enabled.client.generate_presigned_url.assert_called_once_with(
            "get_object",
            Params={
                "Bucket": "test-bucket",
                "Key": "birth-charts/user123/chart456/report.pdf",
            },
            ExpiresIn=3600,
        )

    def test_generate_presigned_url_invalid_format(self, s3_service_enabled):
        """Test presigned URL generation with invalid S3 URL."""
        result = s3_service_enabled.generate_presigned_url("https://invalid.com/file.pdf")
        assert result is None

        result = s3_service_enabled.generate_presigned_url("s3://bucket-only")
        assert result is None

    def test_generate_presigned_url_disabled(self, s3_service_disabled):
        """Test presigned URL generation when S3 is disabled."""
        result = s3_service_disabled.generate_presigned_url(
            "s3://bucket/key/file.pdf"
        )
        assert result is None

    def test_generate_presigned_url_client_error(self, s3_service_enabled):
        """Test presigned URL generation with client error."""
        s3_service_enabled.client.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey", "Message": "Key not found"}},
            "GetObject",
        )

        result = s3_service_enabled.generate_presigned_url(
            "s3://bucket/key/file.pdf"
        )
        assert result is None


class TestDeletePDF:
    """Test PDF deletion from S3."""

    def test_delete_pdf_success(self, s3_service_enabled):
        """Test successful PDF deletion."""
        s3_url = "s3://test-bucket/birth-charts/user123/chart456/report.pdf"

        result = s3_service_enabled.delete_pdf(s3_url)

        assert result is True
        s3_service_enabled.client.delete_object.assert_called_once_with(
            Bucket="test-bucket",
            Key="birth-charts/user123/chart456/report.pdf",
        )

    def test_delete_pdf_invalid_url(self, s3_service_enabled):
        """Test deletion with invalid S3 URL."""
        result = s3_service_enabled.delete_pdf("https://invalid.com/file.pdf")
        assert result is False

    def test_delete_pdf_disabled(self, s3_service_disabled):
        """Test deletion when S3 is disabled."""
        result = s3_service_disabled.delete_pdf("s3://bucket/key/file.pdf")
        assert result is True  # Simulates success in dev mode


class TestListPDFs:
    """Test listing PDFs for a chart."""

    def test_list_pdfs_for_chart_success(self, s3_service_enabled):
        """Test successful PDF listing."""
        user_id = str(uuid4())
        chart_id = str(uuid4())

        # Mock S3 response
        s3_service_enabled.client.list_objects_v2.return_value = {
            "Contents": [
                {"Key": f"birth-charts/{user_id}/{chart_id}/report1.pdf"},
                {"Key": f"birth-charts/{user_id}/{chart_id}/report2.pdf"},
            ]
        }

        result = s3_service_enabled.list_pdfs_for_chart(user_id, chart_id)

        assert len(result) == 2
        assert all(url.startswith("s3://test-bucket/") for url in result)

    def test_list_pdfs_for_chart_empty(self, s3_service_enabled):
        """Test listing when no PDFs exist."""
        s3_service_enabled.client.list_objects_v2.return_value = {}

        result = s3_service_enabled.list_pdfs_for_chart(str(uuid4()), str(uuid4()))

        assert result == []

    def test_list_pdfs_for_chart_disabled(self, s3_service_disabled):
        """Test listing when S3 is disabled."""
        result = s3_service_disabled.list_pdfs_for_chart(str(uuid4()), str(uuid4()))
        assert result == []


class TestPDFExists:
    """Test PDF existence check."""

    def test_pdf_exists_true(self, s3_service_enabled):
        """Test PDF exists check (file exists)."""
        s3_url = "s3://test-bucket/birth-charts/user/chart/report.pdf"

        # Mock successful head_object (file exists)
        s3_service_enabled.client.head_object.return_value = {"ContentLength": 12345}

        result = s3_service_enabled.pdf_exists(s3_url)

        assert result is True

    def test_pdf_exists_false(self, s3_service_enabled):
        """Test PDF exists check (file not found)."""
        s3_url = "s3://test-bucket/birth-charts/user/chart/report.pdf"

        # Mock 404 error
        s3_service_enabled.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404", "Message": "Not Found"}},
            "HeadObject",
        )

        result = s3_service_enabled.pdf_exists(s3_url)

        assert result is False

    def test_pdf_exists_disabled(self, s3_service_disabled):
        """Test PDF exists when S3 is disabled."""
        result = s3_service_disabled.pdf_exists("s3://bucket/key/file.pdf")
        assert result is False

    def test_pdf_exists_invalid_url(self, s3_service_enabled):
        """Test PDF exists with invalid URL."""
        result = s3_service_enabled.pdf_exists("https://invalid.com/file.pdf")
        assert result is False
