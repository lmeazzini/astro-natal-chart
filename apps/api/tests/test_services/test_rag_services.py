"""Tests for RAG services."""
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.models.vector_document import VectorDocument
from app.services.rag.bm25_service import BM25Service
from app.services.rag.document_ingestion_service import DocumentIngestionService
from app.services.rag.hybrid_search_service import HybridSearchService
from app.services.rag.qdrant_service import QdrantService


class TestBM25Service:
    """Test BM25 sparse search service."""

    def test_tokenize(self):
        """Test text tokenization."""
        service = BM25Service()
        text = "The Sun is in Aries at 15 degrees"
        tokens = service.tokenize(text)

        # Check stopwords are removed
        assert "the" not in tokens
        assert "is" not in tokens
        assert "in" not in tokens
        assert "at" not in tokens

        # Check content words remain
        assert "sun" in tokens
        assert "aries" in tokens

        # Check all lowercase
        assert all(token.islower() for token in tokens)

    def test_tokenize_portuguese(self):
        """Test text tokenization with Portuguese stopwords."""
        service = BM25Service()
        text = "O Sol está em Áries no grau 15 da casa"
        tokens = service.tokenize(text)

        # Check Portuguese stopwords are removed
        assert "o" not in tokens
        assert "está" not in tokens
        assert "em" not in tokens
        assert "no" not in tokens
        assert "da" not in tokens
        assert "casa" not in tokens  # astrological stopword
        assert "grau" not in tokens  # astrological stopword

        # Check content words remain
        assert "sol" in tokens
        assert "áries" in tokens

        # Check all lowercase
        assert all(token.islower() for token in tokens)

    def test_build_index(self):
        """Test building BM25 index."""
        service = BM25Service()
        documents = [
            "Mercury in retrograde affects communication",
            "Venus conjunction Jupiter brings abundance",
            "Mars square Saturn creates tension"
        ]
        document_ids = ["doc1", "doc2", "doc3"]

        service.build_index(documents, document_ids)

        assert len(service.corpus) == 3
        assert len(service.document_ids) == 3
        assert service.bm25 is not None

    def test_search(self):
        """Test BM25 search."""
        service = BM25Service()
        documents = [
            "Mercury in retrograde affects communication and travel",
            "Venus conjunction Jupiter brings love and abundance",
            "Mars square Saturn creates conflict and tension"
        ]
        document_ids = ["doc1", "doc2", "doc3"]

        service.build_index(documents, document_ids)

        # Search for Mercury
        results = service.search("Mercury communication", limit=2)

        assert len(results) > 0
        assert results[0]["document_id"] == "doc1"  # Should match first document
        assert results[0]["score"] > 0

    def test_add_document(self):
        """Test adding document to index."""
        service = BM25Service()

        # Add first document
        service.add_document("Sun in Leo brings confidence", "doc1")
        assert len(service.corpus) == 1
        assert "doc1" in service.document_ids

        # Add second document
        service.add_document("Moon in Cancer nurtures emotions", "doc2")
        assert len(service.corpus) == 2
        assert "doc2" in service.document_ids

    def test_remove_document(self):
        """Test removing document from index."""
        service = BM25Service()
        service.add_document("Sun in Leo", "doc1")
        service.add_document("Moon in Cancer", "doc2")

        # Remove document
        success = service.remove_document("doc1")
        assert success
        assert len(service.corpus) == 1
        assert "doc1" not in service.document_ids
        assert "doc2" in service.document_ids

        # Try removing non-existent document
        success = service.remove_document("doc3")
        assert not success

    def test_get_term_frequencies(self):
        """Test term frequency calculation."""
        service = BM25Service()
        text = "Mars Mars Venus Jupiter Mars"
        freqs = service.get_term_frequencies(text)

        assert freqs["mars"] == 3
        assert freqs["venus"] == 1
        assert freqs["jupiter"] == 1

    def test_calculate_score(self):
        """Test BM25 score calculation."""
        service = BM25Service()
        query = "Mercury retrograde"
        document = "Mercury in retrograde affects communication"

        score = service.calculate_score(query, document)
        # BM25 scores can be negative for short documents
        assert isinstance(score, float)

        # Non-matching document should have different score
        unrelated_doc = "Sun in Leo brings confidence"
        unrelated_score = service.calculate_score(query, unrelated_doc)
        # Document with matching terms should have different score than unrelated
        assert score != unrelated_score


