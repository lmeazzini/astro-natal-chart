#!/usr/bin/env python3
"""
Populate growth interpretations for public charts.

Each chart gets 8 growth interpretations total (4 per language):
- points (strength points)
- challenges (growth challenges)
- opportunities (opportunities)
- purpose (life purpose)

Languages: PT-BR and EN-US

Usage:
    # Generate all missing interpretations
    python scripts/populate_public_growth.py

    # Clear existing and regenerate all
    python scripts/populate_public_growth.py --clear

    # Process specific chart
    python scripts/populate_public_growth.py --chart-id <uuid>
"""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.public_chart import PublicChart
from app.models.public_chart_interpretation import PublicChartInterpretation
from app.repositories.public_interpretation_repository import PublicInterpretationRepository
from app.services.personal_growth_service import PersonalGrowthService

# Supported languages
LANGUAGES = ["pt-BR", "en-US"]


async def clear_chart_growth(
    db: AsyncSession,
    chart_id: UUID,
) -> int:
    """Delete all existing growth interpretations for a chart."""
    stmt = delete(PublicChartInterpretation).where(
        PublicChartInterpretation.chart_id == chart_id,
        PublicChartInterpretation.interpretation_type == "growth",
    )
    result = await db.execute(stmt)
    count = result.rowcount or 0
    await db.commit()
    return count


async def generate_growth(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    repo: PublicInterpretationRepository,
) -> int:
    """Generate growth interpretations (4 components)."""
    # Get language-specific chart data
    lang_data = chart.chart_data.get(language, {})

    if not lang_data:
        logger.warning(f"No chart data found for language '{language}' in {chart.full_name}")
        return 0

    count = 0
    growth_service = PersonalGrowthService(language=language, db=None)

    try:
        # Generate all 4 growth components at once
        growth_data = await growth_service.generate_growth_suggestions(
            chart_data=lang_data,  # Pass language-specific data
            chart_id=None,  # Don't auto-save
        )

        # Map growth_data keys to database subject names
        components_map = {
            "points": growth_data.get("growth_points"),
            "challenges": growth_data.get("challenges"),
            "opportunities": growth_data.get("opportunities"),
            "purpose": growth_data.get("purpose"),
        }

        # Save each component
        for subject, content_data in components_map.items():
            if content_data:
                await repo.upsert_interpretation(
                    chart_id=chart.id,
                    interpretation_type="growth",
                    subject=subject,
                    content=json.dumps(content_data, ensure_ascii=False),
                    language=language,
                    openai_model="gpt-4o-mini",
                    prompt_version="1.0.0",
                )
                count += 1

        await db.commit()

    except Exception as e:
        logger.error(f"Failed to generate growth interpretations for {language}: {e}")
        await db.rollback()

    return count


async def process_chart(
    chart_id: UUID,
    clear: bool = False,
) -> dict[str, int]:
    """Process a single chart and generate growth interpretations."""
    async with AsyncSessionLocal() as db:
        # Fetch chart
        stmt = select(PublicChart).where(PublicChart.id == chart_id)
        result = await db.execute(stmt)
        chart = result.scalar_one_or_none()

        if not chart:
            logger.error(f"Chart {chart_id} not found")
            return {}

        # Clear existing growth interpretations if requested
        if clear:
            deleted = await clear_chart_growth(db, chart.id)
            if deleted > 0:
                logger.info(f"  Deleted {deleted} existing growth interpretations")

        # Generate growth interpretations for both languages
        repo = PublicInterpretationRepository(db)
        counts = {"pt-BR": 0, "en-US": 0}

        for language in LANGUAGES:
            count = await generate_growth(db, chart, language, repo)
            counts[language] = count

        total = sum(counts.values())
        logger.success(
            f"  {chart.full_name}: {total} growth interpretations "
            f"(PT-BR: {counts['pt-BR']}, EN-US: {counts['en-US']})"
        )

        return counts


async def main(
    chart_id: str | None = None,
    clear: bool = False,
):
    """Main function."""
    start_time = datetime.now(UTC)

    logger.info("=" * 70)
    logger.info("Public Chart Growth Interpretations Population Script")
    logger.info("=" * 70)

    if clear:
        logger.warning("[CLEAR MODE] Existing growth interpretations will be deleted")

    # Get charts to process
    async with AsyncSessionLocal() as db:
        if chart_id:
            try:
                parsed_id = UUID(chart_id)
                stmt = select(PublicChart).where(PublicChart.id == parsed_id)
            except ValueError:
                logger.error(f"Invalid chart ID: {chart_id}")
                return
        else:
            stmt = select(PublicChart).where(PublicChart.is_published)

        result = await db.execute(stmt)
        charts = result.scalars().all()

    if not charts:
        logger.warning("No charts found to process")
        return

    logger.info(f"\nProcessing {len(charts)} chart(s)...\n")

    # Process each chart
    success_count = 0
    fail_count = 0
    grand_total = {"pt-BR": 0, "en-US": 0}

    for i, chart in enumerate(charts, 1):
        try:
            logger.info(f"[{i}/{len(charts)}] {chart.full_name}")
            counts = await process_chart(
                chart_id=chart.id,
                clear=clear,
            )

            for lang, count in counts.items():
                grand_total[lang] += count

            success_count += 1

        except Exception as e:
            logger.error(f"Failed to process {chart.full_name}: {e}")
            fail_count += 1
            continue

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("Summary")
    logger.info("=" * 70)
    logger.info(f"Charts processed: {success_count}/{len(charts)}")
    logger.info(f"Failed: {fail_count}")
    logger.info("\nGrowth interpretations generated:")
    logger.info(f"  PT-BR: {grand_total['pt-BR']}")
    logger.info(f"  EN-US: {grand_total['en-US']}")
    logger.info(f"  TOTAL: {sum(grand_total.values())}")

    elapsed = (datetime.now(UTC) - start_time).total_seconds()
    logger.info(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate public chart growth interpretations")
    parser.add_argument(
        "--chart-id",
        type=str,
        help="Specific chart ID to process (UUID)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing growth interpretations before generating",
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            chart_id=args.chart_id,
            clear=args.clear,
        )
    )
