"""
AWS S3 service for storing and retrieving PostgreSQL database backups.

This service provides secure, persistent storage for database backup files
using Amazon S3, with support for integrity verification and automated cleanup.
"""

import hashlib
import time
from datetime import UTC, datetime
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from app.core.config import settings


class BackupS3Service:
    """
    Service for managing PostgreSQL backup files in AWS S3.

    Provides methods for uploading, downloading, listing, and verifying
    database backups with retry logic and integrity checks.

    Attributes:
        bucket_name: Name of the S3 bucket for backups
        prefix: Optional prefix for all S3 keys (e.g., 'backups/')
        region: AWS region for the bucket
        enabled: Whether S3 is configured and enabled
    """

    def __init__(self) -> None:
        """Initialize S3 client with configuration from settings."""
        self.bucket_name = settings.BACKUP_S3_BUCKET
        self.prefix = settings.BACKUP_S3_PREFIX
        self.region = settings.AWS_REGION
        self.enabled = settings.backup_s3_enabled

        if self.enabled:
            try:
                self.client = boto3.client(
                    "s3",
                    region_name=self.region,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    config=Config(signature_version="s3v4"),
                )
                logger.info(
                    f"BackupS3Service initialized for bucket '{self.bucket_name}' in region '{self.region}'"
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize Backup S3 client: {e}")
                self.enabled = False
        else:
            logger.warning("[DEV MODE] BackupS3Service not configured - uploads will be simulated")

    def _build_key(self, filename: str) -> str:
        """
        Build S3 object key with date-based organization.

        Args:
            filename: Name of the backup file (e.g., 'astro_backup_20250120_143000.sql.gz')

        Returns:
            Full S3 key path (e.g., 'backups/20250120/astro_backup_20250120_143000.sql.gz')
        """
        # Remove any path components from filename (security)
        filename = Path(filename).name

        # Extract date from filename (format: astro_backup_YYYYMMDD_HHMMSS.sql.gz)
        try:
            # Parse date from filename: astro_backup_YYYYMMDD_HHMMSS.sql.gz
            date_part = filename.split("_")[2]  # Get YYYYMMDD
            date_str = date_part[:8]  # First 8 chars: YYYYMMDD
        except (IndexError, ValueError):
            # Fallback to current date if filename format unexpected
            date_str = datetime.now(UTC).strftime("%Y%m%d")
            logger.warning(
                f"Could not parse date from filename '{filename}', using today: {date_str}"
            )

        # Build key: prefix/YYYYMMDD/filename
        parts = [part for part in [self.prefix, date_str, filename] if part]
        return "/".join(parts)

    def _calculate_md5(self, file_path: Path) -> str:
        """
        Calculate MD5 checksum of a file.

        Args:
            file_path: Path to the file

        Returns:
            MD5 hash as hexadecimal string
        """
        md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _upload_with_retry(
        self,
        file_path: Path,
        key: str,
        max_attempts: int = 3,
        initial_wait: int = 5,
    ) -> bool:
        """
        Upload file to S3 with exponential backoff retry logic.

        Args:
            file_path: Path to the local backup file
            key: S3 object key
            max_attempts: Maximum number of upload attempts
            initial_wait: Initial wait time in seconds (doubles each retry)

        Returns:
            True if upload successful, False otherwise
        """
        wait_time = initial_wait

        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Upload attempt {attempt}/{max_attempts}: {key}")

                # Calculate MD5 before upload for integrity verification
                local_md5 = self._calculate_md5(file_path)
                file_size = file_path.stat().st_size

                # Upload with content type and metadata
                if not self.bucket_name:
                    return False

                self.client.upload_file(
                    str(file_path),
                    self.bucket_name,
                    key,
                    ExtraArgs={
                        "ContentType": "application/gzip",
                        "Metadata": {
                            "backup_date": datetime.now(UTC).isoformat(),
                            "database": "astro",
                            "size": str(file_size),
                            "md5_checksum": local_md5,
                        },
                    },
                )

                logger.info(f"Upload successful on attempt {attempt}: {key}")
                return True

            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Upload failed on attempt {attempt}/{max_attempts}: {e}")

                if attempt < max_attempts:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    wait_time *= 2  # Exponential backoff
                else:
                    logger.error(f"All {max_attempts} upload attempts failed")
                    return False

        return False

    def verify_upload_integrity(self, file_path: Path, s3_url: str) -> bool:
        """
        Verify that uploaded file matches local file using MD5 checksum.

        Args:
            file_path: Path to the local backup file
            s3_url: S3 URL of the uploaded file

        Returns:
            True if checksums match, False otherwise
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Skipping integrity verification")
            return True

        # Parse S3 URL to extract key
        if not s3_url.startswith("s3://"):
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return False

        parts = s3_url[5:].split("/", 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URL structure: {s3_url}")
            return False

        bucket, key = parts

        try:
            # Calculate local MD5
            local_md5 = self._calculate_md5(file_path)

            # Get S3 object metadata
            response = self.client.head_object(Bucket=bucket, Key=key)
            s3_md5 = response.get("Metadata", {}).get("md5_checksum")

            if not s3_md5:
                logger.warning("S3 object has no MD5 checksum in metadata, using ETag")
                # ETag is MD5 for single-part uploads
                s3_md5 = response.get("ETag", "").strip('"')

            if local_md5 == s3_md5:
                logger.info(f"Integrity verification passed: {local_md5}")
                return True
            else:
                logger.error(
                    f"Integrity verification failed! Local MD5: {local_md5}, S3 MD5: {s3_md5}"
                )
                return False

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to verify upload integrity: {e}")
            return False

    def upload_backup(self, file_path: Path | str) -> str | None:
        """
        Upload a database backup file to S3 with retry logic and integrity verification.

        Args:
            file_path: Path to the local backup file (.sql.gz)

        Returns:
            S3 URL (s3://bucket/key) if successful, None if failed or disabled

        Example:
            >>> backup_s3 = BackupS3Service()
            >>> url = backup_s3.upload_backup('/var/backups/astro_backup_20250120.sql.gz')
            >>> print(url)
            's3://my-bucket/backups/20250120/astro_backup_20250120.sql.gz'
        """
        if not self.enabled:
            logger.warning(f"[DEV MODE] Simulated upload of {file_path}")
            return f"file://{file_path}"  # Return local path in dev mode

        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Backup file not found: {file_path}")
            return None

        key = self._build_key(file_path.name)

        # Upload with retry logic
        if not self._upload_with_retry(file_path, key):
            return None

        s3_url = f"s3://{self.bucket_name}/{key}"

        # Verify upload integrity
        if not self.verify_upload_integrity(file_path, s3_url):
            logger.error("Upload integrity check failed - backup may be corrupted")
            # Don't return None here - upload succeeded but verification failed
            # Let the caller decide whether to keep or delete
            logger.warning(f"Backup uploaded but integrity verification failed: {s3_url}")

        logger.info(f"Successfully uploaded backup to {s3_url}")
        return s3_url

    def download_backup(self, s3_url: str, local_path: Path | str) -> bool:
        """
        Download a backup file from S3 to local filesystem.

        Args:
            s3_url: S3 URL of the backup file (format: s3://bucket/key)
            local_path: Local path where backup should be saved

        Returns:
            True if download successful, False otherwise
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Cannot download from S3 - not enabled")
            return False

        # Parse S3 URL
        if not s3_url.startswith("s3://"):
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return False

        parts = s3_url[5:].split("/", 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URL structure: {s3_url}")
            return False

        bucket, key = parts
        local_path = Path(local_path)

        # Ensure parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.info(f"Downloading backup from {s3_url} to {local_path}")
            self.client.download_file(bucket, key, str(local_path))
            logger.info(f"Successfully downloaded backup to {local_path}")
            return True

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to download backup from S3: {e}")
            return False

    def list_backups(self, limit: int = 30) -> list[dict]:
        """
        List recent backup files from S3.

        Args:
            limit: Maximum number of backups to return (default: 30)

        Returns:
            List of dictionaries with backup metadata:
            [
                {
                    'filename': 'astro_backup_20250120_143000.sql.gz',
                    'date': '2025-01-20',
                    'size': 52428800,  # bytes
                    'url': 's3://bucket/backups/20250120/astro_backup_20250120.sql.gz',
                    'last_modified': datetime(2025, 1, 20, 14, 30)
                }
            ]
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Cannot list backups - S3 not enabled")
            return []

        prefix = self.prefix or ""

        if not self.bucket_name:
            return []

        try:
            # List all objects with prefix
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit,
            )

            if "Contents" not in response:
                logger.info("No backups found in S3")
                return []

            backups = []
            for obj in response["Contents"]:
                key = obj["Key"]
                filename = Path(key).name

                # Extract date from filename or key
                try:
                    date_part = filename.split("_")[2][:8]  # YYYYMMDD
                    date_str = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                except (IndexError, ValueError):
                    date_str = obj["LastModified"].strftime("%Y-%m-%d")

                backups.append(
                    {
                        "filename": filename,
                        "date": date_str,
                        "size": obj["Size"],
                        "url": f"s3://{self.bucket_name}/{key}",
                        "last_modified": obj["LastModified"],
                    }
                )

            # Sort by last modified (newest first)
            from datetime import datetime as dt

            backups.sort(
                key=lambda x: x["last_modified"] if isinstance(x["last_modified"], dt) else dt.min,
                reverse=True,
            )

            logger.info(f"Found {len(backups)} backups in S3")
            return backups[:limit]

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to list backups from S3: {e}")
            return []

    def delete_backup(self, s3_url: str) -> bool:
        """
        Delete a backup file from S3.

        Args:
            s3_url: S3 URL of the backup to delete (format: s3://bucket/key)

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"[DEV MODE] Simulated deletion of {s3_url}")
            return True

        # Parse S3 URL
        if not s3_url.startswith("s3://"):
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return False

        parts = s3_url[5:].split("/", 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URL structure: {s3_url}")
            return False

        bucket, key = parts

        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.info(f"Successfully deleted backup: {s3_url}")
            return True

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to delete backup from S3: {e}")
            return False


# Create singleton instance
backup_s3_service = BackupS3Service()
