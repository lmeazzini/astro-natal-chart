#!/usr/bin/env python3
"""
Backfill missing language interpretations for existing charts.

This script finds charts that have interpretations in only one language
and generates missing interpretations for the other language.

Supported languages:
- pt-BR (Portuguese - Brazil)
- en-US (English - United States)

The script will:
1. Find charts with completed chart_data
2. For each chart, detect which languages have interpretations
3. Generate missing interpretations for languages that don't exist
4. Use the cache system to avoid duplicate generations

Usage:
    # Dry run (shows what would be backfilled)
    python scripts/backfill_missing_language_interpretations.py --dry-run

    # Actual backfill (with progress tracking)
    python scripts/backfill_missing_language_interpretations.py

    # Backfill specific chart by ID
    python scripts/backfill_missing_language_interpretations.py --chart-id <uuid>

    # Limit number of charts to process
    python scripts/backfill_missing_language_interpretations.py --limit 10
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
from app.services.interpretation_service_rag import InterpretationServiceRAG

# Languages we support
SUPPORTED_LANGUAGES = ["pt-BR", "en-US"]

# Interpretation types we expect
EXPECTED_TYPES = ["planet", "house", "aspect"]


async def count_charts_needing_backfill(db: AsyncSession) -> dict[str, int]:
    """
    Count how many charts need backfilling per language.

    Returns:
        Dict with language codes and count of charts missing that language
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

    needs_backfill = dict.fromkeys(SUPPORTED_LANGUAGES, 0)

    for chart in all_charts:
        # Get existing interpretations for this chart
        interp_stmt = (
            select(ChartInterpretation.language)
            .where(ChartInterpretation.chart_id == chart.id)
            .distinct()
        )
        interp_result = await db.execute(interp_stmt)
        existing_languages = {row[0] for row in interp_result.fetchall()}

        # Count which languages are missing
        for lang in SUPPORTED_LANGUAGES:
            if lang not in existing_languages:
                needs_backfill[lang] += 1

    return needs_backfill


async def get_charts_needing_backfill(
    db: AsyncSession,
    chart_id: UUID | None = None,
    limit: int | None = None,
) -> list[tuple[BirthChart, set[str]]]:
    """
    Get charts that need language backfilling.

    Args:
        db: Database session
        chart_id: Optional specific chart ID to backfill
        limit: Optional limit on number of charts to process

    Returns:
        List of tuples: (chart, set of missing language codes)
    """
    # Build query for charts with chart_data
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
        # Get existing interpretations for this chart
        interp_stmt = (
            select(ChartInterpretation.language)
            .where(ChartInterpretation.chart_id == chart.id)
            .distinct()
        )
        interp_result = await db.execute(interp_stmt)
        existing_languages = {row[0] for row in interp_result.fetchall()}

        # Find missing languages
        missing_languages = set(SUPPORTED_LANGUAGES) - existing_languages

        if missing_languages:
            charts_to_backfill.append((chart, missing_languages))

    return charts_to_backfill


