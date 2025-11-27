#!/usr/bin/env python3
"""
Identify Charts Missing Growth Interpretations

This script identifies charts that don't have growth interpretations
in the chart_interpretations table.

Since the InterpretationCache table doesn't store chart_id, we can't
directly migrate growth data. Instead, this script identifies which
charts need growth regeneration.

Usage:
    cd apps/api
    uv run python ../../scripts/identify_charts_missing_growth.py

Options:
    --output FILE: Save chart IDs to file (one per line)
    --limit N: Only check first N charts
"""

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import UUID

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Import all models to ensure relationships are configured
from app.core.database import Base  # noqa: F401
from app.models import chart, interpretation, subscription, user  # noqa: F401

from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation


async def check_chart_has_growth(db: AsyncSession, chart_id: UUID) -> bool:
    """
    Check if a chart has growth interpretations.

    Args:
        db: Database session
        chart_id: Chart UUID

    Returns:
        True if growth interpretations exist
    """
    stmt = select(ChartInterpretation).where(
        ChartInterpretation.chart_id == chart_id,
        ChartInterpretation.interpretation_type.like("growth_%"),
    )
    result = await db.execute(stmt)
    return result.first() is not None


async def get_all_charts(
    db: AsyncSession,
    limit: int | None = None,
) -> list[tuple[UUID, str]]:
    """
    Get all charts in the database.

    Args:
        db: Database session
        limit: Optional limit on number of charts

    Returns:
        List of (chart_id, person_name) tuples
    """
    stmt = select(BirthChart.id, BirthChart.person_name).where(
        BirthChart.deleted_at.is_(None)
    )

    if limit:
        stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    return [(row[0], row[1]) for row in result.all()]


async def identify_missing_growth(
    limit: int | None = None,
    output_file: str | None = None,
):
    """
    Main identification function.

    Args:
        limit: Optional limit on number of charts to check
        output_file: Optional file to save chart IDs
    """
    # Create async engine
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as db:
        # Get all charts
        logger.info("Fetching charts from database...")
        charts = await get_all_charts(db, limit)
        logger.info(f"Found {len(charts)} charts to check")

        if not charts:
            logger.info("No charts found in database")
            return

        # Check each chart for growth interpretations
        charts_with_growth = []
        charts_without_growth = []

        for i, (chart_id, person_name) in enumerate(charts, 1):
            logger.info(f"Checking chart {i}/{len(charts)}: {person_name} ({chart_id})")

            has_growth = await check_chart_has_growth(db, chart_id)

            if has_growth:
                charts_with_growth.append((chart_id, person_name))
                logger.debug(f"  ✓ Has growth interpretations")
            else:
                charts_without_growth.append((chart_id, person_name))
                logger.warning(f"  ✗ Missing growth interpretations")

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total charts checked: {len(charts)}")
        logger.info(f"Charts with growth: {len(charts_with_growth)}")
        logger.info(f"Charts WITHOUT growth: {len(charts_without_growth)}")

        if charts_without_growth:
            logger.warning(f"\n{len(charts_without_growth)} charts need growth regeneration:")
            for chart_id, person_name in charts_without_growth[:10]:  # Show first 10
                logger.warning(f"  - {person_name} ({chart_id})")

            if len(charts_without_growth) > 10:
                logger.warning(f"  ... and {len(charts_without_growth) - 10} more")

            # Save to file if requested
            if output_file:
                output_path = Path(output_file)
                with output_path.open("w") as f:
                    for chart_id, _ in charts_without_growth:
                        f.write(f"{chart_id}\n")
                logger.success(f"\nChart IDs saved to: {output_file}")
                logger.info(f"Total IDs written: {len(charts_without_growth)}")

            logger.info("\nTo regenerate growth for these charts, users can:")
            logger.info("1. Open each chart detail page")
            logger.info("2. Navigate to the 'Growth' tab")
            logger.info("3. Click 'Generate Suggestions' button")
            logger.info("\nOr use the API endpoint:")
            logger.info("  GET /api/v1/charts/{chart_id}/interpretations?regenerate=growth")

        else:
            logger.success("\n✓ All charts have growth interpretations!")

    await engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description="Identify charts missing growth interpretations"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Only check first N charts",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save chart IDs to file (one per line)",
    )

    args = parser.parse_args()

    # Configure logger
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
    )

    # Run identification
    logger.info("Identifying charts missing growth interpretations...")
    asyncio.run(identify_missing_growth(
        limit=args.limit,
        output_file=args.output,
    ))


if __name__ == "__main__":
    main()
