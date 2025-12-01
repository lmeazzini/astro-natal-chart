#!/usr/bin/env python
"""
Script to upload local RAG documents to AWS S3.

This script:
1. Reads all documents from the local RAG_LOCAL_PATH directory
2. Uploads them to S3 bucket preserving directory structure
3. Optionally verifies uploads and shows progress

Usage:
    # Upload all documents
    python scripts/upload_rag_docs_to_s3.py

    # Upload specific document type
    python scripts/upload_rag_docs_to_s3.py --type texts

    # Dry run (show what would be uploaded)
    python scripts/upload_rag_docs_to_s3.py --dry-run

    # Skip verification
    python scripts/upload_rag_docs_to_s3.py --no-verify

Run inside Docker:
    docker exec astro-api sh -c 'cd /app && .venv/bin/python scripts/upload_rag_docs_to_s3.py'
"""

import argparse
import mimetypes
import sys
from pathlib import Path

sys.path.insert(0, "/app")

from loguru import logger  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.services.rag.s3_document_loader import S3DocumentLoader  # noqa: E402


def get_content_type(file_path: Path) -> str:
    """
    Determine MIME type from file extension.

    Args:
        file_path: Path to file

    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def upload_documents(
    document_type: str | None = None,
    dry_run: bool = False,
    verify: bool = True,
) -> dict[str, int | str]:
    """
    Upload local RAG documents to S3.

    Args:
        document_type: Optional filter by document type subdirectory
        dry_run: If True, only show what would be uploaded
        verify: If True, verify uploads by checking existence

    Returns:
        Dictionary with upload statistics (int values) or error (str value)
    """
    # Initialize loaders
    local_path = Path(settings.RAG_LOCAL_PATH)
    if not local_path.exists():
        logger.error(f"Local RAG path does not exist: {local_path}")
        return {"error": "Local path not found"}

    # Check S3 configuration
    if not settings.rag_s3_enabled:
        logger.error(
            "S3 storage is not enabled. Set RAG_STORAGE_TYPE=s3 and configure AWS credentials."
        )
        return {"error": "S3 not configured"}

    s3_loader = S3DocumentLoader()

    # Find all documents
    search_path = local_path
    if document_type:
        search_path = local_path / document_type
        if not search_path.exists():
            logger.error(f"Document type path does not exist: {search_path}")
            return {"error": f"Path not found: {document_type}"}

    files = list(search_path.rglob("*"))
    files = [f for f in files if f.is_file()]

    if not files:
        logger.warning(f"No files found in {search_path}")
        return {"total": 0, "uploaded": 0, "failed": 0, "skipped": 0}

    logger.info(f"Found {len(files)} files to upload")

    stats: dict[str, int | str] = {
        "total": len(files),
        "uploaded": 0,
        "failed": 0,
        "skipped": 0,
        "verified": 0,
    }

    for file_path in files:
        # Get relative path from local_path
        relative_path = str(file_path.relative_to(local_path))

        # Determine content type
        content_type = get_content_type(file_path)

        try:
            # Check if already exists in S3
            if s3_loader.document_exists(relative_path):
                logger.info(f"⏭️  SKIP: {relative_path} (already exists)")
                assert isinstance(stats["skipped"], int)
                stats["skipped"] += 1
                continue

            if dry_run:
                logger.info(f"🔍 DRY-RUN: Would upload {relative_path} ({content_type})")
                assert isinstance(stats["uploaded"], int)
                stats["uploaded"] += 1
                continue

            # Upload to S3
            logger.info(f"⬆️  Uploading: {relative_path} ({file_path.stat().st_size} bytes)")

            with open(file_path, "rb") as f:
                s3_key = s3_loader.upload_document(
                    relative_path=relative_path,
                    content=f,
                    content_type=content_type,
                )

            logger.info(f"✅ Uploaded: {s3_key}")
            assert isinstance(stats["uploaded"], int)
            stats["uploaded"] += 1

            # Verify upload if requested
            if verify:
                if s3_loader.document_exists(relative_path):
                    assert isinstance(stats["verified"], int)
                    stats["verified"] += 1
                else:
                    logger.warning(f"⚠️  Verification failed: {relative_path}")

        except Exception as e:
            logger.error(f"❌ Failed to upload {relative_path}: {e}")
            assert isinstance(stats["failed"], int)
            stats["failed"] += 1

    return stats


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Upload local RAG documents to AWS S3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Upload all documents
    python scripts/upload_rag_docs_to_s3.py

    # Upload only PDFs
    python scripts/upload_rag_docs_to_s3.py --type pdfs

    # Dry run to see what would be uploaded
    python scripts/upload_rag_docs_to_s3.py --dry-run

    # Upload without verification (faster)
    python scripts/upload_rag_docs_to_s3.py --no-verify
        """,
    )

    parser.add_argument(
        "--type",
        type=str,
        help="Document type subdirectory to upload (e.g., 'texts', 'pdfs', 'interpretations')",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading",
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip verification after upload (faster but less safe)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    # Print banner
    print("=" * 70)
    print("RAG DOCUMENTS S3 UPLOAD")
    print("=" * 70)
    print(f"Local path: {settings.RAG_LOCAL_PATH}")
    print(f"S3 bucket: {settings.RAG_S3_BUCKET}")
    print(f"S3 prefix: {settings.RAG_S3_PREFIX}")
    if args.type:
        print(f"Document type: {args.type}")
    if args.dry_run:
        print("Mode: DRY-RUN (no actual uploads)")
    print("=" * 70)
    print()

    # Upload documents
    stats = upload_documents(
        document_type=args.type,
        dry_run=args.dry_run,
        verify=not args.no_verify,
    )

    # Print summary
    print()
    print("=" * 70)
    print("UPLOAD SUMMARY")
    print("=" * 70)

    if "error" in stats:
        print(f"❌ Error: {stats['error']}")
        return 1

    print(f"Total files: {stats['total']}")
    print(f"✅ Uploaded: {stats['uploaded']}")
    print(f"⏭️  Skipped (already exist): {stats['skipped']}")
    print(f"❌ Failed: {stats['failed']}")

    if not args.dry_run and not args.no_verify:
        print(f"✓  Verified: {stats['verified']}")

    print("=" * 70)

    # Exit with error code if any uploads failed
    failed_count = stats.get("failed", 0)
    return 1 if (isinstance(failed_count, int) and failed_count > 0) else 0


if __name__ == "__main__":
    sys.exit(main())
