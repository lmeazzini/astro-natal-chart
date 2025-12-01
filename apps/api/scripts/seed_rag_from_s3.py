#!/usr/bin/env python
"""
Script to download RAG documents from S3 and ingest into Qdrant + PostgreSQL.

This script:
1. Lists all documents in S3 bucket (genesis-dev-559050210551) with prefix rag_documents
2. Downloads each document
3. Ingests into PostgreSQL vector_documents table
4. Creates embeddings and stores in Qdrant
5. Creates BM25 search indices

Usage:
    docker compose exec api uv run python scripts/seed_rag_from_s3.py

    # With options
    docker compose exec api uv run python scripts/seed_rag_from_s3.py --clear --verbose
"""

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/app")

import boto3
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import (  # noqa: F401
    AuditLog,
    BirthChart,
    BlogPost,
    ChartInterpretation,
    InterpretationCache,
    OAuthAccount,
    PasswordResetToken,
    PublicChart,
    PublicChartInterpretation,
    SearchIndex,
    Subscription,
    User,
    UserConsent,
    VectorDocument,
)
from app.services.rag import document_ingestion_service


async def generate_embedding(text: str, client: AsyncOpenAI) -> list[float] | None:
    """Generate embedding for text using OpenAI."""
    try:
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        return None


async def clear_existing_documents(db: AsyncSession) -> None:
    """Clear all existing documents from database."""
    try:
        logger.info("Clearing existing documents from PostgreSQL...")
        await db.execute(delete(SearchIndex))
        await db.execute(delete(VectorDocument))
        await db.commit()
        logger.info("✅ Cleared existing documents from PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to clear documents: {e}")
        await db.rollback()
        raise


def list_s3_documents(bucket: str, prefix: str) -> list[dict]:
    """
    List all documents in S3 bucket with given prefix.

    Returns:
        List of dicts with keys: key, size, last_modified
    """
    try:
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        logger.info(f"Listing objects in s3://{bucket}/{prefix}")

        documents = []
        paginator = s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            if "Contents" not in page:
                continue

            for obj in page["Contents"]:
                # Skip directories (keys ending with /)
                if obj["Key"].endswith("/"):
                    continue

                documents.append(
                    {
                        "key": obj["Key"],
                        "size": obj["Size"],
                        "last_modified": obj["LastModified"],
                    }
                )

        logger.info(f"Found {len(documents)} documents in S3")
        return documents

    except Exception as e:
        logger.error(f"Failed to list S3 documents: {e}")
        raise


def download_s3_document(bucket: str, key: str, local_path: Path) -> bool:
    """Download document from S3 to local path."""
    try:
        s3_client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        s3_client.download_file(bucket, key, str(local_path))
        return True

    except Exception as e:
        logger.error(f"Failed to download {key}: {e}")
        return False


def determine_document_type(key: str) -> str:
    """Determine document type from S3 key."""
    # Extract type from path: rag_documents/type/filename
    parts = key.split("/")
    if len(parts) >= 2:
        return parts[1]  # Second part is the type (texts, pdfs, etc.)
    return "unknown"


async def ingest_document(
    db: AsyncSession,
    file_path: Path,
    document_type: str,
    metadata: dict,
    get_embeddings_func,
) -> int:
    """
    Ingest a document (text or PDF) into the RAG system.

    Returns:
        Number of chunks created
    """
    try:
        # Check file extension
        if file_path.suffix.lower() == ".pdf":
            # Ingest as PDF
            documents = await document_ingestion_service.ingest_pdf(
                db=db,
                pdf_path=file_path,
                metadata=metadata,
                get_embeddings_func=get_embeddings_func,
            )
        else:
            # Ingest as text
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            title = file_path.stem.replace("_", " ").replace("-", " ").title()

            documents = await document_ingestion_service.ingest_text(
                db=db,
                title=title,
                content=content,
                document_type=document_type,
                metadata=metadata,
                get_embeddings_func=get_embeddings_func,
            )

        return len(documents)

    except Exception as e:
        logger.error(f"Failed to ingest {file_path}: {e}")
        raise


