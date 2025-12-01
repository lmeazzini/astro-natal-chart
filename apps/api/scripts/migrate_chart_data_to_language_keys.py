#!/usr/bin/env python3
"""
Migration script to convert existing chart_data from single-language format
to the new language-keyed format: {"en-US": {...}, "pt-BR": {...}}

This script:
1. Identifies charts with old single-language format
2. Regenerates chart data for both supported languages
3. Updates the database with the new format

Supports both BirthChart and PublicChart models.

Usage:
    # Dry run (no changes)
    uv run python scripts/migrate_chart_data_to_language_keys.py --dry-run

    # Migrate all charts (BirthChart and PublicChart)
    uv run python scripts/migrate_chart_data_to_language_keys.py

    # Migrate only public charts
    uv run python scripts/migrate_chart_data_to_language_keys.py --public-only

    # Migrate specific chart
    uv run python scripts/migrate_chart_data_to_language_keys.py --chart-id <uuid>
"""

import argparse
import asyncio
import sys
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy import select

# Add the app directory to the path
sys.path.insert(0, "/app")

from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.models.public_chart import PublicChart
from app.services.astro_service import calculate_birth_chart
from app.translations import SUPPORTED_LANGUAGES
from app.utils.chart_data_accessor import is_language_first_format, validate_language_data


def is_new_format(chart_data: dict[str, Any] | None) -> bool:
    """Check if chart_data is already in the new language-keyed format."""
    if not chart_data:
        return False
    # Use the utility function for consistent detection
    return is_language_first_format(chart_data)


async def migrate_birth_chart(chart: BirthChart, dry_run: bool = False) -> bool:
    """Migrate a single BirthChart to the new language-keyed format."""
    if not chart.chart_data:
        logger.warning(f"BirthChart {chart.id} has no chart_data, skipping")
        return False

    if is_new_format(chart.chart_data):
        logger.info(f"BirthChart {chart.id} already in new format, skipping")
        return False

    logger.info(f"Migrating BirthChart {chart.id} ({chart.person_name})")

    if dry_run:
        logger.info(f"[DRY RUN] Would regenerate chart data for BirthChart {chart.id}")
        return True

    try:
        # Regenerate chart data for all supported languages
        chart_data_by_lang: dict[str, Any] = {}
        for language in SUPPORTED_LANGUAGES:
            logger.debug(f"Calculating {language} chart data for BirthChart {chart.id}")
            chart_data_by_lang[language] = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system,
                language=language,
            )

        # Validate the new data before saving
        for language in SUPPORTED_LANGUAGES:
            valid, error = validate_language_data(chart_data_by_lang, language)
            if not valid:
                logger.error(f"Validation failed for {language}: {error}")
                return False

        # Update the chart with new format
        chart.chart_data = chart_data_by_lang
        logger.info(f"✓ Successfully migrated BirthChart {chart.id}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to migrate BirthChart {chart.id}: {e}")
        return False


async def migrate_public_chart(chart: PublicChart, dry_run: bool = False) -> bool:
    """Migrate a single PublicChart to the new language-keyed format."""
    if not chart.chart_data:
        logger.warning(f"PublicChart {chart.slug} has no chart_data, skipping")
        return False

    if is_new_format(chart.chart_data):
        logger.info(f"PublicChart {chart.slug} already in new format, skipping")
        return False

    logger.info(f"Migrating PublicChart {chart.slug} ({chart.full_name})")

    if dry_run:
        logger.info(f"[DRY RUN] Would regenerate chart data for PublicChart {chart.slug}")
        return True

    try:
        # Regenerate chart data for all supported languages
        chart_data_by_lang: dict[str, Any] = {}
        for language in SUPPORTED_LANGUAGES:
            logger.debug(f"Calculating {language} chart data for PublicChart {chart.slug}")
            chart_data_by_lang[language] = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system or "placidus",
                language=language,
            )

        # Validate the new data before saving
        for language in SUPPORTED_LANGUAGES:
            valid, error = validate_language_data(chart_data_by_lang, language)
            if not valid:
                logger.error(f"Validation failed for {language}: {error}")
                return False

        # Update the chart with new format
        chart.chart_data = chart_data_by_lang
        logger.info(f"✓ Successfully migrated PublicChart {chart.slug}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to migrate PublicChart {chart.slug}: {e}")
        return False


