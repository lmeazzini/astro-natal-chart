"""
Document loader abstraction supporting both local filesystem and S3 storage.

This module provides a unified interface for loading RAG documents from either
local filesystem or AWS S3, depending on the RAG_STORAGE_TYPE configuration.
"""

from pathlib import Path
from typing import Protocol

from loguru import logger

from app.core.config import settings


class DocumentLoader(Protocol):
    """Protocol for document loaders."""

    def list_documents(self, document_type: str | None = None) -> list[str]:
        """
        List all document paths.

        Args:
            document_type: Optional filter by document type subdirectory

        Returns:
            List of relative document paths
        """
        ...

    def load_document(self, relative_path: str, use_cache: bool = True) -> bytes:
        """
        Load a document.

        Args:
            relative_path: Relative path to document
            use_cache: Whether to use local cache (S3 only)

        Returns:
            Document content as bytes
        """
        ...

    def document_exists(self, relative_path: str) -> bool:
        """
        Check if a document exists.

        Args:
            relative_path: Relative path to document

        Returns:
            True if document exists
        """
        ...


class LocalDocumentLoader:
    """Load documents from local filesystem."""

    def __init__(self, base_path: str | None = None):
        """
        Initialize local document loader.

        Args:
            base_path: Base directory for documents (defaults to settings.RAG_LOCAL_PATH)
        """
        self.base_path = Path(base_path or settings.RAG_LOCAL_PATH)
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created local document directory: {self.base_path}")
        else:
            logger.info(f"Local document loader initialized: {self.base_path}")

    def list_documents(self, document_type: str | None = None) -> list[str]:
        """
        List all document paths in the local filesystem.

        Args:
            document_type: Optional filter by document type subdirectory
                          (e.g., "texts", "pdfs", "interpretations")

        Returns:
            List of relative document paths
        """
        search_path = self.base_path
        if document_type:
            search_path = self.base_path / document_type

        if not search_path.exists():
            logger.warning(f"Document path does not exist: {search_path}")
            return []

        # Find all files recursively
        documents = []
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                # Get relative path from base_path
                relative_path = file_path.relative_to(self.base_path)
                documents.append(str(relative_path))

        logger.info(f"Found {len(documents)} documents in {search_path}")
        return sorted(documents)

    def load_document(self, relative_path: str, use_cache: bool = True) -> bytes:
        """
        Load a document from local filesystem.

        Args:
            relative_path: Relative path to document (e.g., "texts/file.txt")
            use_cache: Ignored for local loader (kept for interface compatibility)

        Returns:
            Document content as bytes

        Raises:
            FileNotFoundError: If document not found
        """
        file_path = self.base_path / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        logger.debug(f"Loading document from local filesystem: {relative_path}")
        return file_path.read_bytes()

    def document_exists(self, relative_path: str) -> bool:
        """
        Check if a document exists in local filesystem.

        Args:
            relative_path: Relative path to document

        Returns:
            True if document exists
        """
        file_path = self.base_path / relative_path
        return file_path.exists() and file_path.is_file()


def get_document_loader() -> DocumentLoader:
    """
    Get the configured document loader (local or S3).

    Returns:
        DocumentLoader instance based on RAG_STORAGE_TYPE setting

    Raises:
        ValueError: If storage type is invalid or S3 is not properly configured
    """
    if settings.RAG_STORAGE_TYPE == "local":
        return LocalDocumentLoader()
    elif settings.RAG_STORAGE_TYPE == "s3":
        # Import S3 loader only if needed
        from app.services.rag.s3_document_loader import get_s3_document_loader

        return get_s3_document_loader()
    else:
        raise ValueError(
            f"Invalid RAG_STORAGE_TYPE: {settings.RAG_STORAGE_TYPE}. Must be 'local' or 's3'."
        )
