"""
Tests for BackupS3Service - AWS S3 integration for database backup storage.
"""

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from app.services.backup_s3_service import BackupS3Service


@pytest.fixture
def mock_s3_client():
    """Mock boto3 S3 client."""
    with patch("app.services.backup_s3_service.boto3.client") as mock:
        yield mock.return_value


@pytest.fixture
def mock_settings():
    """Mock settings with Backup S3 enabled."""
    with patch("app.services.backup_s3_service.settings") as mock:
        mock.BACKUP_S3_BUCKET = "test-backup-bucket"
        mock.BACKUP_S3_PREFIX = "backups"
        mock.AWS_REGION = "us-east-1"
        mock.AWS_ACCESS_KEY_ID = "test-key"
        mock.AWS_SECRET_ACCESS_KEY = "test-secret"
        mock.backup_s3_enabled = True
        yield mock


@pytest.fixture
def backup_s3_service_enabled(mock_s3_client, mock_settings):
    """BackupS3Service instance with mocked client (enabled)."""
    service = BackupS3Service()
    service.enabled = True
    service.client = mock_s3_client
    service.bucket_name = "test-backup-bucket"
    service.prefix = "backups"
    service.region = "us-east-1"
    return service


@pytest.fixture
def backup_s3_service_disabled():
    """BackupS3Service instance with S3 disabled (dev mode)."""
    with patch("app.services.backup_s3_service.settings") as mock:
        mock.AWS_ACCESS_KEY_ID = None
        mock.backup_s3_enabled = False
        service = BackupS3Service()
        return service


@pytest.fixture
def tmp_backup_file(tmp_path):
    """Create a temporary backup file for testing."""
    backup_file = tmp_path / "astro_backup_20250120_143000.sql.gz"
    backup_file.write_bytes(b"fake compressed backup data" * 1000)
    return backup_file


class TestBackupS3ServiceInitialization:
    """Test BackupS3Service initialization."""

    def test_init_with_credentials(self, mock_settings, mock_s3_client):
        """Test initialization with valid AWS credentials."""
        service = BackupS3Service()
        assert service.enabled is True
        assert service.bucket_name == "test-backup-bucket"
        assert service.prefix == "backups"
        assert service.region == "us-east-1"

    def test_init_without_credentials(self):
        """Test initialization without AWS credentials (dev mode)."""
        with patch("app.services.backup_s3_service.settings") as mock:
            mock.AWS_ACCESS_KEY_ID = None
            mock.backup_s3_enabled = False

            service = BackupS3Service()
            assert service.enabled is False


class TestBuildKey:
    """Test S3 key building for backups."""

    def test_build_key_with_date_extraction(self, backup_s3_service_enabled):
        """Test building S3 key with date extracted from filename."""
        filename = "astro_backup_20250120_143000.sql.gz"

        key = backup_s3_service_enabled._build_key(filename)

        assert key == "backups/20250120/astro_backup_20250120_143000.sql.gz"

    def test_build_key_strips_path_from_filename(self, backup_s3_service_enabled):
        """Test that path components are stripped from filename."""
        filename = "/tmp/malicious/../astro_backup_20250120_143000.sql.gz"

        key = backup_s3_service_enabled._build_key(filename)

        # Should only use the filename, not the path
        assert "tmp" not in key
        assert "malicious" not in key
        assert key.endswith("astro_backup_20250120_143000.sql.gz")

    def test_build_key_with_invalid_filename_format(self, backup_s3_service_enabled):
        """Test building key with filename that doesn't match expected format."""
        filename = "invalid_backup.sql.gz"

        key = backup_s3_service_enabled._build_key(filename)

        # Should fallback to today's date
        assert key.startswith("backups/")
        assert key.endswith("invalid_backup.sql.gz")


class TestCalculateMD5:
    """Test MD5 checksum calculation."""

    def test_calculate_md5(self, backup_s3_service_enabled, tmp_backup_file):
        """Test MD5 calculation for a file."""
        md5 = backup_s3_service_enabled._calculate_md5(tmp_backup_file)

        assert isinstance(md5, str)
        assert len(md5) == 32  # MD5 hash is 32 hex characters
        assert md5.isalnum()

    def test_calculate_md5_consistency(self, backup_s3_service_enabled, tmp_backup_file):
        """Test MD5 calculation is consistent for same file."""
        md5_1 = backup_s3_service_enabled._calculate_md5(tmp_backup_file)
        md5_2 = backup_s3_service_enabled._calculate_md5(tmp_backup_file)

        assert md5_1 == md5_2


