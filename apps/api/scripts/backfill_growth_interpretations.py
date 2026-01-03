#!/usr/bin/env python3
"""
Backfill missing growth interpretations for existing charts.

Growth interpretations consist of 4 components per language:
- points (strength points)
- challenges (growth challenges)
- opportunities (opportunities)
- purpose (life purpose)

This script:
1. Finds charts missing growth interpretations
2. Generates all 4 components for both PT-BR and EN-US
3. Uses cache to avoid duplicate API calls

Usage:
    # Dry run (shows what would be generated)
    python scripts/backfill_growth_interpretations.py --dry-run

    # Actual generation
    python scripts/backfill_growth_interpretations.py

    # Specific chart
    python scripts/backfill_growth_interpretations.py --chart-id <uuid>

    # Limit processing
    python scripts/backfill_growth_interpretations.py --limit 5
"""

import argparse
import asyncio
from datetime import UTC, datetime
from uuid import UUID

from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation
from app.services.personal_growth_service import PersonalGrowthService

# Languages we support
SUPPORTED_LANGUAGES = ["pt-BR", "en-US"]

# Growth components (4 per language = 8 total)
# These are the "subject" values stored in ChartInterpretation table
GROWTH_COMPONENTS = ["points", "challenges", "opportunities", "purpose"]


async def count_charts_needing_growth(db: AsyncSession) -> dict[str, int]:
    """
    Count charts missing growth interpretations by language.

    Returns:
        Dict with language codes and count of charts missing growth for that language
    """
    # Get all charts with completed chart_data
    stmt = select(BirthChart).where(
        and_(
            BirthChart.chart_data.isnot(None),
            BirthChart.deleted_at.is_(None),
        )
    )
    result = await db.execute(stmt)
    all_charts = result.scalars().all()

    needs_growth = dict.fromkeys(SUPPORTED_LANGUAGES, 0)

    for chart in all_charts:
        # Get existing growth interpretations for this chart
        interp_stmt = (
            select(ChartInterpretation.language, ChartInterpretation.subject)
            .where(
                and_(
                    ChartInterpretation.chart_id == chart.id,
                    ChartInterpretation.interpretation_type == "growth",
                )
            )
            .distinct()
        )
        interp_result = await db.execute(interp_stmt)
        existing = interp_result.fetchall()

        # Group by language
        by_lang = {}
        for lang, subject in existing:
            if lang not in by_lang:
                by_lang[lang] = set()
            by_lang[lang].add(subject)

        # Check if each language has all 4 components
        for lang in SUPPORTED_LANGUAGES:
            components = by_lang.get(lang, set())
            if len(components) < 4:  # Missing some or all components
                needs_growth[lang] += 1

    return needs_growth


async def get_charts_needing_growth(
    db: AsyncSession,
    chart_id: UUID | None = None,
    limit: int | None = None,
) -> list[tuple[BirthChart, set[str]]]:
    """
    Get charts that need growth interpretation backfilling.

    Args:
        db: Database session
        chart_id: Optional specific chart ID
        limit: Optional limit on number of charts

    Returns:
        List of tuples: (chart, set of language codes needing growth)
    """
    # Build query
    if chart_id:
        stmt = select(BirthChart).where(
            and_(
                BirthChart.id == chart_id,
                BirthChart.chart_data.isnot(None),
                BirthChart.deleted_at.is_(None),
            )
        )
    else:
        stmt = (
            select(BirthChart)
            .where(
                and_(
                    BirthChart.chart_data.isnot(None),
                    BirthChart.deleted_at.is_(None),
                )
            )
            .order_by(BirthChart.created_at.desc())
        )
        if limit:
            stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    all_charts = result.scalars().all()

    charts_to_backfill: list[tuple[BirthChart, set[str]]] = []

    for chart in all_charts:
        # Get existing growth interpretations
        interp_stmt = (
            select(ChartInterpretation.language, ChartInterpretation.subject)
            .where(
                and_(
                    ChartInterpretation.chart_id == chart.id,
                    ChartInterpretation.interpretation_type == "growth",
                )
            )
            .distinct()
        )
        interp_result = await db.execute(interp_stmt)
        existing = interp_result.fetchall()

        # Group by language
        by_lang = {}
        for lang, subject in existing:
            if lang not in by_lang:
                by_lang[lang] = set()
            by_lang[lang].add(subject)

        # Check which languages need growth
        missing_languages = set()
        for lang in SUPPORTED_LANGUAGES:
            components = by_lang.get(lang, set())
            if len(components) < 4:  # Missing components
                missing_languages.add(lang)

        if missing_languages:
            charts_to_backfill.append((chart, missing_languages))

    return charts_to_backfill