async def main(
    dry_run: bool = False,
    chart_id: str | None = None,
    public_only: bool = False,
) -> None:
    """Main migration function."""
    start_time = datetime.now(UTC)

    logger.info("=" * 70)
    logger.info("Chart Data Migration to Language-Keyed Format")
    logger.info("=" * 70)
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    logger.info(f"Scope: {'Public charts only' if public_only else 'All charts'}")
    if chart_id:
        logger.info(f"Target: Specific chart {chart_id}")
    logger.info("")

    async with AsyncSessionLocal() as db:
        migrated = 0
        skipped = 0
        failed = 0

        # Migrate BirthCharts (unless public_only)
        if not public_only:
            query = select(BirthChart).where(
                BirthChart.status == "completed",
                BirthChart.chart_data.isnot(None),
                BirthChart.deleted_at.is_(None),
            )

            if chart_id:
                query = query.where(BirthChart.id == UUID(chart_id))

            result = await db.execute(query)
            birth_charts = result.scalars().all()

            logger.info(f"Found {len(birth_charts)} BirthCharts to check")

            for idx, chart in enumerate(birth_charts, 1):
                progress = f"[{idx}/{len(birth_charts)}]"
                try:
                    logger.info(f"{progress} Processing BirthChart {chart.id}...")
                    if await migrate_birth_chart(chart, dry_run):
                        migrated += 1
                    else:
                        skipped += 1
                except Exception as e:
                    logger.error(f"{progress} Error processing BirthChart {chart.id}: {e}")
                    failed += 1

        # Migrate PublicCharts
        public_query = select(PublicChart).where(
            PublicChart.chart_data.isnot(None),
        )

        result = await db.execute(public_query)
        public_charts = result.scalars().all()

        logger.info(f"\nFound {len(public_charts)} PublicCharts to check")

        for idx, chart in enumerate(public_charts, 1):
            progress = f"[{idx}/{len(public_charts)}]"
            try:
                logger.info(f"{progress} Processing PublicChart {chart.slug}...")
                if await migrate_public_chart(chart, dry_run):
                    migrated += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"{progress} Error processing PublicChart {chart.slug}: {e}")
                failed += 1

        if not dry_run and migrated > 0:
            logger.info("\nCommitting changes to database...")
            await db.commit()
            logger.info("✓ Changes committed successfully")

        # Summary
        elapsed = (datetime.now(UTC) - start_time).total_seconds()

        logger.info("")
        logger.info("=" * 70)
        logger.info("Migration Summary")
        logger.info("=" * 70)
        logger.info(f"Total charts processed: {migrated + skipped + failed}")
        logger.info(f"  ✓ Migrated: {migrated}")
        logger.info(f"  ⊘ Skipped (already migrated): {skipped}")
        logger.info(f"  ✗ Failed: {failed}")
        logger.info(f"\nElapsed time: {elapsed:.2f} seconds")

        if dry_run:
            logger.info("\n[DRY RUN] No changes were made to the database")
        elif migrated > 0:
            logger.info(f"\n✅ Successfully migrated {migrated} charts to language-first format")
        else:
            logger.info("\nℹ️  No charts needed migration")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate chart data to language-keyed format")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--chart-id",
        type=str,
        help="Migrate a specific BirthChart by UUID",
    )
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Migrate only PublicCharts (skip BirthCharts)",
    )

    args = parser.parse_args()

    asyncio.run(main(dry_run=args.dry_run, chart_id=args.chart_id, public_only=args.public_only))