class TestUploadBackup:
    """Test upload_backup method."""

    def test_upload_success(self, backup_s3_service_enabled, tmp_backup_file):
        """Test successful backup upload."""
        # Mock successful upload
        backup_s3_service_enabled.client.upload_file = MagicMock()
        backup_s3_service_enabled.client.head_object = MagicMock(
            return_value={
                "Metadata": {"md5_checksum": backup_s3_service_enabled._calculate_md5(tmp_backup_file)},
                "ETag": '"someetag"',
            }
        )

        s3_url = backup_s3_service_enabled.upload_backup(tmp_backup_file)

        assert s3_url is not None
        assert s3_url.startswith("s3://test-backup-bucket/backups/")
        assert "astro_backup_20250120_143000.sql.gz" in s3_url

        # Verify upload_file was called
        backup_s3_service_enabled.client.upload_file.assert_called_once()

    def test_upload_file_not_found(self, backup_s3_service_enabled, tmp_path):
        """Test upload when backup file doesn't exist."""
        non_existent = tmp_path / "nonexistent.sql.gz"

        s3_url = backup_s3_service_enabled.upload_backup(non_existent)

        assert s3_url is None

    def test_upload_client_error(self, backup_s3_service_enabled, tmp_backup_file):
        """Test upload when S3 client raises ClientError."""
        backup_s3_service_enabled.client.upload_file = MagicMock(
            side_effect=ClientError({"Error": {"Code": "AccessDenied"}}, "upload_file")
        )

        s3_url = backup_s3_service_enabled.upload_backup(tmp_backup_file)

        assert s3_url is None

    def test_upload_no_credentials_error(self, backup_s3_service_enabled, tmp_backup_file):
        """Test upload when AWS credentials are invalid."""
        backup_s3_service_enabled.client.upload_file = MagicMock(
            side_effect=NoCredentialsError()
        )

        s3_url = backup_s3_service_enabled.upload_backup(tmp_backup_file)

        assert s3_url is None

    def test_upload_dev_mode(self, backup_s3_service_disabled, tmp_backup_file):
        """Test upload in dev mode (S3 disabled)."""
        s3_url = backup_s3_service_disabled.upload_backup(tmp_backup_file)

        assert s3_url is not None
        assert s3_url.startswith("file://")
        assert str(tmp_backup_file) in s3_url


class TestUploadWithRetry:
    """Test upload retry logic with exponential backoff."""

    def test_retry_success_on_second_attempt(self, backup_s3_service_enabled, tmp_backup_file):
        """Test successful upload on second attempt."""
        # First attempt fails, second succeeds
        backup_s3_service_enabled.client.upload_file = MagicMock(
            side_effect=[ClientError({"Error": {"Code": "ServiceUnavailable"}}, "upload_file"), None]
        )

        # Mock time.sleep to avoid waiting
        with patch("app.services.backup_s3_service.time.sleep"):
            success = backup_s3_service_enabled._upload_with_retry(
                tmp_backup_file,
                "backups/20250120/astro_backup_20250120_143000.sql.gz",
                max_attempts=3,
                initial_wait=1,
            )

        assert success is True
        assert backup_s3_service_enabled.client.upload_file.call_count == 2

    def test_retry_failure_after_max_attempts(self, backup_s3_service_enabled, tmp_backup_file):
        """Test upload failure after exhausting all retries."""
        # All attempts fail
        backup_s3_service_enabled.client.upload_file = MagicMock(
            side_effect=ClientError({"Error": {"Code": "ServiceUnavailable"}}, "upload_file")
        )

        with patch("app.services.backup_s3_service.time.sleep"):
            success = backup_s3_service_enabled._upload_with_retry(
                tmp_backup_file,
                "backups/20250120/astro_backup_20250120_143000.sql.gz",
                max_attempts=3,
                initial_wait=1,
            )

        assert success is False
        assert backup_s3_service_enabled.client.upload_file.call_count == 3

    def test_retry_exponential_backoff(self, backup_s3_service_enabled, tmp_backup_file):
        """Test that retry uses exponential backoff."""
        backup_s3_service_enabled.client.upload_file = MagicMock(
            side_effect=ClientError({"Error": {"Code": "ServiceUnavailable"}}, "upload_file")
        )

        sleep_times = []

        def mock_sleep(seconds):
            sleep_times.append(seconds)

        with patch("app.services.backup_s3_service.time.sleep", side_effect=mock_sleep):
            backup_s3_service_enabled._upload_with_retry(
                tmp_backup_file,
                "backups/20250120/astro_backup_20250120_143000.sql.gz",
                max_attempts=3,
                initial_wait=5,
            )

        # Should sleep 5s, then 10s (exponential backoff)
        assert sleep_times == [5, 10]