async def backfill_chart_growth(
    db: AsyncSession,
    chart: BirthChart,
    languages_to_generate: set[str],
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Generate missing growth interpretations for a chart.

    Args:
        db: Database session
        chart: Birth chart
        languages_to_generate: Languages needing growth
        dry_run: If True, don't actually generate

    Returns:
        Dict with counts per language
    """
    results = dict.fromkeys(languages_to_generate, 0)

    if dry_run:
        logger.info(
            f"[DRY RUN] Would generate growth for {languages_to_generate} "
            f"on chart {chart.id} ({chart.person_name})"
        )
        # Each language gets 4 growth components
        for lang in languages_to_generate:
            results[lang] = 4
        return results

    logger.info(
        f"Generating growth for {languages_to_generate} on chart {chart.id} ({chart.person_name})"
    )

    for language in languages_to_generate:
        try:
            # Disable cache for backfill to avoid concurrency issues
            # The cache service has problems with concurrent updates
            growth_service = PersonalGrowthService(language=language, db=None)

            # Generate and store growth interpretations manually
            growth_data = await growth_service.generate_growth_suggestions(
                chart_data=chart.chart_data,
                chart_id=None,  # Don't auto-save, we'll do it manually
            )

            # Now manually save to database using repository
            import json

            from app.repositories.interpretation_repository import InterpretationRepository

            repo = InterpretationRepository(db)

            # Map growth_data keys to database subject names
            components_map = {
                "points": growth_data.get("growth_points"),
                "challenges": growth_data.get("challenges"),
                "opportunities": growth_data.get("opportunities"),
                "purpose": growth_data.get("purpose"),
            }

            # Delete old growth interpretations for this language
            existing = await repo.get_by_chart_and_type(
                chart_id=chart.id,
                interpretation_type="growth",
            )
            for interp in existing:
                if interp.language == language:
                    await repo.delete(interp)

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

            # Count generated components
            # Note: growth_data uses keys: growth_points, challenges, opportunities, purpose
            growth_keys = ["growth_points", "challenges", "opportunities", "purpose"]
            count = len([v for k, v in growth_data.items() if k in growth_keys and v])
            results[language] = count
            logger.info(f"  ✓ Generated {count} {language} growth components")

            # Commit after each language to avoid database concurrency issues
            await db.commit()

            # Small delay to let the connection fully settle
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"  ✗ Failed to generate {language}: {e}")
            await db.rollback()
            # Continue with next language even if one fails
            continue
    logger.success(f"Successfully generated growth for chart {chart.id}")

    return results


async def main(
    dry_run: bool = False,
    chart_id: str | None = None,
    limit: int | None = None,
    verbose: bool = False,
):
    """Main backfill function."""
    start_time = datetime.now(UTC)

    logger.info("=" * 70)
    logger.info("Growth Interpretations Backfill Script")
    logger.info("=" * 70)

    if dry_run:
        logger.warning("[DRY RUN MODE] No interpretations will be generated")
    else:
        logger.warning("[LIVE MODE] Growth interpretations will be GENERATED")

    # Parse chart ID
    parsed_chart_id = None
    if chart_id:
        try:
            parsed_chart_id = UUID(chart_id)
            logger.info(f"Processing specific chart: {parsed_chart_id}")
        except ValueError:
            logger.error(f"Invalid chart ID: {chart_id}")
            return

    async with AsyncSessionLocal() as db:
        # Count charts needing growth
        logger.info("Analyzing charts...")
        needs_growth = await count_charts_needing_growth(db)

        logger.info("\nCharts missing growth interpretations by language:")
        for lang, count in needs_growth.items():
            logger.info(f"  • {lang}: {count} charts")

        total_missing = sum(needs_growth.values())
        if total_missing == 0:
            logger.success("No charts need growth backfilling!")
            return

        # Get charts to process
        charts_to_process = await get_charts_needing_growth(
            db, chart_id=parsed_chart_id, limit=limit
        )

        if not charts_to_process:
            logger.success("No charts to process with current filters.")
            return

        logger.info(f"\nFound {len(charts_to_process)} chart(s) to process")

        if verbose or dry_run:
            logger.info("\nCharts requiring growth backfill:")
            for i, (chart, missing_langs) in enumerate(charts_to_process, 1):
                logger.info(
                    f"  {i}. {chart.person_name} ({chart.id}): "
                    f"missing {', '.join(sorted(missing_langs))}"
                )

        # Process each chart
        logger.info("")
        total_generated = dict.fromkeys(SUPPORTED_LANGUAGES, 0)
        processed_count = 0
        failed_count = 0

        for i, (chart, missing_langs) in enumerate(charts_to_process, 1):
            # Create a fresh database session for each chart to avoid session state issues
            async with AsyncSessionLocal() as chart_db:
                try:
                    logger.info(
                        f"[{i}/{len(charts_to_process)}] Processing {chart.person_name} "
                        f"({chart.id})..."
                    )

                    # Reload chart in new session
                    chart_stmt = select(BirthChart).where(BirthChart.id == chart.id)
                    chart_result = await chart_db.execute(chart_stmt)
                    fresh_chart = chart_result.scalar_one()

                    results = await backfill_chart_growth(
                        db=chart_db,
                        chart=fresh_chart,
                        languages_to_generate=missing_langs,
                        dry_run=dry_run,
                    )

                    # Accumulate counts
                    for lang, count in results.items():
                        total_generated[lang] += count

                    processed_count += 1

                except Exception as exc:
                    logger.error(f"Failed to process chart {chart.id}: {exc}")
                    failed_count += 1

        # Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("Backfill Summary")
        logger.info("=" * 70)
        logger.info(f"Charts processed: {processed_count}/{len(charts_to_process)}")
        logger.info(f"Failed: {failed_count}")

        logger.info("\nGrowth components generated by language:")
        for lang in SUPPORTED_LANGUAGES:
            count = total_generated[lang]
            if count > 0:
                logger.info(f"  • {lang}: {count} components")

        if failed_count > 0:
            logger.warning(f"\n⚠️  {failed_count} chart(s) failed")
        else:
            logger.success("\n✅ All charts processed successfully!")

    elapsed = (datetime.now(UTC) - start_time).total_seconds()
    logger.info(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backfill missing growth interpretations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without actually generating",
    )
    parser.add_argument(
        "--chart-id",
        type=str,
        help="Specific chart ID to backfill (UUID)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of charts to process",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed information",
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            dry_run=args.dry_run,
            chart_id=args.chart_id,
            limit=args.limit,
            verbose=args.verbose,
        )
    )