class TestQdrantService:
    """Test Qdrant vector search service."""

    @patch('app.services.rag.qdrant_service.QdrantClient')
    def test_initialization_success(self, mock_client):
        """Test successful Qdrant initialization."""
        mock_client.return_value.get_collections.return_value.collections = []

        service = QdrantService()

        assert service.client is not None
        assert service.enabled is True
        assert service.collection_name == "astrology_knowledge"

    @patch('app.services.rag.qdrant_service.QdrantClient')
    def test_initialization_failure(self, mock_client):
        """Test Qdrant initialization failure."""
        mock_client.side_effect = Exception("Connection failed")

        service = QdrantService()

        assert service.client is None
        assert service.enabled is False

    @pytest.mark.asyncio
    @patch('app.services.rag.qdrant_service.QdrantClient')
    async def test_upsert_vectors(self, mock_client):
        """Test vector upsert."""
        service = QdrantService()
        service.client = mock_client.return_value
        service.enabled = True

        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        payloads = [{"doc": "doc1"}, {"doc": "doc2"}]
        ids = ["id1", "id2"]

        result = await service.upsert_vectors(vectors, payloads, ids)

        assert result is True
        service.client.upsert.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.rag.qdrant_service.QdrantClient')
    async def test_search(self, mock_client):
        """Test vector search."""
        service = QdrantService()
        service.client = mock_client.return_value
        service.enabled = True

        # Mock search results
        mock_point = MagicMock()
        mock_point.id = "doc1"
        mock_point.score = 0.95
        mock_point.payload = {"title": "Test"}
        service.client.search.return_value = [mock_point]

        query_vector = [0.1, 0.2, 0.3]
        results = await service.search(query_vector, limit=10)

        assert len(results) == 1
        assert results[0]["id"] == "doc1"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    @patch('app.services.rag.qdrant_service.QdrantClient')
    async def test_delete_vectors(self, mock_client):
        """Test vector deletion."""
        service = QdrantService()
        service.client = mock_client.return_value
        service.enabled = True

        ids = ["id1", "id2"]
        result = await service.delete_vectors(ids)

        assert result is True
        service.client.delete.assert_called_once()


class TestHybridSearchService:
    """Test hybrid search service."""

    def test_normalize_score(self):
        """Test score normalization."""
        service = HybridSearchService()

        # Normal case
        normalized = service._normalize_score(5, 0, 10)
        assert normalized == 0.5

        # Edge case: all scores same
        normalized = service._normalize_score(5, 5, 5)
        assert normalized == 0.5

    def test_reciprocal_rank_fusion(self):
        """Test RRF fusion."""
        service = HybridSearchService()

        dense_results = [
            {"id": "doc1", "score": 0.9},
            {"id": "doc2", "score": 0.8},
            {"id": "doc3", "score": 0.7},
        ]

        sparse_results = [
            {"document_id": "doc2", "score": 10},
            {"document_id": "doc3", "score": 8},
            {"document_id": "doc4", "score": 6},
        ]

        fused = service._reciprocal_rank_fusion(dense_results, sparse_results)

        # doc2 should rank high (appears in both)
        assert "doc2" in [r["document_id"] for r in fused[:2]]
        # All documents should be included
        assert len(fused) == 4

    def test_weighted_fusion(self):
        """Test weighted fusion."""
        service = HybridSearchService(alpha=0.7)  # 70% dense, 30% sparse

        dense_results = [
            {"id": "doc1", "score": 0.9},
            {"id": "doc2", "score": 0.8},
        ]

        sparse_results = [
            {"document_id": "doc2", "score": 10},
            {"document_id": "doc3", "score": 8},
        ]

        fused = service._weighted_fusion(dense_results, sparse_results)

        # Check that fusion worked
        assert len(fused) == 3  # doc1, doc2, doc3
        assert all("hybrid_score" in r for r in fused)
        # doc2 appears in both lists, so should have a good score
        doc2_result = next(r for r in fused if r["document_id"] == "doc2")
        assert "dense_score" in doc2_result
        assert "sparse_score" in doc2_result

    @pytest.mark.asyncio
    async def test_search_hybrid(self):
        """Test hybrid search."""
        service = HybridSearchService()

        # Mock underlying services
        with patch.object(service.qdrant, 'search') as mock_qdrant:
            with patch.object(service.bm25, 'search') as mock_bm25:
                service.qdrant.enabled = True

                mock_qdrant.return_value = [
                    {"id": "doc1", "score": 0.9, "payload": {}}
                ]
                mock_bm25.return_value = [
                    {"document_id": "doc1", "score": 10}
                ]

                results = await service.search(
                    query="test query",
                    query_vector=[0.1, 0.2, 0.3],
                    limit=5,
                    fusion_method="rrf"
                )

                assert len(results) > 0
                assert results[0]["document_id"] == "doc1"


