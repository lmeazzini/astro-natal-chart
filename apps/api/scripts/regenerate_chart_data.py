#!/usr/bin/env python3
"""
Regenerate chart_data for all charts in birth_charts and public_charts tables.

This script recalculates the astrological chart data using the current version of
calculate_birth_chart() and updates the database records with fresh data.

Usage:
    uv run python scripts/regenerate_chart_data.py [--birth-charts] [--public-charts] [--dry-run]

Arguments:
    --birth-charts: Regenerate only birth_charts (default: both)
    --public-charts: Regenerate only public_charts (default: both)
    --dry-run: Show what would be updated without making changes
    --verbose: Enable verbose logging
"""

import asyncio
import sys
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.models.public_chart import PublicChart
from app.services.astro_service import calculate_birth_chart


async def regenerate_birth_charts(
    db: AsyncSession, dry_run: bool = False, verbose: bool = False
) -> tuple[int, int]:
    """Regenerate chart_data for all birth_charts.

    Returns:
        Tuple of (success_count, fail_count)
    """
    logger.info("Fetching birth charts from database...")

    # Get all birth charts that are completed (have chart_data)
    stmt = select(BirthChart).where(BirthChart.deleted_at.is_(None))
    result = await db.execute(stmt)
    charts = result.scalars().all()

    logger.info(f"Found {len(charts)} birth charts to process")

    success_count = 0
    fail_count = 0

    for i, chart in enumerate(charts, 1):
        try:
            if verbose:
                logger.info(f"[{i}/{len(charts)}] Processing: {chart.person_name} (ID: {chart.id})")

            # Calculate new chart data
            new_chart_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system,
            )

            if dry_run:
                logger.info(f"  [DRY-RUN] Would update chart {chart.id}")
                success_count += 1
                continue

            # Update the chart
            chart.chart_data = new_chart_data
            chart.updated_at = datetime.now(UTC)

            success_count += 1
            if verbose:
                logger.success(f"  ✓ Updated chart for {chart.person_name}")

        except Exception as e:
            fail_count += 1
            logger.error(f"  ✗ Failed to process {chart.person_name}: {e}")
            continue

    if not dry_run:
        await db.commit()
        logger.success(f"Committed {success_count} birth chart updates to database")

    return success_count, fail_count


async def regenerate_public_charts(
    db: AsyncSession, dry_run: bool = False, verbose: bool = False
) -> tuple[int, int]:
    """Regenerate chart_data for all public_charts.

    Returns:
        Tuple of (success_count, fail_count)
    """
    logger.info("Fetching public charts from database...")

    # Get all public charts
    stmt = select(PublicChart)
    result = await db.execute(stmt)
    charts = result.scalars().all()

    logger.info(f"Found {len(charts)} public charts to process")

    success_count = 0
    fail_count = 0

    for i, chart in enumerate(charts, 1):
        try:
            if verbose:
                logger.info(f"[{i}/{len(charts)}] Processing: {chart.full_name} ({chart.slug})")

            # Calculate new chart data
            new_chart_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system,
            )

            if dry_run:
                logger.info(f"  [DRY-RUN] Would update chart {chart.slug}")
                success_count += 1
                continue

            # Update the chart
            chart.chart_data = new_chart_data
            chart.updated_at = datetime.now(UTC)

            success_count += 1
            if verbose:
                logger.success(f"  ✓ Updated chart for {chart.full_name}")

        except Exception as e:
            fail_count += 1
            logger.error(f"  ✗ Failed to process {chart.full_name}: {e}")
            continue

    if not dry_run:
        await db.commit()
        logger.success(f"Committed {success_count} public chart updates to database")

    return success_count, fail_count


async def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Regenerate chart_data for birth_charts and public_charts"
    )
    parser.add_argument(
        "--birth-charts",
        action="store_true",
        help="Regenerate only birth_charts",
    )
    parser.add_argument(
        "--public-charts",
        action="store_true",
        help="Regenerate only public_charts",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # If neither flag is set, process both
    process_birth = args.birth_charts or (not args.birth_charts and not args.public_charts)
    process_public = args.public_charts or (not args.birth_charts and not args.public_charts)

    logger.info(f"\n{'='*60}")
    logger.info("CHART DATA REGENERATION SCRIPT")
    logger.info(f"{'='*60}")
    logger.info(f"Process birth_charts: {process_birth}")
    logger.info(f"Process public_charts: {process_public}")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"{'='*60}\n")

    total_success = 0
    total_fail = 0

    async with AsyncSessionLocal() as db:
        try:
            # Process birth_charts
            if process_birth:
                logger.info("\n" + "=" * 40)
                logger.info("PROCESSING BIRTH CHARTS")
                logger.info("=" * 40)
                success, fail = await regenerate_birth_charts(
                    db, dry_run=args.dry_run, verbose=args.verbose
                )
                total_success += success
                total_fail += fail
                logger.info(f"Birth charts: {success} success, {fail} failed\n")

            # Process public_charts
            if process_public:
                logger.info("\n" + "=" * 40)
                logger.info("PROCESSING PUBLIC CHARTS")
                logger.info("=" * 40)
                success, fail = await regenerate_public_charts(
                    db, dry_run=args.dry_run, verbose=args.verbose
                )
                total_success += success
                total_fail += fail
                logger.info(f"Public charts: {success} success, {fail} failed\n")

            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("REGENERATION COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"✓ Total success: {total_success}")
            if total_fail > 0:
                logger.warning(f"✗ Total failed: {total_fail}")
            if args.dry_run:
                logger.info("(DRY RUN - no changes were made)")
            logger.info(f"{'='*60}\n")

        except Exception as e:
            logger.error(f"Fatal error during regeneration: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