class TestVerifyUploadIntegrity:
    """Test MD5 integrity verification."""

    def test_verify_integrity_match(self, backup_s3_service_enabled, tmp_backup_file):
        """Test integrity verification when checksums match."""
        local_md5 = backup_s3_service_enabled._calculate_md5(tmp_backup_file)

        backup_s3_service_enabled.client.head_object = MagicMock(
            return_value={"Metadata": {"md5_checksum": local_md5}}
        )

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_enabled.verify_upload_integrity(tmp_backup_file, s3_url)

        assert result is True

    def test_verify_integrity_mismatch(self, backup_s3_service_enabled, tmp_backup_file):
        """Test integrity verification when checksums don't match."""
        backup_s3_service_enabled.client.head_object = MagicMock(
            return_value={"Metadata": {"md5_checksum": "wrong_checksum"}}
        )

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_enabled.verify_upload_integrity(tmp_backup_file, s3_url)

        assert result is False

    def test_verify_integrity_uses_etag_fallback(self, backup_s3_service_enabled, tmp_backup_file):
        """Test integrity verification falls back to ETag when no MD5 metadata."""
        local_md5 = backup_s3_service_enabled._calculate_md5(tmp_backup_file)

        backup_s3_service_enabled.client.head_object = MagicMock(
            return_value={"Metadata": {}, "ETag": f'"{local_md5}"'}
        )

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_enabled.verify_upload_integrity(tmp_backup_file, s3_url)

        assert result is True

    def test_verify_integrity_dev_mode(self, backup_s3_service_disabled, tmp_backup_file):
        """Test integrity verification in dev mode."""
        s3_url = f"file://{tmp_backup_file}"
        result = backup_s3_service_disabled.verify_upload_integrity(tmp_backup_file, s3_url)

        assert result is True  # Always returns True in dev mode

    def test_verify_integrity_invalid_url(self, backup_s3_service_enabled, tmp_backup_file):
        """Test integrity verification with invalid S3 URL."""
        result = backup_s3_service_enabled.verify_upload_integrity(
            tmp_backup_file, "invalid-url"
        )

        assert result is False


class TestDownloadBackup:
    """Test download_backup method."""

    def test_download_success(self, backup_s3_service_enabled, tmp_path):
        """Test successful backup download."""
        backup_s3_service_enabled.client.download_file = MagicMock()

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        local_path = tmp_path / "downloaded_backup.sql.gz"

        result = backup_s3_service_enabled.download_backup(s3_url, local_path)

        assert result is True
        backup_s3_service_enabled.client.download_file.assert_called_once_with(
            "test-backup-bucket",
            "backups/20250120/astro_backup_20250120_143000.sql.gz",
            str(local_path),
        )

    def test_download_client_error(self, backup_s3_service_enabled, tmp_path):
        """Test download when S3 client raises ClientError."""
        backup_s3_service_enabled.client.download_file = MagicMock(
            side_effect=ClientError({"Error": {"Code": "NoSuchKey"}}, "download_file")
        )

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        local_path = tmp_path / "downloaded_backup.sql.gz"

        result = backup_s3_service_enabled.download_backup(s3_url, local_path)

        assert result is False

    def test_download_creates_parent_directory(self, backup_s3_service_enabled, tmp_path):
        """Test download creates parent directories if they don't exist."""
        backup_s3_service_enabled.client.download_file = MagicMock()

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        local_path = tmp_path / "nested" / "directory" / "downloaded_backup.sql.gz"

        backup_s3_service_enabled.download_backup(s3_url, local_path)

        assert local_path.parent.exists()

    def test_download_dev_mode(self, backup_s3_service_disabled, tmp_path):
        """Test download in dev mode (S3 disabled)."""
        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        local_path = tmp_path / "downloaded_backup.sql.gz"

        result = backup_s3_service_disabled.download_backup(s3_url, local_path)

        assert result is False

    def test_download_invalid_url(self, backup_s3_service_enabled, tmp_path):
        """Test download with invalid S3 URL."""
        local_path = tmp_path / "downloaded_backup.sql.gz"

        result = backup_s3_service_enabled.download_backup("invalid-url", local_path)

        assert result is False


