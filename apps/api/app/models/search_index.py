"""Search index model for BM25 sparse search."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SearchIndex(Base):
    """Store BM25 index data for sparse keyword search."""

    __tablename__ = "search_indices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Index identification
    index_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    index_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="bm25"
    )  # Future: 'tf-idf', 'bm25plus'

    # Tokenized content for BM25
    document_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), nullable=False, index=True
    )  # References vector_documents.id
    tokens: Mapped[str] = mapped_column(Text, nullable=False)  # Space-separated tokens
    token_frequencies: Mapped[dict[str, int]] = mapped_column(
        JSON, default=dict
    )  # {"token": frequency}

    # BM25 parameters (can be tuned per index)
    k1: Mapped[float] = mapped_column(default=1.2)  # Term frequency saturation
    b: Mapped[float] = mapped_column(default=0.75)  # Length normalization

    # Statistics
    doc_length: Mapped[int] = mapped_column(default=0)  # Number of tokens
    doc_metadata: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # Create indexes and constraints for efficient querying
    __table_args__ = (
        Index("idx_search_indices_document_id", "document_id"),
        Index("idx_search_indices_index_name", "index_name"),
        # Prevent duplicate entries for the same document in the same index
        UniqueConstraint("index_name", "document_id", name="uq_search_indices_index_document"),
    )

    def __repr__(self) -> str:
        """String representation of the search index."""
        return (
            f"<SearchIndex(id={self.id}, index_name='{self.index_name}', "
            f"doc_id={self.document_id}, tokens={self.doc_length})>"
        )
