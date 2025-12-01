"""Tests for RAG document loader abstraction."""

import tempfile
from pathlib import Path

import pytest

from app.services.rag.document_loader import LocalDocumentLoader, get_document_loader


class TestLocalDocumentLoader:
    """Tests for LocalDocumentLoader."""

    def test_init_creates_directory(self):
        """Test that initialization creates the directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "test_docs"
            assert not base_path.exists()

            loader = LocalDocumentLoader(str(base_path))
            assert base_path.exists()
            assert loader.base_path == base_path

    def test_list_documents_empty(self):
        """Test listing documents in empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = LocalDocumentLoader(tmpdir)
            documents = loader.list_documents()
            assert documents == []

    def test_list_documents_with_files(self):
        """Test listing documents with files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            base_path = Path(tmpdir)
            (base_path / "file1.txt").write_text("content1")
            (base_path / "subdir").mkdir()
            (base_path / "subdir" / "file2.txt").write_text("content2")

            loader = LocalDocumentLoader(tmpdir)
            documents = loader.list_documents()

            assert len(documents) == 2
            assert "file1.txt" in documents
            assert "subdir/file2.txt" in documents or "subdir\\file2.txt" in documents

    def test_list_documents_with_type_filter(self):
        """Test listing documents with type filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            base_path = Path(tmpdir)
            (base_path / "texts").mkdir()
            (base_path / "texts" / "file1.txt").write_text("content1")
            (base_path / "pdfs").mkdir()
            (base_path / "pdfs" / "file2.pdf").write_bytes(b"pdf content")

            loader = LocalDocumentLoader(tmpdir)
            documents = loader.list_documents(document_type="texts")

            assert len(documents) == 1
            assert documents[0].endswith("file1.txt")

    def test_load_document_success(self):
        """Test loading a document successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            base_path = Path(tmpdir)
            test_content = b"test content"
            (base_path / "test.txt").write_bytes(test_content)

            loader = LocalDocumentLoader(tmpdir)
            content = loader.load_document("test.txt")

            assert content == test_content

    def test_load_document_not_found(self):
        """Test loading a non-existent document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = LocalDocumentLoader(tmpdir)

            with pytest.raises(FileNotFoundError):
                loader.load_document("nonexistent.txt")

    def test_document_exists_true(self):
        """Test checking if document exists (true case)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            base_path = Path(tmpdir)
            (base_path / "test.txt").write_text("content")

            loader = LocalDocumentLoader(tmpdir)
            assert loader.document_exists("test.txt") is True

    def test_document_exists_false(self):
        """Test checking if document exists (false case)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = LocalDocumentLoader(tmpdir)
            assert loader.document_exists("nonexistent.txt") is False

    def test_document_exists_directory(self):
        """Test that directories are not considered documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create directory
            base_path = Path(tmpdir)
            (base_path / "subdir").mkdir()

            loader = LocalDocumentLoader(tmpdir)
            assert loader.document_exists("subdir") is False

    def test_load_document_preserves_binary_content(self):
        """Test that binary content is preserved when loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create binary file
            base_path = Path(tmpdir)
            binary_content = bytes(range(256))  # All byte values
            (base_path / "binary.bin").write_bytes(binary_content)

            loader = LocalDocumentLoader(tmpdir)
            loaded_content = loader.load_document("binary.bin")

            assert loaded_content == binary_content
            assert len(loaded_content) == 256


class TestGetDocumentLoader:
    """Tests for get_document_loader factory function."""

    def test_get_local_loader(self, monkeypatch):
        """Test getting local document loader."""
        # Mock settings
        from app.core import config

        monkeypatch.setattr(config.settings, "RAG_STORAGE_TYPE", "local")

        loader = get_document_loader()
        assert isinstance(loader, LocalDocumentLoader)

    def test_get_invalid_storage_type(self, monkeypatch):
        """Test getting loader with invalid storage type."""
        from app.core import config

        monkeypatch.setattr(config.settings, "RAG_STORAGE_TYPE", "invalid")

        with pytest.raises(ValueError, match="Invalid RAG_STORAGE_TYPE"):
            get_document_loader()