class TestListBackups:
    """Test list_backups method."""

    def test_list_backups_success(self, backup_s3_service_enabled):
        """Test successful listing of backups."""
        from datetime import datetime

        backup_s3_service_enabled.client.list_objects_v2 = MagicMock(
            return_value={
                "Contents": [
                    {
                        "Key": "backups/20250120/astro_backup_20250120_143000.sql.gz",
                        "Size": 1024000,
                        "LastModified": datetime(2025, 1, 20, 14, 30),
                    },
                    {
                        "Key": "backups/20250119/astro_backup_20250119_030000.sql.gz",
                        "Size": 512000,
                        "LastModified": datetime(2025, 1, 19, 3, 0),
                    },
                ]
            }
        )

        backups = backup_s3_service_enabled.list_backups(30)

        assert len(backups) == 2
        assert backups[0]["filename"] == "astro_backup_20250120_143000.sql.gz"
        assert backups[0]["date"] == "2025-01-20"
        assert backups[0]["size"] == 1024000
        assert backups[0]["url"].startswith("s3://test-backup-bucket/backups/")

    def test_list_backups_empty(self, backup_s3_service_enabled):
        """Test listing when no backups exist."""
        backup_s3_service_enabled.client.list_objects_v2 = MagicMock(return_value={})

        backups = backup_s3_service_enabled.list_backups(30)

        assert backups == []

    def test_list_backups_respects_limit(self, backup_s3_service_enabled):
        """Test that list_backups respects the limit parameter."""
        from datetime import datetime

        # Create 5 mock backups
        contents = [
            {
                "Key": f"backups/2025012{i}/astro_backup_2025012{i}_030000.sql.gz",
                "Size": 1024000,
                "LastModified": datetime(2025, 1, 20 + i, 3, 0),
            }
            for i in range(5)
        ]

        backup_s3_service_enabled.client.list_objects_v2 = MagicMock(
            return_value={"Contents": contents}
        )

        backups = backup_s3_service_enabled.list_backups(limit=3)

        assert len(backups) <= 3

    def test_list_backups_sorted_by_date(self, backup_s3_service_enabled):
        """Test that backups are sorted by last modified date (newest first)."""
        from datetime import datetime

        backup_s3_service_enabled.client.list_objects_v2 = MagicMock(
            return_value={
                "Contents": [
                    {
                        "Key": "backups/20250119/astro_backup_20250119_030000.sql.gz",
                        "Size": 512000,
                        "LastModified": datetime(2025, 1, 19, 3, 0),
                    },
                    {
                        "Key": "backups/20250120/astro_backup_20250120_143000.sql.gz",
                        "Size": 1024000,
                        "LastModified": datetime(2025, 1, 20, 14, 30),
                    },
                ]
            }
        )

        backups = backup_s3_service_enabled.list_backups(30)

        # Newest first
        assert backups[0]["date"] == "2025-01-20"
        assert backups[1]["date"] == "2025-01-19"

    def test_list_backups_dev_mode(self, backup_s3_service_disabled):
        """Test listing backups in dev mode."""
        backups = backup_s3_service_disabled.list_backups(30)

        assert backups == []

    def test_list_backups_client_error(self, backup_s3_service_enabled):
        """Test listing backups when S3 client raises ClientError."""
        backup_s3_service_enabled.client.list_objects_v2 = MagicMock(
            side_effect=ClientError({"Error": {"Code": "AccessDenied"}}, "list_objects_v2")
        )

        backups = backup_s3_service_enabled.list_backups(30)

        assert backups == []


class TestDeleteBackup:
    """Test delete_backup method."""

    def test_delete_success(self, backup_s3_service_enabled):
        """Test successful backup deletion."""
        backup_s3_service_enabled.client.delete_object = MagicMock()

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_enabled.delete_backup(s3_url)

        assert result is True
        backup_s3_service_enabled.client.delete_object.assert_called_once_with(
            Bucket="test-backup-bucket",
            Key="backups/20250120/astro_backup_20250120_143000.sql.gz",
        )

    def test_delete_client_error(self, backup_s3_service_enabled):
        """Test deletion when S3 client raises ClientError."""
        backup_s3_service_enabled.client.delete_object = MagicMock(
            side_effect=ClientError({"Error": {"Code": "NoSuchKey"}}, "delete_object")
        )

        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_enabled.delete_backup(s3_url)

        assert result is False

    def test_delete_dev_mode(self, backup_s3_service_disabled):
        """Test deletion in dev mode."""
        s3_url = "s3://test-backup-bucket/backups/20250120/astro_backup_20250120_143000.sql.gz"
        result = backup_s3_service_disabled.delete_backup(s3_url)

        assert result is True  # Simulated success in dev mode

    def test_delete_invalid_url(self, backup_s3_service_enabled):
        """Test deletion with invalid S3 URL."""
        result = backup_s3_service_enabled.delete_backup("invalid-url")

        assert result is False
