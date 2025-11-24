"""RAG API endpoints for vector search and document management."""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.models.vector_document import VectorDocument
from app.services.rag import (
    document_ingestion_service,
    hybrid_search_service,
)

# OpenAI client for embeddings
_openai_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    """Get or create OpenAI client singleton."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def generate_embedding(text: str) -> list[float] | None:
    """
    Generate embedding for text using OpenAI.

    Args:
        text: Text to embed

    Returns:
        Embedding vector or None if error
    """
    try:
        client = get_openai_client()
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None

router = APIRouter(prefix="/rag", tags=["RAG"])


# Request/Response schemas
class SearchRequest(BaseModel):
    """Request schema for hybrid search."""

    query: str = Field(..., description="Search query text")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    fusion_method: str = Field("rrf", description="Fusion method: 'rrf' or 'weighted'")
    filters: dict[str, Any] | None = Field(None, description="Optional metadata filters")


class SearchResult(BaseModel):
    """Search result schema."""

    document_id: str
    title: str
    content_preview: str
    score: float
    metadata: dict[str, Any]
    source_type: str  # "dense", "sparse", or "hybrid"


class SearchResponse(BaseModel):
    """Response schema for search."""

    query: str
    results: list[SearchResult]
    total_results: int
    fusion_method: str


class IngestTextRequest(BaseModel):
    """Request schema for text ingestion."""

    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    document_type: str = Field("text", description="Type of document")
    metadata: dict[str, Any] | None = Field(None, description="Optional metadata")


class IngestResponse(BaseModel):
    """Response schema for document ingestion."""

    message: str
    documents_created: int
    document_ids: list[str]


class DocumentResponse(BaseModel):
    """Response schema for document details."""

    id: str
    title: str
    content: str
    document_type: str
    metadata: dict[str, Any]
    created_at: str
    indexed: bool


class StatsResponse(BaseModel):
    """Response schema for RAG statistics."""

    total_documents: int
    indexed_documents: int
    documents_by_type: dict[str, int]
    bm25_stats: dict[str, Any]
    qdrant_stats: dict[str, Any] | None


@router.post("/search", response_model=SearchResponse)
@limiter.limit(RateLimits.RAG_SEARCH)
async def search_documents(
    search_request: SearchRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """
    Perform hybrid search across documents.

    This endpoint combines:
    - Dense search: Semantic similarity using vector embeddings
    - Sparse search: Keyword matching using BM25
    - Fusion: RRF or weighted combination of results
    """
    try:
        # Generate embedding for semantic search
        query_vector = await generate_embedding(search_request.query)
        if query_vector is None:
            logger.warning("Failed to generate embedding, falling back to BM25-only search")

        # Perform hybrid search
        results = await hybrid_search_service.search(
            query=search_request.query,
            query_vector=query_vector,
            limit=search_request.limit,
            fusion_method=search_request.fusion_method,
            filters=search_request.filters,
        )

        # Format results
        formatted_results = []
        for result in results:
            # Get document from database
            doc_id = result.get("document_id")
            if doc_id:
                doc = await db.get(VectorDocument, UUID(doc_id) if len(doc_id) == 36 else None)
                if doc:
                    formatted_results.append(
                        SearchResult(
                            document_id=str(doc.id),
                            title=doc.title,
                            content_preview=doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                            score=result.get("hybrid_score", result.get("rrf_score", 0)),
                            metadata=doc.doc_metadata,
                            source_type="hybrid" if "hybrid_score" in result else "sparse",
                        )
                    )

        return SearchResponse(
            query=search_request.query,
            results=formatted_results,
            total_results=len(formatted_results),
            fusion_method=search_request.fusion_method,
        )

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        ) from e


@router.post("/ingest/text", response_model=IngestResponse)
@limiter.limit(RateLimits.RAG_INGEST_TEXT)
async def ingest_text_document(
    ingest_request: IngestTextRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    """
    Ingest a text document into the RAG system.

    This will:
    1. Chunk the document into smaller pieces
    2. Generate embeddings for each chunk
    3. Store in vector database (Qdrant)
    4. Index for BM25 search
    """
    try:
        documents = await document_ingestion_service.ingest_text(
            db=db,
            title=ingest_request.title,
            content=ingest_request.content,
            document_type=ingest_request.document_type,
            metadata=ingest_request.metadata,
            get_embeddings_func=generate_embedding,
        )

        return IngestResponse(
            message=f"Successfully ingested document '{ingest_request.title}'",
            documents_created=len(documents),
            document_ids=[str(doc.id) for doc in documents],
        )

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document ingestion failed: {str(e)}",
        ) from e


@router.post("/ingest/pdf", response_model=IngestResponse)
@limiter.limit(RateLimits.RAG_INGEST_PDF)
async def ingest_pdf_document(
    request: Request,
    file: UploadFile = File(...),
    metadata: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IngestResponse:
    """
    Ingest a PDF document into the RAG system.

    This will:
    1. Extract text from each PDF page
    2. Chunk the text into smaller pieces
    3. Generate embeddings for each chunk
    4. Store in vector database (Qdrant)
    5. Index for BM25 search
    """
    import json
    import tempfile
    from pathlib import Path

    try:
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            try:
                parsed_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning("Invalid metadata JSON, ignoring")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        try:
            # Ingest PDF
            documents = await document_ingestion_service.ingest_pdf(
                db=db,
                pdf_path=tmp_path,
                metadata={
                    **parsed_metadata,
                    "original_filename": file.filename,
                    "content_type": file.content_type,
                },
                get_embeddings_func=generate_embedding,
            )

            return IngestResponse(
                message=f"Successfully ingested PDF '{file.filename}'",
                documents_created=len(documents),
                document_ids=[str(doc.id) for doc in documents],
            )

        finally:
            # Clean up temporary file
            tmp_path.unlink()

    except Exception as e:
        logger.error(f"PDF ingestion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF ingestion failed: {str(e)}",
        ) from e


class DocumentListItem(BaseModel):
    """List item schema for document listing."""

    id: str
    title: str
    document_type: str
    content_preview: str
    page: int | None
    source: str | None
    created_at: str
    indexed: bool


class DocumentListResponse(BaseModel):
    """Response schema for document listing."""

    documents: list[DocumentListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    document_type: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """
    List all documents in the RAG system.

    Args:
        page: Page number (1-indexed)
        page_size: Number of documents per page (max 100)
        document_type: Optional filter by document type (text, pdf)

    Returns:
        Paginated list of documents with metadata
    """
    from sqlalchemy import func, select

    # Validate page_size
    page_size = min(page_size, 100)
    offset = (page - 1) * page_size

    # Build query
    query = select(VectorDocument)
    count_query = select(func.count(VectorDocument.id))

    if document_type:
        query = query.where(VectorDocument.document_type == document_type)
        count_query = count_query.where(VectorDocument.document_type == document_type)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get documents with pagination
    query = query.order_by(VectorDocument.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    documents = result.scalars().all()

    # Format response
    doc_items = []
    for doc in documents:
        metadata = doc.doc_metadata or {}
        doc_items.append(
            DocumentListItem(
                id=str(doc.id),
                title=doc.title,
                document_type=doc.document_type,
                content_preview=doc.content[:150] + "..." if len(doc.content) > 150 else doc.content,
                page=metadata.get("page"),
                source=metadata.get("source") or metadata.get("original_filename"),
                created_at=doc.created_at.isoformat(),
                indexed=doc.indexed_at is not None,
            )
        )

    total_pages = (total + page_size - 1) // page_size

    return DocumentListResponse(
        documents=doc_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Get details of a specific document."""
    doc = await db.get(VectorDocument, document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentResponse(
        id=str(doc.id),
        title=doc.title,
        content=doc.content,
        document_type=doc.document_type,
        metadata=doc.doc_metadata,
        created_at=doc.created_at.isoformat(),
        indexed=doc.indexed_at is not None,
    )


@router.delete("/documents/{document_id}")
@limiter.limit(RateLimits.RAG_DELETE)
async def delete_document(
    document_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a document from the RAG system."""
    try:
        success = await document_ingestion_service.delete_document(db, document_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        return {"message": f"Document {document_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document deletion failed: {str(e)}",
        ) from e


@router.get("/stats", response_model=StatsResponse)
async def get_rag_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StatsResponse:
    """Get statistics about the RAG system."""
    try:
        stats = await document_ingestion_service.get_ingestion_stats(db)

        return StatsResponse(
            total_documents=stats.get("total_documents", 0),
            indexed_documents=stats.get("indexed_documents", 0),
            documents_by_type=stats.get("documents_by_type", {}),
            bm25_stats=stats.get("bm25_stats", {}),
            qdrant_stats=stats.get("qdrant_stats"),
        )

    except Exception as e:
        logger.error(f"Failed to get RAG stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}",
        ) from e
