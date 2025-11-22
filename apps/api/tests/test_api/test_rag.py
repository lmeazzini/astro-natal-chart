"""Tests for RAG API endpoints."""
import json
from uuid import uuid4
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.vector_document import VectorDocument


@pytest.fixture
async def mock_rag_services():
    """Mock RAG services."""
    with patch('app.api.v1.endpoints.rag.hybrid_search_service') as mock_hybrid:
        with patch('app.api.v1.endpoints.rag.document_ingestion_service') as mock_ingestion:
            yield mock_hybrid, mock_ingestion


class TestRAGSearch:
    """Test RAG search endpoints."""

    @pytest.mark.asyncio
    async def test_search_documents_success(
        self,
        client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
        mock_rag_services,
    ):
        """Test successful document search."""
        mock_hybrid, _ = mock_rag_services

        # Mock search results
        mock_hybrid.search = AsyncMock(return_value=[
            {
                "document_id": str(uuid4()),
                "hybrid_score": 0.95,
                "dense_score": 0.9,
                "sparse_score": 8.5,
            }
        ])

        # Create test document in database
        test_doc = VectorDocument(
            collection_name="test",
            document_type="text",
            title="Test Document",
            content="This is test content about astrology and planets",
            doc_metadata={"author": "test"},
        )
        db_session.add(test_doc)
        await db_session.commit()

        # Update mock to return correct document ID
        mock_hybrid.search.return_value[0]["document_id"] = str(test_doc.id)

        # Perform search
        response = await client.post(
            "/api/v1/rag/search",
            json={
                "query": "astrology planets",
                "limit": 10,
                "fusion_method": "rrf",
            },
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "astrology planets"
        assert data["fusion_method"] == "rrf"
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Test Document"
        assert "astrology" in data["results"][0]["content_preview"]

    @pytest.mark.asyncio
    async def test_search_documents_no_results(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test search with no results."""
        mock_hybrid, _ = mock_rag_services
        mock_hybrid.search = AsyncMock(return_value=[])

        response = await client.post(
            "/api/v1/rag/search",
            json={
                "query": "nonexistent query",
                "limit": 10,
                "fusion_method": "weighted",
            },
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["query"] == "nonexistent query"
        assert len(data["results"]) == 0
        assert data["total_results"] == 0

    @pytest.mark.asyncio
    async def test_search_documents_unauthorized(
        self,
        client: AsyncClient,
    ):
        """Test search without authentication."""
        response = await client.post(
            "/api/v1/rag/search",
            json={
                "query": "test",
                "limit": 10,
            },
        )

        assert response.status_code == 401


class TestRAGIngestion:
    """Test RAG document ingestion endpoints."""

    @pytest.mark.asyncio
    async def test_ingest_text_document_success(
        self,
        client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
        mock_rag_services,
    ):
        """Test successful text document ingestion."""
        _, mock_ingestion = mock_rag_services

        # Mock ingestion result
        test_doc_id = uuid4()
        mock_doc = VectorDocument(
            id=test_doc_id,
            collection_name="astrology_knowledge",
            document_type="text",
            title="Test Astrology",
            content="Content about planets",
        )
        mock_ingestion.ingest_text = AsyncMock(return_value=[mock_doc])

        response = await client.post(
            "/api/v1/rag/ingest/text",
            json={
                "title": "Test Astrology",
                "content": "Content about planets and houses in astrology",
                "document_type": "text",
                "metadata": {"author": "test_user"},
            },
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "Successfully ingested" in data["message"]
        assert data["documents_created"] == 1
        assert len(data["document_ids"]) == 1
        assert data["document_ids"][0] == str(test_doc_id)

    @pytest.mark.asyncio
    async def test_ingest_text_document_failure(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test text ingestion failure."""
        _, mock_ingestion = mock_rag_services
        mock_ingestion.ingest_text = AsyncMock(side_effect=Exception("Ingestion failed"))

        response = await client.post(
            "/api/v1/rag/ingest/text",
            json={
                "title": "Test",
                "content": "Content",
                "document_type": "text",
            },
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 500
        assert "Document ingestion failed" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_ingest_pdf_document_success(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test successful PDF document ingestion."""
        _, mock_ingestion = mock_rag_services

        # Mock ingestion result
        test_doc_ids = [uuid4(), uuid4()]
        mock_docs = [
            VectorDocument(
                id=doc_id,
                collection_name="astrology_knowledge",
                document_type="pdf",
                title=f"Page {i}",
                content="Content",
            )
            for i, doc_id in enumerate(test_doc_ids, 1)
        ]
        mock_ingestion.ingest_pdf = AsyncMock(return_value=mock_docs)

        # Create test PDF content
        pdf_content = b"%PDF-1.4\n%Test PDF content"

        response = await client.post(
            "/api/v1/rag/ingest/pdf",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
            data={"metadata": json.dumps({"source": "test"})},
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "Successfully ingested PDF" in data["message"]
        assert data["documents_created"] == 2
        assert len(data["document_ids"]) == 2


class TestRAGDocumentManagement:
    """Test RAG document management endpoints."""

    @pytest.mark.asyncio
    async def test_get_document_success(
        self,
        client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
    ):
        """Test getting document details."""
        # Create test document
        test_doc = VectorDocument(
            collection_name="test",
            document_type="text",
            title="Test Document",
            content="Full content of the document",
            doc_metadata={"author": "test"},
        )
        db_session.add(test_doc)
        await db_session.commit()

        response = await client.get(
            f"/api/v1/rag/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(test_doc.id)
        assert data["title"] == "Test Document"
        assert data["content"] == "Full content of the document"
        assert data["document_type"] == "text"
        assert data["metadata"]["author"] == "test"

    @pytest.mark.asyncio
    async def test_get_document_not_found(
        self,
        client: AsyncClient,
        test_user: User,
    ):
        """Test getting non-existent document."""
        fake_id = uuid4()

        response = await client.get(
            f"/api/v1/rag/documents/{fake_id}",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 404
        assert "Document not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_document_success(
        self,
        client: AsyncClient,
        test_user: User,
        db_session: AsyncSession,
        mock_rag_services,
    ):
        """Test successful document deletion."""
        _, mock_ingestion = mock_rag_services

        # Create test document
        test_doc = VectorDocument(
            collection_name="test",
            document_type="text",
            title="To Delete",
            content="Content",
        )
        db_session.add(test_doc)
        await db_session.commit()

        # Mock deletion
        mock_ingestion.delete_document = AsyncMock(return_value=True)

        response = await client.delete(
            f"/api/v1/rag/documents/{test_doc.id}",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

    @pytest.mark.asyncio
    async def test_delete_document_not_found(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test deleting non-existent document."""
        _, mock_ingestion = mock_rag_services
        mock_ingestion.delete_document = AsyncMock(return_value=False)

        fake_id = uuid4()

        response = await client.delete(
            f"/api/v1/rag/documents/{fake_id}",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 404
        assert "Document not found" in response.json()["detail"]


class TestRAGStatistics:
    """Test RAG statistics endpoints."""

    @pytest.mark.asyncio
    async def test_get_rag_stats_success(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test getting RAG statistics."""
        _, mock_ingestion = mock_rag_services

        # Mock statistics
        mock_ingestion.get_ingestion_stats = AsyncMock(return_value={
            "total_documents": 100,
            "indexed_documents": 95,
            "documents_by_type": {
                "text": 50,
                "pdf": 40,
                "interpretation": 10,
            },
            "bm25_stats": {
                "num_documents": 100,
                "avg_doc_length": 250,
                "total_terms": 25000,
                "unique_terms": 3000,
            },
            "qdrant_stats": {
                "vectors_count": 95,
                "points_count": 95,
                "segments_count": 1,
                "status": "green",
            },
        })

        response = await client.get(
            "/api/v1/rag/stats",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_documents"] == 100
        assert data["indexed_documents"] == 95
        assert data["documents_by_type"]["text"] == 50
        assert data["bm25_stats"]["num_documents"] == 100
        assert data["qdrant_stats"]["vectors_count"] == 95

    @pytest.mark.asyncio
    async def test_get_rag_stats_error(
        self,
        client: AsyncClient,
        test_user: User,
        mock_rag_services,
    ):
        """Test getting RAG statistics with error."""
        _, mock_ingestion = mock_rag_services
        mock_ingestion.get_ingestion_stats = AsyncMock(
            side_effect=Exception("Stats error")
        )

        response = await client.get(
            "/api/v1/rag/stats",
            headers={"Authorization": f"Bearer {test_user.id}"},
        )

        assert response.status_code == 500
        assert "Failed to get statistics" in response.json()["detail"]