async def seed_from_s3(
    bucket: str = "genesis-dev-559050210551",
    prefix: str = "rag_documents",
    clear: bool = False,
    verbose: bool = False,
) -> None:
    """
    Download documents from S3 and seed RAG system.

    Args:
        bucket: S3 bucket name
        prefix: S3 key prefix
        clear: If True, clear existing documents first
        verbose: Enable verbose logging
    """
    if verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    logger.info("=" * 70)
    logger.info("RAG SYSTEM SEEDING FROM S3")
    logger.info("=" * 70)
    logger.info(f"S3 Bucket: {bucket}")
    logger.info(f"S3 Prefix: {prefix}")
    logger.info(f"OpenAI API Key configured: {bool(settings.OPENAI_API_KEY)}")
    logger.info("=" * 70)

    # Check configuration
    if not settings.OPENAI_API_KEY:
        logger.error("❌ OpenAI API key not configured")
        logger.error("Set OPENAI_API_KEY in .env file")
        return

    if not settings.AWS_ACCESS_KEY_ID:
        logger.error("❌ AWS credentials not configured")
        logger.error("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
        return

    # Initialize OpenAI client
    openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_embeddings(text: str) -> list[float] | None:
        return await generate_embedding(text, openai_client)

    # Connect to database
    async with AsyncSessionLocal() as db:
        # Clear existing documents if requested
        if clear:
            await clear_existing_documents(db)

    # List S3 documents
    try:
        s3_documents = list_s3_documents(bucket, prefix)
    except Exception as e:
        logger.error(f"Failed to list S3 documents: {e}")
        return

    if not s3_documents:
        logger.warning(f"No documents found in s3://{bucket}/{prefix}")
        return

    # Process each document
    total_chunks = 0
    failed = 0
    temp_dir = Path(tempfile.mkdtemp())

    try:
        for idx, s3_doc in enumerate(s3_documents, 1):
            key = s3_doc["key"]
            size_mb = s3_doc["size"] / (1024 * 1024)

            logger.info(f"\n[{idx}/{len(s3_documents)}] Processing: {key} ({size_mb:.2f} MB)")

            # Download to temp directory
            filename = Path(key).name
            local_path = temp_dir / filename

            if not download_s3_document(bucket, key, local_path):
                logger.error(f"❌ Failed to download {key}")
                failed += 1
                continue

            # Determine document type and metadata
            doc_type = determine_document_type(key)
            metadata = {
                "s3_bucket": bucket,
                "s3_key": key,
                "source": "s3",
                "file_size": s3_doc["size"],
                "last_modified": s3_doc["last_modified"].isoformat(),
            }

            # Ingest document
            try:
                async with AsyncSessionLocal() as db:
                    chunks = await ingest_document(
                        db=db,
                        file_path=local_path,
                        document_type=doc_type,
                        metadata=metadata,
                        get_embeddings_func=get_embeddings,
                    )

                    total_chunks += chunks
                    logger.info(f"✅ Successfully ingested {filename} ({chunks} chunks)")

            except Exception as e:
                logger.error(f"❌ Failed to ingest {filename}: {e}")
                failed += 1

            # Clean up downloaded file
            local_path.unlink(missing_ok=True)

    finally:
        # Clean up temp directory
        try:
            temp_dir.rmdir()
        except Exception:
            pass

    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("SEEDING SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total S3 documents: {len(s3_documents)}")
    logger.info(f"✅ Successfully ingested: {len(s3_documents) - failed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📦 Total chunks created: {total_chunks}")
    logger.info("=" * 70)

    # Get final stats
    async with AsyncSessionLocal() as db:
        stats = await document_ingestion_service.get_ingestion_stats(db)
        logger.info("\nFINAL STATISTICS:")
        logger.info(f"Total documents in PostgreSQL: {stats.get('total_documents', 0)}")
        logger.info(f"Indexed documents: {stats.get('indexed_documents', 0)}")
        logger.info(f"Documents by type: {stats.get('documents_by_type', {})}")

        if stats.get("qdrant_stats"):
            logger.info(f"Qdrant points: {stats['qdrant_stats'].get('points_count', 0)}")
            logger.info(f"Qdrant status: {stats['qdrant_stats'].get('status', 'unknown')}")


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Seed RAG system from S3 documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--bucket",
        type=str,
        default="genesis-dev-559050210551",
        help="S3 bucket name (default: genesis-dev-559050210551)",
    )

    parser.add_argument(
        "--prefix",
        type=str,
        default="rag_documents",
        help="S3 key prefix (default: rag_documents)",
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing documents before seeding",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    try:
        asyncio.run(
            seed_from_s3(
                bucket=args.bucket,
                prefix=args.prefix,
                clear=args.clear,
                verbose=args.verbose,
            )
        )
        return 0
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
