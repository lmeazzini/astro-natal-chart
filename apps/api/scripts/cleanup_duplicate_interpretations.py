#!/usr/bin/env python3
"""
Cleanup duplicate chart interpretations.

This script removes duplicate interpretations from the chart_interpretations table.
For each unique combination of (chart_id, interpretation_type, subject, language),
it keeps the most recent interpretation and deletes older duplicates.

Usage:
    # Dry run (shows what would be deleted)
    python scripts/cleanup_duplicate_interpretations.py --dry-run

    # Actual cleanup
    python scripts/cleanup_duplicate_interpretations.py

    # With verbose output
    python scripts/cleanup_duplicate_interpretations.py --verbose
"""

import argparse
import asyncio
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def count_total_interpretations(db: AsyncSession) -> int:
    """Count total number of interpretations."""
    result = await db.execute(text("SELECT COUNT(*) FROM chart_interpretations"))
    count = result.scalar()
    return count or 0


async def count_duplicate_interpretations(db: AsyncSession) -> int:
    """Count number of duplicate interpretations that would be deleted."""
    query = text("""
        SELECT COUNT(*) FROM (
            SELECT id, ROW_NUMBER() OVER (
                PARTITION BY chart_id, interpretation_type, subject, language
                ORDER BY created_at DESC
            ) as rn
            FROM chart_interpretations
        ) t
        WHERE t.rn > 1
    """)
    result = await db.execute(query)
    count = result.scalar()
    return count or 0


async def get_duplicate_stats(db: AsyncSession) -> dict:
    """Get statistics about duplicates per chart."""
    query = text("""
        SELECT
            bc.person_name,
            bc.id as chart_id,
            COUNT(*) as total_interpretations,
            COUNT(*) - COUNT(DISTINCT (ci.interpretation_type, ci.subject, ci.language)) as duplicates
        FROM chart_interpretations ci
        JOIN birth_charts bc ON ci.chart_id = bc.id
        GROUP BY bc.id, bc.person_name
        HAVING COUNT(*) - COUNT(DISTINCT (ci.interpretation_type, ci.subject, ci.language)) > 0
        ORDER BY duplicates DESC
        LIMIT 10
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    stats = []
    for row in rows:
        stats.append(
            {"person_name": row[0], "chart_id": str(row[1]), "total": row[2], "duplicates": row[3]}
        )
    return stats


async def cleanup_duplicates(db: AsyncSession, dry_run: bool = True) -> int:
    """
    Remove duplicate interpretations, keeping the most recent one for each unique combination.

    Args:
        db: Database session
        dry_run: If True, only count duplicates without deleting

    Returns:
        Number of duplicate interpretations deleted (or would be deleted in dry-run)
    """
    # First, count duplicates
    duplicate_count = await count_duplicate_interpretations(db)

    if duplicate_count == 0:
        logger.info("No duplicate interpretations found!")
        return 0

    if dry_run:
        logger.info(f"[DRY RUN] Would delete {duplicate_count} duplicate interpretations")
        return duplicate_count

    # Actual deletion
    logger.info(f"Deleting {duplicate_count} duplicate interpretations...")

    delete_query = text("""
        DELETE FROM chart_interpretations
        WHERE id IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (
                    PARTITION BY chart_id, interpretation_type, subject, language
                    ORDER BY created_at DESC
                ) as rn
                FROM chart_interpretations
            ) t
            WHERE t.rn > 1
        )
    """)

    result = await db.execute(delete_query)
    await db.commit()

    deleted_count = result.rowcount
    logger.success(f"Successfully deleted {deleted_count} duplicate interpretations")

    return deleted_count


async def main(dry_run: bool = True, verbose: bool = False):
    """Main cleanup function."""
    start_time = datetime.now(UTC)

    logger.info("=" * 60)
    logger.info("Chart Interpretations Cleanup Script")
    logger.info("=" * 60)

    if dry_run:
        logger.warning("[DRY RUN MODE] No changes will be made to the database")
    else:
        logger.warning("[LIVE MODE] Duplicate interpretations will be DELETED")

    async with AsyncSessionLocal() as db:
        # Step 1: Count total interpretations
        total_count = await count_total_interpretations(db)
        logger.info(f"Total interpretations in database: {total_count}")

        # Step 2: Count duplicates
        duplicate_count = await count_duplicate_interpretations(db)
        logger.info(f"Duplicate interpretations found: {duplicate_count}")

        if duplicate_count == 0:
            logger.success("No duplicates to clean up!")
            return

        # Step 3: Show top charts with duplicates (verbose mode)
        if verbose:
            logger.info("\nTop 10 charts with most duplicates:")
            stats = await get_duplicate_stats(db)
            for i, stat in enumerate(stats, 1):
                logger.info(
                    f"  {i}. {stat['person_name']}: "
                    f"{stat['total']} total, {stat['duplicates']} duplicates"
                )

        # Step 4: Cleanup
        logger.info("")
        deleted = await cleanup_duplicates(db, dry_run=dry_run)

        # Step 5: Verify cleanup
        if not dry_run:
            remaining_duplicates = await count_duplicate_interpretations(db)
            final_count = await count_total_interpretations(db)

            logger.info("")
            logger.info("Cleanup Summary:")
            logger.info(f"  - Initial total: {total_count}")
            logger.info(f"  - Deleted: {deleted}")
            logger.info(f"  - Final total: {final_count}")
            logger.info(f"  - Remaining duplicates: {remaining_duplicates}")

            if remaining_duplicates > 0:
                logger.error(f"WARNING: {remaining_duplicates} duplicates still remain!")
            else:
                logger.success("All duplicates successfully removed!")

    elapsed = (datetime.now(UTC) - start_time).total_seconds()
    logger.info(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup duplicate chart interpretations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed statistics about duplicates"
    )

    args = parser.parse_args()

    # Run cleanup
    asyncio.run(main(dry_run=args.dry_run, verbose=args.verbose))
