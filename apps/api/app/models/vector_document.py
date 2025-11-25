"""Vector document model for RAG system."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Float, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VectorDocument(Base):
    """Store document metadata for vector search."""

    __tablename__ = "vector_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Document identification
    collection_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'pdf', 'text', 'interpretation', 'concept'

    # Content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(default=0)  # For multi-chunk documents
    total_chunks: Mapped[int] = mapped_column(default=1)

    # Document metadata
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # Example doc_metadata:
    # {
    #   "source": "docs/references/hellenistic-astrology.pdf",
    #   "page": 42,
    #   "tradition": "hellenistic",
    #   "concepts": ["houses", "aspects", "dignities"],
    #   "author": "Chris Brennan",
    #   "year": 2017
    # }

    # Vector information (stored in Qdrant, referenced here)
    vector_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )  # Qdrant point ID
    embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # 'text-embedding-ada-002', 'all-MiniLM-L6-v2'

    # BM25 relevance score (cached for hybrid search)
    bm25_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # When added to Qdrant

    # Create indexes for common queries
    __table_args__ = (
        Index("idx_vector_documents_collection_type", "collection_name", "document_type"),
        Index("idx_vector_documents_vector_id", "vector_id"),
        Index("idx_vector_documents_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of the vector document."""
        return (
            f"<VectorDocument(id={self.id}, title='{self.title[:50]}...', "
            f"type={self.document_type}, collection={self.collection_name})>"
        )