async def backfill_chart_interpretations(
    db: AsyncSession,
    chart: BirthChart,
    languages_to_generate: set[str],
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Generate missing language interpretations for a chart.

    Args:
        db: Database session
        chart: Birth chart to backfill
        languages_to_generate: Set of language codes to generate
        dry_run: If True, don't actually generate

    Returns:
        Dict with counts of interpretations generated per language
    """
    results = dict.fromkeys(languages_to_generate, 0)

    if dry_run:
        logger.info(
            f"[DRY RUN] Would backfill {languages_to_generate} for chart {chart.id} "
            f"({chart.person_name})"
        )
        # In dry run, just estimate based on chart data
        for lang in languages_to_generate:
            # Rough estimate: 11 planets + 12 houses + ~15 aspects = ~38
            results[lang] = 38
        return results

    logger.info(f"Backfilling {languages_to_generate} for chart {chart.id} ({chart.person_name})")

    for language in languages_to_generate:
        # Create RAG service with cache enabled
        rag_service = InterpretationServiceRAG(
            db=db,
            use_cache=True,
            use_rag=True,
            language=language,
        )

        # Generate all interpretations
        interpretations = await rag_service.generate_all_rag_interpretations(
            chart=chart,
            chart_data=chart.chart_data,
        )

        # Count generated interpretations
        count = sum(
            len(interps)
            for key, interps in interpretations.items()
            if key in ["planets", "houses", "aspects"]
        )

        results[language] = count
        logger.info(f"  ✓ Generated {count} {language} interpretations")

    # Commit all changes
    await db.commit()
    logger.success(f"Successfully backfilled chart {chart.id}")

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
    logger.info("Chart Interpretations Language Backfill Script")
    logger.info("=" * 70)

    if dry_run:
        logger.warning("[DRY RUN MODE] No interpretations will be generated")
    else:
        logger.warning("[LIVE MODE] Missing language interpretations will be GENERATED")

    # Parse chart ID if provided
    parsed_chart_id = None
    if chart_id:
        try:
            parsed_chart_id = UUID(chart_id)
            logger.info(f"Processing specific chart: {parsed_chart_id}")
        except ValueError:
            logger.error(f"Invalid chart ID format: {chart_id}")
            return

    async with AsyncSessionLocal() as db:
        # Step 1: Count charts needing backfill
        logger.info("Analyzing charts...")
        needs_backfill = await count_charts_needing_backfill(db)

        logger.info("\nCharts missing interpretations by language:")
        for lang, count in needs_backfill.items():
            logger.info(f"  • {lang}: {count} charts")

        total_missing = sum(needs_backfill.values())
        if total_missing == 0:
            logger.success("No charts need backfilling! All charts have all languages.")
            return

        # Step 2: Get charts to process
        charts_to_process = await get_charts_needing_backfill(
            db, chart_id=parsed_chart_id, limit=limit
        )

        if not charts_to_process:
            logger.success("No charts to process with current filters.")
            return

        logger.info(f"\nFound {len(charts_to_process)} chart(s) to process")

        if verbose or dry_run:
            logger.info("\nCharts requiring backfill:")
            for i, (chart, missing_langs) in enumerate(charts_to_process, 1):
                logger.info(
                    f"  {i}. {chart.person_name} ({chart.id}): "
                    f"missing {', '.join(sorted(missing_langs))}"
                )

        # Step 3: Process each chart
        logger.info("")
        total_generated = dict.fromkeys(SUPPORTED_LANGUAGES, 0)
        processed_count = 0
        failed_count = 0

        for i, (chart, missing_langs) in enumerate(charts_to_process, 1):
            try:
                logger.info(
                    f"[{i}/{len(charts_to_process)}] Processing {chart.person_name} ({chart.id})..."
                )

                results = await backfill_chart_interpretations(
                    db=db,
                    chart=chart,
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

        # Step 4: Summary
        logger.info("")
        logger.info("=" * 70)
        logger.info("Backfill Summary")
        logger.info("=" * 70)
        logger.info(f"Charts processed: {processed_count}/{len(charts_to_process)}")
        logger.info(f"Failed: {failed_count}")

        logger.info("\nInterpretations generated by language:")
        for lang in SUPPORTED_LANGUAGES:
            count = total_generated[lang]
            if count > 0:
                logger.info(f"  • {lang}: {count} interpretations")

        if failed_count > 0:
            logger.warning(f"\n⚠️  {failed_count} chart(s) failed to process")
        else:
            logger.success("\n✅ All charts processed successfully!")

    elapsed = (datetime.now(UTC) - start_time).total_seconds()
    logger.info(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill missing language interpretations for existing charts"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be backfilled without actually generating",
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
        help="Show detailed information about charts",
    )

    args = parser.parse_args()

    # Run backfill
    asyncio.run(
        main(
            dry_run=args.dry_run,
            chart_id=args.chart_id,
            limit=args.limit,
            verbose=args.verbose,
        )
    )
