"""
S3 Document Loader for RAG system.

This service loads RAG documents from AWS S3, with optional local caching
to reduce S3 API calls and improve performance.
"""

from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from loguru import logger

from app.core.config import settings


class S3DocumentLoader:
    """Load RAG documents from S3 bucket with optional caching."""

    def __init__(
        self,
        bucket: str | None = None,
        prefix: str | None = None,
        cache_dir: str | None = None,
        cache_ttl: int | None = None,
    ):
        """
        Initialize S3 document loader.

        Args:
            bucket: S3 bucket name (defaults to settings.RAG_S3_BUCKET)
            prefix: S3 key prefix (defaults to settings.RAG_S3_PREFIX)
            cache_dir: Local cache directory (defaults to settings.RAG_CACHE_DIR)
            cache_ttl: Cache TTL in seconds (defaults to settings.RAG_CACHE_TTL)
        """
        bucket_name = bucket or settings.RAG_S3_BUCKET
        if not bucket_name:
            raise ValueError("S3 bucket name is required")

        self.bucket: str = bucket_name
        self.prefix = prefix or settings.RAG_S3_PREFIX
        self.cache_dir = cache_dir or settings.RAG_CACHE_DIR
        self.cache_ttl = cache_ttl or settings.RAG_CACHE_TTL

        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            # Test connection
            self.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"S3 document loader initialized: s3://{self.bucket}/{self.prefix}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except ClientError as e:
            logger.error(f"Failed to connect to S3 bucket {self.bucket}: {e}")
            raise

        # Create cache directory if enabled
        if self.cache_dir:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Document cache directory: {self.cache_dir}")

    def _get_s3_key(self, relative_path: str) -> str:
        """
        Get full S3 key from relative path.

        Args:
            relative_path: Relative path (e.g., "texts/traditional-astrology.txt")

        Returns:
            Full S3 key (e.g., "rag-documents/texts/traditional-astrology.txt")
        """
        # Remove leading slash if present
        relative_path = relative_path.lstrip("/")
        return f"{self.prefix}/{relative_path}" if self.prefix else relative_path

    def _get_cache_path(self, s3_key: str) -> Path | None:
        """
        Get local cache path for S3 key.

        Args:
            s3_key: S3 object key

        Returns:
            Cache file path, or None if caching is disabled
        """
        if not self.cache_dir:
            return None

        # Use S3 key as cache path (preserving directory structure)
        cache_path = Path(self.cache_dir) / s3_key
        return cache_path

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """
        Check if cached file is still valid.

        Args:
            cache_path: Path to cached file

        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False

        # Check cache age
        import time
        cache_age = time.time() - cache_path.stat().st_mtime
        return cache_age < self.cache_ttl

    def list_documents(
        self,
        document_type: str | None = None,
    ) -> list[str]:
        """
        List all document keys in the bucket.

        Args:
            document_type: Optional filter by document type subdirectory
                          (e.g., "texts", "pdfs", "interpretations")

        Returns:
            List of relative document paths

        Example:
            >>> loader.list_documents(document_type="texts")
            ['texts/traditional-astrology.txt', 'texts/references/book1.txt']
        """
        try:
            # Build prefix
            list_prefix = self.prefix
            if document_type:
                list_prefix = f"{self.prefix}/{document_type}" if self.prefix else document_type

            # List objects
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket, Prefix=list_prefix)

            documents = []
            for page in pages:
                if "Contents" not in page:
                    continue

                for obj in page["Contents"]:
                    key = obj["Key"]
                    # Skip directories (keys ending with /)
                    if key.endswith("/"):
                        continue

                    # Convert to relative path (remove prefix)
                    if self.prefix and key.startswith(f"{self.prefix}/"):
                        relative_path = key[len(self.prefix) + 1 :]
                    else:
                        relative_path = key

                    documents.append(relative_path)

            logger.info(f"Found {len(documents)} documents in s3://{self.bucket}/{list_prefix}")
            return documents

        except ClientError as e:
            logger.error(f"Failed to list documents from S3: {e}")
            raise

    def load_document(
        self,
        relative_path: str,
        use_cache: bool = True,
    ) -> bytes:
        """
        Load a document from S3 (with optional caching).

        Args:
            relative_path: Relative path to document (e.g., "texts/file.txt")
            use_cache: Whether to use local cache

        Returns:
            Document content as bytes

        Raises:
            ClientError: If document not found or S3 error occurs

        Example:
            >>> content = loader.load_document("texts/traditional-astrology.txt")
            >>> text = content.decode("utf-8")
        """
        s3_key = self._get_s3_key(relative_path)

        # Check cache first
        if use_cache and self.cache_dir:
            cache_path = self._get_cache_path(s3_key)
            if cache_path and self._is_cache_valid(cache_path):
                logger.debug(f"Loading document from cache: {relative_path}")
                return cache_path.read_bytes()

        # Load from S3
        try:
            logger.debug(f"Loading document from S3: s3://{self.bucket}/{s3_key}")
            response = self.s3_client.get_object(Bucket=self.bucket, Key=s3_key)
            content = response["Body"].read()

            # Cache the document
            if use_cache and self.cache_dir and cache_path:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_bytes(content)
                logger.debug(f"Cached document: {cache_path}")

            return content

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                logger.error(f"Document not found: s3://{self.bucket}/{s3_key}")
            else:
                logger.error(f"Failed to load document from S3: {e}")
            raise

    def document_exists(self, relative_path: str) -> bool:
        """
        Check if a document exists in S3.

        Args:
            relative_path: Relative path to document

        Returns:
            True if document exists, False otherwise
        """
        s3_key = self._get_s3_key(relative_path)
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError:
            return False

    def upload_document(
        self,
        relative_path: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """
        Upload a document to S3.

        Args:
            relative_path: Relative path where document should be stored
            content: Document content (bytes or file-like object)
            content_type: Optional MIME type

        Returns:
            S3 key of uploaded document

        Example:
            >>> with open("local_doc.txt", "rb") as f:
            ...     loader.upload_document("texts/doc.txt", f, "text/plain")
        """
        s3_key = self._get_s3_key(relative_path)

        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            # Handle both bytes and file-like objects
            if isinstance(content, bytes):
                self.s3_client.put_object(
                    Bucket=self.bucket,
                    Key=s3_key,
                    Body=content,
                    **extra_args,  # type: ignore[arg-type]
                )
            else:
                self.s3_client.upload_fileobj(
                    content,
                    self.bucket,
                    s3_key,
                    ExtraArgs=extra_args,
                )

            logger.info(f"Uploaded document to s3://{self.bucket}/{s3_key}")
            return s3_key

        except ClientError as e:
            logger.error(f"Failed to upload document to S3: {e}")
            raise

    def delete_document(self, relative_path: str) -> bool:
        """
        Delete a document from S3.

        Args:
            relative_path: Relative path to document

        Returns:
            True if deleted, False if not found
        """
        s3_key = self._get_s3_key(relative_path)

        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            logger.info(f"Deleted document: s3://{self.bucket}/{s3_key}")

            # Also delete from cache if exists
            if self.cache_dir:
                cache_path = self._get_cache_path(s3_key)
                if cache_path and cache_path.exists():
                    cache_path.unlink()
                    logger.debug(f"Deleted cached document: {cache_path}")

            return True

        except ClientError as e:
            logger.error(f"Failed to delete document from S3: {e}")
            return False

    def clear_cache(self) -> int:
        """
        Clear the local document cache.

        Returns:
            Number of files deleted
        """
        if not self.cache_dir:
            return 0

        cache_path = Path(self.cache_dir)
        if not cache_path.exists():
            return 0

        count = 0
        for file_path in cache_path.rglob("*"):
            if file_path.is_file():
                file_path.unlink()
                count += 1

        logger.info(f"Cleared {count} cached documents")
        return count


# Singleton instance
_s3_loader: S3DocumentLoader | None = None


def get_s3_document_loader() -> S3DocumentLoader:
    """
    Get singleton S3 document loader instance.

    Returns:
        S3DocumentLoader instance

    Raises:
        ValueError: If S3 storage is not configured
    """
    global _s3_loader

    if not settings.rag_s3_enabled:
        raise ValueError(
            "S3 document storage is not enabled. "
            "Set RAG_STORAGE_TYPE=s3 and configure AWS credentials."
        )

    if _s3_loader is None:
        _s3_loader = S3DocumentLoader()

    return _s3_loader