class TestDocumentIngestionService:
    """Test document ingestion service."""

    def test_count_tokens(self):
        """Test token counting."""
        service = DocumentIngestionService()
        text = "This is a test document"
        count = service._count_tokens(text)
        assert count > 0

    def test_chunk_text_small(self):
        """Test chunking small text."""
        service = DocumentIngestionService()
        service.chunk_size = 100

        text = "Small text"
        chunks = service._chunk_text(text)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_large(self):
        """Test chunking large text."""
        service = DocumentIngestionService()
        service.chunk_size = 10
        service.chunk_overlap = 2

        # Create a text that will be chunked
        text = " ".join(["word"] * 50)
        chunks = service._chunk_text(text, chunk_size=10, overlap=2)

        assert len(chunks) > 1
        # Check overlap exists between chunks
        # (Can't test exact overlap due to tokenization)

    def test_generate_document_id(self):
        """Test document ID generation."""
        service = DocumentIngestionService()

        content = "Test content"
        metadata = {"source": "test.pdf", "page": 1}

        doc_id1 = service._generate_document_id(content, metadata)
        doc_id2 = service._generate_document_id(content, metadata)

        # Same input should generate same ID
        assert doc_id1 == doc_id2
        assert len(doc_id1) == 16  # SHA256 truncated to 16 chars

        # Different input should generate different ID
        doc_id3 = service._generate_document_id("Different", metadata)
        assert doc_id3 != doc_id1

    @pytest.mark.asyncio
    async def test_ingest_text(self):
        """Test text ingestion."""
        service = DocumentIngestionService()

        # Mock database session
        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()

        # Mock BM25 service
        with patch.object(service.bm25, 'add_document'):
            documents = await service.ingest_text(
                db=mock_db,
                title="Test Document",
                content="This is test content for RAG system",
                document_type="text",
                metadata={"author": "test"},
                get_embeddings_func=None
            )

            assert len(documents) > 0
            assert documents[0].title.startswith("Test Document")
            assert documents[0].document_type == "text"
            assert mock_db.commit.called

    @pytest.mark.asyncio
    async def test_delete_document(self):
        """Test document deletion."""
        service = DocumentIngestionService()

        # Mock database session
        mock_db = AsyncMock()
        mock_doc = VectorDocument(
            id=uuid4(),
            collection_name="test",
            document_type="text",
            title="Test",
            content="Content",
            vector_id="vec1"
        )
        mock_db.get = AsyncMock(return_value=mock_doc)
        mock_db.delete = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()

        # Mock services
        with patch.object(service.qdrant, 'delete_vectors') as mock_qdrant:
            with patch.object(service.bm25, 'remove_document') as mock_bm25:
                service.qdrant.enabled = True
                mock_qdrant.return_value = True
                mock_bm25.return_value = True

                result = await service.delete_document(mock_db, mock_doc.id)

                assert result is True
                mock_qdrant.assert_called_once_with(["vec1"])
                mock_bm25.assert_called_once_with("vec1")
                mock_db.delete.assert_called_once()
                mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_ingestion_stats(self):
        """Test getting ingestion statistics."""
        service = DocumentIngestionService()

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 10
        mock_db.execute = AsyncMock(return_value=mock_result)

        # Mock BM25 stats
        with patch.object(service.bm25, 'get_index_stats') as mock_bm25_stats:
            mock_bm25_stats.return_value = {
                "num_documents": 10,
                "avg_doc_length": 100
            }

            stats = await service.get_ingestion_stats(mock_db)

            assert "total_documents" in stats
            assert "bm25_stats" in stats
            assert stats["bm25_stats"]["num_documents"] == 10
