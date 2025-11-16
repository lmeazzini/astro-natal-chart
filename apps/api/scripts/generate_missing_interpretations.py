#!/usr/bin/env python3
"""
Script to generate interpretations for all charts that don't have them yet.

This script:
1. Connects to the database
2. Finds all charts without interpretations
3. Generates interpretations for each chart using the InterpretationService
4. Logs progress and errors

Usage:
    python scripts/generate_missing_interpretations.py [--limit N] [--dry-run]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Module imports must come after sys.path modification
from loguru import logger  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.repositories.chart_repository import ChartRepository  # noqa: E402
from app.services.interpretation_service import InterpretationService  # noqa: E402


async def generate_missing_interpretations(
    limit: int | None = None,
    dry_run: bool = False,
) -> None:
    """
    Generate interpretations for all charts without them.

    Args:
        limit: Maximum number of charts to process (None for all)
        dry_run: If True, only show what would be done without actually doing it
    """
    # Create async engine and session
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        chart_repo = ChartRepository(session)

        # Get charts without interpretations
        logger.info("Finding charts without interpretations...")
        charts = await chart_repo.get_charts_without_interpretations(
            skip=0,
            limit=limit if limit else 10000,  # Large default if no limit specified
        )

        logger.info(f"Found {len(charts)} charts without interpretations")

        if dry_run:
            logger.info("DRY RUN - No interpretations will be generated")
            for i, chart in enumerate(charts, 1):
                logger.info(
                    f"  [{i}/{len(charts)}] Would generate for: {chart.person_name} "
                    f"(ID: {chart.id}, Created: {chart.created_at})"
                )
            return

        # Process each chart
        success_count = 0
        error_count = 0

        for i, chart in enumerate(charts, 1):
            try:
                logger.info(
                    f"[{i}/{len(charts)}] Generating interpretations for: {chart.person_name} "
                    f"(ID: {chart.id})"
                )

                # Create interpretation service
                interp_service = InterpretationService(session)

                # Generate all interpretations
                interpretations = await interp_service.generate_all_interpretations(
                    chart_id=chart.id,
                    chart_data=chart.chart_data,
                )

                logger.success(
                    f"  ✓ Generated {len(interpretations)} interpretations for {chart.person_name}"
                )
                success_count += 1

            except Exception as e:
                logger.error(f"  ✗ Error generating interpretations for {chart.person_name}: {e}")
                error_count += 1
                continue

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total charts processed: {len(charts)}")
    logger.success(f"Successfully generated: {success_count}")
    if error_count > 0:
        logger.error(f"Errors: {error_count}")
    logger.info("=" * 70)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Generate interpretations for charts that don't have them yet"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of charts to process (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )

    args = parser.parse_args()

    # Configure logger
    logger.remove()  # Remove default handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )

    # Run async function
    try:
        asyncio.run(generate_missing_interpretations(limit=args.limit, dry_run=args.dry_run))
    except KeyboardInterrupt:
        logger.warning("\nScript interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
