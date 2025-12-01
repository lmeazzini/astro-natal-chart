#!/usr/bin/env python3
"""
Script to populate Qdrant vector database with RAG documents.

This script ingests PDF and DOCX files from docs/references/rag/ into the
RAG system for enhanced astrological interpretations.

Usage:
    # From the project root:
    cd apps/api && uv run python ../../scripts/populate_rag.py

    # Or with Docker:
    docker exec -it astro-api python /app/scripts/populate_rag.py

    # Clear existing documents first:
    cd apps/api && uv run python ../../scripts/populate_rag.py --clear
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add the api app directory to the path
# Script is at /astro/scripts/, api is at /astro/apps/api/
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

from loguru import logger


async def get_embedding(text: str) -> list[float] | None:
    """Generate embedding using OpenAI."""
    from openai import AsyncOpenAI

    from app.core.config import settings

    if not settings.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set, skipping embeddings")
        return None

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text[:8000],  # Truncate to avoid token limits
        )
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding with {len(embedding)} dimensions")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document

        doc = Document(file_path)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        return "\n\n".join(paragraphs)
    except ImportError:
        logger.error("python-docx not installed. Install with: uv add python-docx")
        raise
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise


def extract_text_from_pdf(file_path: Path) -> list[tuple[int, str]]:
    """
    Extract text from a PDF file.

    Returns:
        List of tuples (page_number, text)
    """
    try:
        import PyPDF2

        pages = []
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append((i + 1, text))
        return pages
    except ImportError:
        logger.error("PyPDF2 not installed. Install with: uv add PyPDF2")
        raise
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise


async def clear_all_documents(db) -> int:
    """Clear all existing documents from the RAG system."""
    from sqlalchemy import delete, select
    from sqlalchemy.sql import func

    from app.models.search_index import SearchIndex
    from app.models.vector_document import VectorDocument
    from app.services.rag.bm25_service import bm25_service
    from app.services.rag.qdrant_service import qdrant_service

    # Count existing documents
    count_result = await db.execute(select(func.count(VectorDocument.id)))
    count = count_result.scalar() or 0

    if count == 0:
        logger.info("No existing documents to clear")
        return 0

    logger.info(f"Clearing {count} existing documents...")

    # Clear Qdrant collection
    if qdrant_service.enabled and qdrant_service.client:
        try:
            # Delete and recreate collection
            qdrant_service.client.delete_collection(
                collection_name=qdrant_service.collection_name
            )
            qdrant_service._ensure_collection()
            logger.info("Cleared Qdrant collection")
        except Exception as e:
            logger.warning(f"Failed to clear Qdrant: {e}")

    # Clear BM25 in-memory index by resetting its properties
    bm25_service.corpus = []
    bm25_service.document_ids = []
    bm25_service.bm25 = None
    logger.info("Cleared BM25 index")

    # Clear database tables
    await db.execute(delete(SearchIndex))
    await db.execute(delete(VectorDocument))
    await db.commit()

    logger.info(f"Cleared {count} documents from database")
    return count


async def ingest_document(
    db,
    title: str,
    content: str,
    document_type: str,
    metadata: dict,
) -> int:
    """Ingest a single document into the RAG system."""
    from app.services.rag.document_ingestion_service import document_ingestion_service

    try:
        documents = await document_ingestion_service.ingest_text(
            db=db,
            title=title,
            content=content,
            document_type=document_type,
            metadata=metadata,
            get_embeddings_func=get_embedding,
        )
        return len(documents)
    except Exception as e:
        logger.error(f"Failed to ingest '{title}': {e}")
        return 0


async def process_pdf(db, file_path: Path) -> int:
    """Process a PDF file and ingest all pages."""
    logger.info(f"Processing PDF: {file_path.name}")

    pages = extract_text_from_pdf(file_path)
    if not pages:
        logger.warning(f"No text extracted from {file_path.name}")
        return 0

    total_chunks = 0
    for page_num, text in pages:
        if len(text.strip()) < 100:  # Skip very short pages
            continue

        chunks = await ingest_document(
            db=db,
            title=f"{file_path.stem} - Page {page_num}",
            content=text,
            document_type="pdf",
            metadata={
                "source": file_path.name,
                "page": page_num,
                "total_pages": len(pages),
                "category": "astrology_reference",
            },
        )
        total_chunks += chunks

    logger.info(f"Ingested {total_chunks} chunks from {file_path.name}")
    return total_chunks


async def process_docx(db, file_path: Path) -> int:
    """Process a DOCX file and ingest it."""
    logger.info(f"Processing DOCX: {file_path.name}")

    text = extract_text_from_docx(file_path)
    if not text or len(text.strip()) < 100:
        logger.warning(f"No significant text extracted from {file_path.name}")
        return 0

    chunks = await ingest_document(
        db=db,
        title=file_path.stem,
        content=text,
        document_type="docx",
        metadata={
            "source": file_path.name,
            "category": "astrology_reference",
        },
    )

    logger.info(f"Ingested {chunks} chunks from {file_path.name}")
    return chunks


async def main(clear: bool = False, docs_path: str | None = None):
    """Main function to populate RAG with documents."""
    from app.core.config import settings
    from app.core.database import AsyncSessionLocal

    # Import all models to ensure relationships are properly configured
    from app.models import (  # noqa: F401
        AuditLog,
        BirthChart,
        InterpretationCache,
        OAuthAccount,
        PasswordResetToken,
        SearchIndex,
        User,
        UserConsent,
        VectorDocument,
    )
    from app.models.interpretation import ChartInterpretation  # noqa: F401
    from app.models.subscription import Subscription  # noqa: F401

    # Determine documents path
    if docs_path:
        rag_docs_path = Path(docs_path)
    else:
        # Default path: script is at /astro/scripts/, docs at /astro/docs/references/rag/
        rag_docs_path = Path(__file__).parent.parent / "docs" / "references" / "rag"

    if not rag_docs_path.exists():
        logger.error(f"Documents directory not found: {rag_docs_path}")
        logger.info("Please create the directory and add PDF/DOCX files")
        return

    # List available files
    pdf_files = list(rag_docs_path.glob("*.pdf"))
    docx_files = list(rag_docs_path.glob("*.docx"))
    doc_files = list(rag_docs_path.glob("*.doc"))

    total_files = len(pdf_files) + len(docx_files) + len(doc_files)
    if total_files == 0:
        logger.error(f"No PDF or DOCX files found in {rag_docs_path}")
        return

    logger.info(f"Found {len(pdf_files)} PDFs, {len(docx_files)} DOCX, {len(doc_files)} DOC files")

    if doc_files:
        logger.warning(
            f"Found {len(doc_files)} .doc files - these are not supported. "
            "Please convert them to .docx format."
        )

    # Check OpenAI API key
    if not settings.OPENAI_API_KEY:
        logger.warning(
            "OPENAI_API_KEY not configured - documents will be indexed for BM25 "
            "search only, without semantic embeddings"
        )

    async with AsyncSessionLocal() as db:
        # Clear existing documents if requested
        if clear:
            await clear_all_documents(db)

        total_chunks = 0

        # Process PDF files
        for pdf_file in pdf_files:
            try:
                chunks = await process_pdf(db, pdf_file)
                total_chunks += chunks
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                continue

        # Process DOCX files
        for docx_file in docx_files:
            try:
                chunks = await process_docx(db, docx_file)
                total_chunks += chunks
            except Exception as e:
                logger.error(f"Error processing {docx_file.name}: {e}")
                continue

        # Print summary
        logger.info("=" * 50)
        logger.info("RAG Population Complete!")
        logger.info(f"Total files processed: {len(pdf_files) + len(docx_files)}")
        logger.info(f"Total chunks created: {total_chunks}")
        logger.info("=" * 50)

        # Get and print stats
        from app.services.rag.document_ingestion_service import document_ingestion_service

        stats = await document_ingestion_service.get_ingestion_stats(db)
        logger.info(f"Total documents in DB: {stats.get('total_documents', 0)}")
        logger.info(f"Indexed documents: {stats.get('indexed_documents', 0)}")
        logger.info(f"Documents by type: {stats.get('documents_by_type', {})}")

        if stats.get("qdrant_stats"):
            qdrant_info = stats["qdrant_stats"]
            logger.info(f"Qdrant vectors: {qdrant_info.get('points_count', 0)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate RAG with astrological documents")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing documents before ingesting",
    )
    parser.add_argument(
        "--path",
        type=str,
        help="Custom path to documents directory (default: docs/references/rag/)",
    )

    args = parser.parse_args()

    asyncio.run(main(clear=args.clear, docs_path=args.path))
