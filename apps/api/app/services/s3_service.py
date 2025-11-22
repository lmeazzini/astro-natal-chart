"""
AWS S3 service for storing and retrieving birth chart PDF reports.

This service provides secure, persistent storage for generated PDF files
using Amazon S3, with support for presigned URLs for temporary access.
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from app.core.config import settings


class S3Service:
    """
    Service for managing PDF files in AWS S3.

    Provides methods for uploading, downloading, deleting, and generating
    temporary access URLs for birth chart PDF reports.

    Attributes:
        bucket_name: Name of the S3 bucket
        prefix: Optional prefix for all S3 keys (e.g., 'birth-charts/')
        region: AWS region for the bucket
        enabled: Whether S3 is configured and enabled
    """

    def __init__(self) -> None:
        """Initialize S3 client with configuration from settings."""
        self.bucket_name = settings.S3_BUCKET_NAME
        self.prefix = settings.S3_PREFIX
        self.region = settings.AWS_REGION
        self.enabled = settings.s3_enabled

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
                    f"S3Service initialized for bucket '{self.bucket_name}' in region '{self.region}'"
                )
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self.enabled = False
        else:
            logger.warning(
                "[DEV MODE] S3Service not configured - uploads will be simulated"
            )

    def _build_key(self, user_id: str, chart_id: str, filename: str) -> str:
        """
        Build S3 object key with standard structure.

        Args:
            user_id: UUID of the chart owner
            chart_id: UUID of the birth chart
            filename: Name of the PDF file

        Returns:
            Full S3 key path (e.g., 'birth-charts/{user_id}/{chart_id}/report.pdf')
        """
        # Remove any path components from filename (security)
        filename = Path(filename).name

        # Build key: prefix/user_id/chart_id/filename
        parts = [part for part in [self.prefix, user_id, chart_id, filename] if part]
        return "/".join(parts)

    def upload_pdf(
        self,
        file_path: Path | str,
        user_id: str,
        chart_id: str,
        filename: str | None = None,
    ) -> str | None:
        """
        Upload a PDF file to S3 from a local file path.

        Args:
            file_path: Path to the local PDF file
            user_id: UUID of the chart owner
            chart_id: UUID of the birth chart
            filename: Optional custom filename (defaults to file_path name)

        Returns:
            S3 URL (s3://bucket/key) if successful, None if failed or disabled

        Example:
            >>> s3 = S3Service()
            >>> url = s3.upload_pdf('/tmp/chart.pdf', user_id='123', chart_id='456')
            >>> print(url)
            's3://my-bucket/birth-charts/123/456/full-report-20250120.pdf'
        """
        if not self.enabled:
            logger.warning(f"[DEV MODE] Simulated upload of {file_path}")
            return f"file://{file_path}"  # Return local path in dev mode

        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        filename = filename or file_path.name
        key = self._build_key(user_id, chart_id, filename)

        try:
            # Upload with content type and metadata
            self.client.upload_file(
                str(file_path),
                self.bucket_name,
                key,
                ExtraArgs={
                    "ContentType": "application/pdf",
                    "Metadata": {
                        "user_id": str(user_id),
                        "chart_id": str(chart_id),
                        "uploaded_at": datetime.now(UTC).isoformat(),
                    },
                },
            )

            s3_url = f"s3://{self.bucket_name}/{key}"
            logger.info(f"Successfully uploaded PDF to {s3_url}")
            return s3_url

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload PDF to S3: {e}")
            return None

    def upload_pdf_from_bytes(
        self,
        pdf_bytes: bytes | BinaryIO,
        user_id: str,
        chart_id: str,
        filename: str,
    ) -> str | None:
        """
        Upload a PDF file to S3 from bytes or file-like object.

        Args:
            pdf_bytes: PDF content as bytes or file-like object
            user_id: UUID of the chart owner
            chart_id: UUID of the birth chart
            filename: Name for the PDF file

        Returns:
            S3 URL (s3://bucket/key) if successful, None if failed or disabled
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Simulated upload from bytes")
            return f"memory://{filename}"  # Return memory indicator in dev mode

        key = self._build_key(user_id, chart_id, filename)

        try:
            # Upload bytes with content type and metadata
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=pdf_bytes,
                ContentType="application/pdf",
                Metadata={
                    "user_id": str(user_id),
                    "chart_id": str(chart_id),
                    "uploaded_at": datetime.now(UTC).isoformat(),
                },
            )

            s3_url = f"s3://{self.bucket_name}/{key}"
            logger.info(f"Successfully uploaded PDF bytes to {s3_url}")
            return s3_url

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload PDF bytes to S3: {e}")
            return None

    def generate_presigned_url(
        self, s3_url: str, expires_in: int | None = None
    ) -> str | None:
        """
        Generate a temporary presigned URL for downloading a PDF.

        Args:
            s3_url: S3 URL (format: s3://bucket/key)
            expires_in: URL expiration time in seconds (default from settings)

        Returns:
            HTTPS presigned URL valid for specified duration, None if failed

        Example:
            >>> s3 = S3Service()
            >>> url = s3.generate_presigned_url('s3://bucket/path/file.pdf', 3600)
            >>> print(url)
            'https://bucket.s3.amazonaws.com/path/file.pdf?...'
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Cannot generate presigned URL - S3 not enabled")
            return None

        # Parse S3 URL to extract key
        if not s3_url.startswith("s3://"):
            logger.error(f"Invalid S3 URL format: {s3_url}")
            return None

        # Extract bucket and key from s3://bucket/key
        parts = s3_url[5:].split("/", 1)
        if len(parts) != 2:
            logger.error(f"Invalid S3 URL structure: {s3_url}")
            return None

        bucket, key = parts
        expires_in = expires_in or settings.S3_PRESIGNED_URL_EXPIRATION

        try:
            presigned_url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expires_in,
            )

            logger.info(
                f"Generated presigned URL for {key} (expires in {expires_in}s)"
            )
            return presigned_url

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def delete_pdf(self, s3_url: str) -> bool:
        """
        Delete a PDF file from S3.

        Args:
            s3_url: S3 URL of the file to delete (format: s3://bucket/key)

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"[DEV MODE] Simulated deletion of {s3_url}")
            return True  # Simulate success in dev mode

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
            logger.info(f"Successfully deleted PDF: {s3_url}")
            return True

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to delete PDF from S3: {e}")
            return False

    def list_pdfs_for_chart(self, user_id: str, chart_id: str) -> list[str]:
        """
        List all PDF files for a specific birth chart.

        Args:
            user_id: UUID of the chart owner
            chart_id: UUID of the birth chart

        Returns:
            List of S3 URLs for all PDFs associated with the chart
        """
        if not self.enabled:
            logger.warning("[DEV MODE] Cannot list PDFs - S3 not enabled")
            return []

        prefix = self._build_key(user_id, chart_id, "")

        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )

            if "Contents" not in response:
                return []

            s3_urls = [
                f"s3://{self.bucket_name}/{obj['Key']}" for obj in response["Contents"]
            ]

            logger.info(f"Found {len(s3_urls)} PDFs for chart {chart_id}")
            return s3_urls

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to list PDFs from S3: {e}")
            return []

    def pdf_exists(self, s3_url: str) -> bool:
        """
        Check if a PDF file exists in S3.

        Args:
            s3_url: S3 URL to check (format: s3://bucket/key)

        Returns:
            True if file exists, False otherwise
        """
        if not self.enabled:
            return False

        # Parse S3 URL
        if not s3_url.startswith("s3://"):
            return False

        parts = s3_url[5:].split("/", 1)
        if len(parts) != 2:
            return False

        bucket, key = parts

        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False

    # ============================================
    # Avatar Upload Methods
    # ============================================

    ALLOWED_IMAGE_TYPES = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }
    MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB

    # Magic bytes (file signatures) for image validation
    IMAGE_MAGIC_BYTES = {
        "image/jpeg": [b"\xff\xd8\xff"],  # JPEG
        "image/png": [b"\x89PNG\r\n\x1a\n"],  # PNG
        "image/webp": [b"RIFF"],  # WebP (followed by size and WEBP)
    }

    def _validate_image_magic_bytes(
        self, image_bytes: bytes, content_type: str
    ) -> bool:
        """
        Validate that the image file's magic bytes match the declared content type.

        This provides additional security by verifying the actual file content
        matches what the client claims it is.

        Args:
            image_bytes: The raw image data
            content_type: The declared MIME type

        Returns:
            True if magic bytes match, False otherwise
        """
        if content_type not in self.IMAGE_MAGIC_BYTES:
            return False

        magic_signatures = self.IMAGE_MAGIC_BYTES[content_type]

        for signature in magic_signatures:
            if image_bytes.startswith(signature):
                # Special check for WebP: must have 'WEBP' at offset 8
                if content_type == "image/webp":
                    return len(image_bytes) > 12 and image_bytes[8:12] == b"WEBP"
                return True

        return False

    def _build_avatar_key(self, user_id: str, filename: str) -> str:
        """
        Build S3 object key for avatar images.

        Args:
            user_id: UUID of the user
            filename: Name of the image file

        Returns:
            Full S3 key path (e.g., 'avatars/{user_id}/{filename}')
        """
        # Remove any path components from filename (security)
        filename = Path(filename).name
        return f"avatars/{user_id}/{filename}"

    def upload_avatar(
        self,
        image_bytes: bytes,
        user_id: str,
        content_type: str,
        filename: str | None = None,
    ) -> str | None:
        """
        Upload an avatar image to S3.

        Args:
            image_bytes: Image content as bytes
            user_id: UUID of the user
            content_type: MIME type of the image (image/jpeg, image/png, image/webp)
            filename: Optional custom filename

        Returns:
            S3 URL (s3://bucket/key) if successful, None if failed or invalid

        Raises:
            ValueError: If content type is not allowed or file is too large
        """
        # Validate content type
        if content_type not in self.ALLOWED_IMAGE_TYPES:
            raise ValueError(
                f"Invalid image type. Allowed: {', '.join(self.ALLOWED_IMAGE_TYPES.keys())}"
            )

        # Validate file size
        if len(image_bytes) > self.MAX_AVATAR_SIZE:
            raise ValueError(
                f"File too large. Maximum size is {self.MAX_AVATAR_SIZE // (1024 * 1024)}MB"
            )

        # Validate magic bytes (file signature) for security
        if not self._validate_image_magic_bytes(image_bytes, content_type):
            logger.warning(
                f"Magic bytes validation failed for content_type={content_type}"
            )
            raise ValueError(
                "File content does not match declared type. Please upload a valid image."
            )

        # Generate filename if not provided
        if not filename:
            ext = self.ALLOWED_IMAGE_TYPES[content_type]
            filename = f"avatar-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}.{ext}"

        if not self.enabled:
            logger.warning("[DEV MODE] Simulated avatar upload")
            return f"memory://avatars/{user_id}/{filename}"

        key = self._build_avatar_key(user_id, filename)

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType=content_type,
                Metadata={
                    "user_id": str(user_id),
                    "uploaded_at": datetime.now(UTC).isoformat(),
                },
            )

            s3_url = f"s3://{self.bucket_name}/{key}"
            logger.info(f"Successfully uploaded avatar to {s3_url}")
            return s3_url

        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload avatar to S3: {e}")
            return None

    def get_avatar_public_url(self, s3_url: str) -> str | None:
        """
        Get a public URL for an avatar image (presigned URL with longer expiration).

        For avatars, we use a longer expiration (24 hours) since they're displayed frequently.

        Args:
            s3_url: S3 URL of the avatar (format: s3://bucket/key)

        Returns:
            HTTPS presigned URL valid for 24 hours, None if failed
        """
        return self.generate_presigned_url(s3_url, expires_in=86400)  # 24 hours

    def delete_avatar(self, s3_url: str) -> bool:
        """
        Delete an avatar image from S3.

        Args:
            s3_url: S3 URL of the avatar to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        return self.delete_pdf(s3_url)  # Same logic as PDF deletion


# Create singleton instance
s3_service = S3Service()
