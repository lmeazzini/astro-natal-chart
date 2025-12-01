"""Document ingestion service for processing and indexing content."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

import tiktoken
from loguru import logger
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.search_index import SearchIndex
from app.models.vector_document import VectorDocument
from app.services.rag.bm25_service import bm25_service
from app.services.rag.qdrant_service import qdrant_service


class DocumentIngestionService:
    """Service for ingesting documents into the RAG system."""

    def __init__(self) -> None:
        """Initialize document ingestion service."""
        self.qdrant = qdrant_service
        self.bm25 = bm25_service
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer

        # Chunking parameters
        self.chunk_size = 500  # tokens
        self.chunk_overlap = 100  # tokens

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.tokenizer.encode(text))

    def _chunk_text(
        self,
        text: str,
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum tokens per chunk
            overlap: Token overlap between chunks

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        overlap = overlap or self.chunk_overlap

        # Tokenize text
        tokens = self.tokenizer.encode(text)

        if len(tokens) <= chunk_size:
            return [text]

        # Create chunks with overlap
        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]

            # Decode chunk back to text
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

            # Move to next chunk with overlap
            start += chunk_size - overlap

            # Stop if we've reached the end
            if end >= len(tokens):
                break

        return chunks

    def _generate_document_id(self, content: str, metadata: dict[str, Any]) -> str:
        """
        Generate unique document ID from content and metadata.

        Args:
            content: Document content
            metadata: Document metadata

        Returns:
            Unique document ID (UUID format for Qdrant compatibility)
        """
        # Create a unique hash from content and key metadata
        hash_input = f"{content[:1000]}{metadata.get('source', '')}{metadata.get('page', '')}"
        # Generate a deterministic UUID from the hash (Qdrant requires UUID or integer)
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()[:16]
        import uuid

        return str(uuid.UUID(bytes=hash_bytes))

    async def ingest_text(
        self,
        db: AsyncSession,
        title: str,
        content: str,
        document_type: str,
        metadata: dict[str, Any] | None = None,
        collection_name: str = "astrology_knowledge",
        get_embeddings_func: Any | None = None,
    ) -> list[VectorDocument]:
        """
        Ingest text document into the RAG system.

        Args:
            db: Database session
            title: Document title
            content: Document content
            document_type: Type of document
            metadata: Optional metadata
            collection_name: Qdrant collection name
            get_embeddings_func: Function to generate embeddings

        Returns:
            List of created VectorDocument objects
        """
        metadata = metadata or {}
        documents = []

        try:
            # Chunk the content
            chunks = self._chunk_text(content)
            logger.info(f"Split document '{title}' into {len(chunks)} chunks")

            # Process each chunk
            for i, chunk in enumerate(chunks):
                # Create VectorDocument
                doc = VectorDocument(
                    collection_name=collection_name,
                    document_type=document_type,
                    title=f"{title} (chunk {i + 1}/{len(chunks)})" if len(chunks) > 1 else title,
                    content=chunk,
                    chunk_index=i,
                    total_chunks=len(chunks),
                    doc_metadata={
                        **metadata,
                        "original_title": title,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "token_count": self._count_tokens(chunk),
                    },
                )

                # Generate unique vector ID
                doc.vector_id = self._generate_document_id(chunk, doc.doc_metadata)

                # Save to database and flush to get the doc.id
                db.add(doc)
                await db.flush()  # Flush to generate doc.id
                documents.append(doc)

                # Add to BM25 index
                self.bm25.add_document(chunk, doc.vector_id)

                # Generate and store embeddings if function provided
                if get_embeddings_func and self.qdrant.enabled:
                    embedding = await get_embeddings_func(chunk)
                    if embedding:
                        success = await self.qdrant.upsert_vectors(
                            vectors=[embedding],
                            payloads=[
                                {
                                    "document_id": str(doc.id),
                                    "title": doc.title,
                                    "document_type": doc.document_type,
                                    "content": chunk[:500],  # Store first 500 chars for preview
                                    "metadata": doc.doc_metadata,
                                }
                            ],
                            ids=[doc.vector_id],
                        )

                        if success:
                            doc.indexed_at = datetime.now(UTC)
                            doc.embedding_model = settings.OPENAI_EMBEDDING_MODEL
                            logger.debug(f"Indexed chunk {i + 1}/{len(chunks)} for '{title}'")
                        else:
                            logger.warning(
                                f"Failed to index chunk {i + 1}/{len(chunks)} for '{title}'"
                            )
                    else:
                        logger.warning(
                            f"No embedding generated for chunk {i + 1}/{len(chunks)} of '{title}'"
                        )

                # Create BM25 index entry
                term_freqs = self.bm25.get_term_frequencies(chunk)
                search_index = SearchIndex(
                    index_name=collection_name,
                    document_id=doc.id,
                    tokens=" ".join(self.bm25.tokenize(chunk)),
                    token_frequencies=term_freqs,
                    doc_length=len(term_freqs),
                )
                db.add(search_index)

            # Commit all documents
            await db.commit()

            logger.info(f"Successfully ingested {len(documents)} chunks for '{title}'")
            return documents

        except Exception as e:
            logger.error(f"Failed to ingest document '{title}': {e}")
            await db.rollback()
            raise

    async def ingest_pdf(
        self,
        db: AsyncSession,
        pdf_path: Path,
        metadata: dict[str, Any] | None = None,
        get_embeddings_func: Any | None = None,
    ) -> list[VectorDocument]:
        """
        Ingest PDF document into the RAG system.

        Args:
            db: Database session
            pdf_path: Path to PDF file
            metadata: Optional metadata
            get_embeddings_func: Function to generate embeddings

        Returns:
            List of created VectorDocument objects
        """
        try:
            # Import PyPDF2 only when needed (no type stubs available)
            import PyPDF2  # type: ignore[import-not-found]

            documents = []
            metadata = metadata or {}

            # Extract text from PDF
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                logger.info(f"Processing PDF '{pdf_path.name}' with {num_pages} pages")

                # Process each page
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()

                    if not page_text.strip():
                        continue

                    # Add page-specific metadata
                    page_metadata = {
                        **metadata,
                        "source": str(pdf_path),
                        "page": page_num + 1,
                        "total_pages": num_pages,
                    }

                    # Ingest page text
                    page_docs = await self.ingest_text(
                        db=db,
                        title=f"{pdf_path.stem} - Page {page_num + 1}",
                        content=page_text,
                        document_type="pdf",
                        metadata=page_metadata,
                        get_embeddings_func=get_embeddings_func,
                    )

                    documents.extend(page_docs)

            logger.info(f"Successfully ingested PDF '{pdf_path.name}' ({len(documents)} chunks)")
            return documents

        except ImportError:
            logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            raise
        except Exception as e:
            logger.error(f"Failed to ingest PDF '{pdf_path}': {e}")
            raise

    async def delete_document(
        self,
        db: AsyncSession,
        document_id: UUID,
    ) -> bool:
        """
        Delete a document from the RAG system.

        Args:
            db: Database session
            document_id: Document ID to delete

        Returns:
            True if successful
        """
        try:
            # Get document from database
            doc = await db.get(VectorDocument, document_id)
            if not doc:
                logger.warning(f"Document {document_id} not found")
                return False

            # Remove from Qdrant if indexed
            if doc.vector_id and self.qdrant.enabled:
                await self.qdrant.delete_vectors([doc.vector_id])

            # Remove from BM25 index
            if doc.vector_id:
                self.bm25.remove_document(doc.vector_id)

            # Delete search index entries
            await db.execute(delete(SearchIndex).where(SearchIndex.document_id == document_id))

            # Delete document
            await db.delete(doc)
            await db.commit()

            logger.info(f"Successfully deleted document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            await db.rollback()
            return False

    async def update_document(
        self,
        db: AsyncSession,
        document_id: UUID,
        content: str | None = None,
        metadata: dict[str, Any] | None = None,
        get_embeddings_func: Any | None = None,
    ) -> VectorDocument | None:
        """
        Update a document in the RAG system.

        Args:
            db: Database session
            document_id: Document ID to update
            content: New content (optional)
            metadata: New metadata (optional)
            get_embeddings_func: Function to generate embeddings

        Returns:
            Updated VectorDocument or None if not found
        """
        try:
            # Get document from database
            doc = await db.get(VectorDocument, document_id)
            if not doc:
                logger.warning(f"Document {document_id} not found")
                return None

            # Update content if provided
            if content:
                doc.content = content

                # Update BM25 index
                if doc.vector_id:
                    self.bm25.remove_document(doc.vector_id)
                    self.bm25.add_document(content, doc.vector_id)

                # Update embeddings if function provided
                if get_embeddings_func and self.qdrant.enabled and doc.vector_id:
                    embedding = await get_embeddings_func(content)
                    if embedding:
                        await self.qdrant.upsert_vectors(
                            vectors=[embedding],
                            payloads=[
                                {
                                    "document_id": str(doc.id),
                                    "title": doc.title,
                                    "document_type": doc.document_type,
                                    "content": content[:500],
                                    "metadata": doc.doc_metadata,
                                }
                            ],
                            ids=[doc.vector_id],
                        )

            # Update metadata if provided
            if metadata:
                doc.doc_metadata = {**doc.doc_metadata, **metadata}

            # Update timestamps
            doc.updated_at = datetime.now(UTC)

            await db.commit()

            logger.info(f"Successfully updated document {document_id}")
            return doc

        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {e}")
            await db.rollback()
            return None

    async def get_ingestion_stats(self, db: AsyncSession) -> dict[str, Any]:
        """
        Get statistics about ingested documents.

        Args:
            db: Database session

        Returns:
            Dictionary with ingestion statistics
        """
        try:
            # Count documents by type
            from sqlalchemy import func, select

            type_counts = await db.execute(
                select(
                    VectorDocument.document_type,
                    func.count(VectorDocument.id).label("count"),
                ).group_by(VectorDocument.document_type)
            )

            # Count total documents and chunks
            total_docs = await db.execute(select(func.count(VectorDocument.id)))
            total_count = total_docs.scalar() or 0

            # Count indexed documents
            indexed_docs = await db.execute(
                select(func.count(VectorDocument.id)).where(VectorDocument.indexed_at.isnot(None))
            )
            indexed_count = indexed_docs.scalar() or 0

            # Get BM25 stats
            bm25_stats = self.bm25.get_index_stats()

            # Get Qdrant stats
            qdrant_stats = None
            if self.qdrant.enabled:
                qdrant_stats = await self.qdrant.get_collection_info()

            return {
                "total_documents": total_count,
                "indexed_documents": indexed_count,
                "documents_by_type": {row[0]: row[1] for row in type_counts},
                "bm25_stats": bm25_stats,
                "qdrant_stats": qdrant_stats,
            }

        except Exception as e:
            logger.error(f"Failed to get ingestion stats: {e}")
            return {}


# Singleton instance
document_ingestion_service = DocumentIngestionService()
