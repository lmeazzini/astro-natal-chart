#!/usr/bin/env python3
"""
Populate public chart interpretations for all published charts.

This script generates AI interpretations for public charts (famous people).
Each chart gets 100 interpretations total:
- 11 planets × 2 languages = 22
- 12 houses × 2 languages = 24
- ~10 aspects × 2 languages = 20
- 13 Arabic Parts × 2 languages = 26
- 4 growth components × 2 languages = 8
Total = 100 interpretations per chart

Usage:
    # Generate all missing interpretations
    python scripts/populate_public_interpretations.py

    # Clear existing and regenerate all
    python scripts/populate_public_interpretations.py --clear

    # Process specific chart
    python scripts/populate_public_interpretations.py --chart-id <uuid>

    # Dry run (show what would be done)
    python scripts/populate_public_interpretations.py --dry-run
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
from app.services.interpretation_service_rag import InterpretationServiceRAG
from app.services.personal_growth_service import PersonalGrowthService

# Supported languages
LANGUAGES = ["pt-BR", "en-US"]


async def clear_chart_interpretations(
    db: AsyncSession,
    chart_id: UUID,
) -> int:
    """
    Delete all existing interpretations for a chart.

    Args:
        db: Database session
        chart_id: Chart UUID

    Returns:
        Number of interpretations deleted
    """
    stmt = delete(PublicChartInterpretation).where(PublicChartInterpretation.chart_id == chart_id)
    result = await db.execute(stmt)
    count = result.rowcount or 0
    await db.commit()
    return count


async def generate_planet_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    repo: PublicInterpretationRepository,
) -> int:
    """Generate planet in sign interpretations."""
    # Get language-specific chart data
    lang_data = chart.chart_data.get(language, {})
    planets = lang_data.get("planets", [])

    if not planets:
        logger.warning(f"No planets found in chart_data['{language}'] for {chart.full_name}")
        return 0

    count = 0
    rag_service = InterpretationServiceRAG(db=db, language=language, use_cache=True)

    for planet in planets:
        planet_name = planet.get("name")
        sign = planet.get("sign")

        if not planet_name or not sign:
            continue

        try:
            # Generate interpretation
            content = await rag_service.generate_planet_interpretation(
                planet=planet_name,
                sign=sign,
            )

            if content:
                await repo.upsert_interpretation(
                    chart_id=chart.id,
                    interpretation_type="planet",
                    subject=planet_name,
                    content=content,
                    language=language,
                    openai_model="gpt-4o-mini",
                    prompt_version="1.0.0",
                )
                count += 1

        except Exception as e:
            logger.error(f"Failed to generate planet interpretation for {planet_name}: {e}")
            continue

    await db.commit()
    return count


async def generate_house_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    repo: PublicInterpretationRepository,
) -> int:
    """Generate house interpretations."""
    # Get language-specific chart data
    lang_data = chart.chart_data.get(language, {})
    houses = lang_data.get("houses", [])

    if not houses:
        logger.warning(f"No houses found in chart_data['{language}'] for {chart.full_name}")
        return 0

    count = 0
    rag_service = InterpretationServiceRAG(db=db, language=language, use_cache=True)

    for house in houses:
        house_number = house.get("house")
        sign = house.get("sign")

        if house_number is None or not sign:
            continue

        try:
            # Generate interpretation
            content = await rag_service.generate_house_interpretation(
                house=str(house_number),
                sign=sign,
            )

            if content:
                await repo.upsert_interpretation(
                    chart_id=chart.id,
                    interpretation_type="house",
                    subject=str(house_number),
                    content=content,
                    language=language,
                    openai_model="gpt-4o-mini",
                    prompt_version="1.0.0",
                )
                count += 1

        except Exception as e:
            logger.error(f"Failed to generate house interpretation for house {house_number}: {e}")
            continue

    await db.commit()
    return count


async def generate_aspect_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    repo: PublicInterpretationRepository,
) -> int:
    """Generate aspect interpretations."""
    # Get language-specific chart data
    lang_data = chart.chart_data.get(language, {})
    aspects = lang_data.get("aspects", [])

    if not aspects:
        logger.warning(f"No aspects found in chart_data['{language}'] for {chart.full_name}")
        return 0

    count = 0
    rag_service = InterpretationServiceRAG(db=db, language=language, use_cache=True)

    for aspect in aspects:
        planet1 = aspect.get("planet1")
        planet2 = aspect.get("planet2")
        aspect_type = aspect.get("aspect")

        if not planet1 or not planet2 or not aspect_type:
            continue

        # Create subject identifier (e.g., "Sun-Trine-Moon")
        subject = f"{planet1}-{aspect_type.title()}-{planet2}"

        try:
            # Generate interpretation
            content = await rag_service.generate_aspect_interpretation(
                planet1=planet1,
                planet2=planet2,
                aspect=aspect_type,
            )

            if content:
                await repo.upsert_interpretation(
                    chart_id=chart.id,
                    interpretation_type="aspect",
                    subject=subject,
                    content=content,
                    language=language,
                    openai_model="gpt-4o-mini",
                    prompt_version="1.0.0",
                )
                count += 1

        except Exception as e:
            logger.error(f"Failed to generate aspect interpretation for {subject}: {e}")
            continue

    await db.commit()
    return count


async def generate_arabic_parts_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    repo: PublicInterpretationRepository,
) -> int:
    """Generate Arabic Parts interpretations."""
    # Get language-specific chart data
    lang_data = chart.chart_data.get(language, {})
    arabic_parts = lang_data.get("arabic_parts", {})

    if not arabic_parts:
        logger.warning(f"No Arabic Parts found in chart_data['{language}'] for {chart.full_name}")
        return 0

    count = 0
    rag_service = InterpretationServiceRAG(db=db, language=language, use_cache=True)

    # arabic_parts is a dict where keys are part names (eros, fortune, etc.)
    for part_name, part_data in arabic_parts.items():
        if not isinstance(part_data, dict):
            continue

        sign = part_data.get("sign")

        if not part_name or not sign:
            continue

        try:
            # Generate interpretation
            content = await rag_service.generate_arabic_part_interpretation(
                part_name=part_name,
                sign=sign,
            )

            if content:
                await repo.upsert_interpretation(
                    chart_id=chart.id,
                    interpretation_type="arabic_part",
                    subject=part_name,
                    content=content,
                    language=language,
                    openai_model="gpt-4o-mini",
                    prompt_version="1.0.0",
                )
                count += 1

        except Exception as e:
            logger.error(f"Failed to generate Arabic Part interpretation for {part_name}: {e}")
            continue

    await db.commit()
    return count


async def generate_growth_interpretations(
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
        logger.error(f"Failed to generate growth interpretations: {e}")
        await db.rollback()

    return count


async def process_chart(
    chart_id: UUID,
    clear: bool = False,
    dry_run: bool = False,
) -> dict[str, int]:
    """
    Process a single chart and generate all interpretations.

    Args:
        chart_id: Chart UUID
        clear: Whether to clear existing interpretations first
        dry_run: If True, don't actually generate anything

    Returns:
        Dict with counts by category
    """
    async with AsyncSessionLocal() as db:
        # Fetch chart
        stmt = select(PublicChart).where(PublicChart.id == chart_id)
        result = await db.execute(stmt)
        chart = result.scalar_one_or_none()

        if not chart:
            logger.error(f"Chart {chart_id} not found")
            return {}

        logger.info(f"Processing: {chart.full_name}")

        # Clear existing interpretations if requested
        if clear and not dry_run:
            deleted = await clear_chart_interpretations(db, chart.id)
            logger.info(f"  Deleted {deleted} existing interpretations")

        if dry_run:
            logger.info("  [DRY RUN] Would generate interpretations for both languages")
            return {
                "planets": 11 * 2,
                "houses": 12 * 2,
                "aspects": 10 * 2,
                "arabic_parts": 13 * 2,
                "growth": 4 * 2,
            }

        # Generate interpretations for both languages
        total_counts = {
            "planets": 0,
            "houses": 0,
            "aspects": 0,
            "arabic_parts": 0,
            "growth": 0,
        }

        repo = PublicInterpretationRepository(db)

        for language in LANGUAGES:
            logger.info(f"  Generating {language} interpretations...")

            # Planets
            count = await generate_planet_interpretations(db, chart, language, repo)
            total_counts["planets"] += count
            logger.info(f"    ✓ {count} planets")

            # Houses
            count = await generate_house_interpretations(db, chart, language, repo)
            total_counts["houses"] += count
            logger.info(f"    ✓ {count} houses")

            # Aspects
            count = await generate_aspect_interpretations(db, chart, language, repo)
            total_counts["aspects"] += count
            logger.info(f"    ✓ {count} aspects")

            # Arabic Parts
            count = await generate_arabic_parts_interpretations(db, chart, language, repo)
            total_counts["arabic_parts"] += count
            logger.info(f"    ✓ {count} Arabic Parts")

            # Growth
            count = await generate_growth_interpretations(db, chart, language, repo)
            total_counts["growth"] += count
            logger.info(f"    ✓ {count} growth components")

        total = sum(total_counts.values())
        logger.success(f"  Total: {total} interpretations generated")

        return total_counts


async def main(
    chart_id: str | None = None,
    clear: bool = False,
    dry_run: bool = False,
):
    """Main function."""
    start_time = datetime.now(UTC)

    logger.info("=" * 70)
    logger.info("Public Chart Interpretations Population Script")
    logger.info("=" * 70)

    if dry_run:
        logger.warning("[DRY RUN MODE] No interpretations will be generated")

    if clear:
        logger.warning("[CLEAR MODE] Existing interpretations will be deleted")

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

    logger.info(f"\nFound {len(charts)} chart(s) to process\n")

    # Process each chart
    success_count = 0
    fail_count = 0
    grand_total = {"planets": 0, "houses": 0, "aspects": 0, "arabic_parts": 0, "growth": 0}

    for i, chart in enumerate(charts, 1):
        try:
            logger.info(f"[{i}/{len(charts)}] {chart.full_name}")
            counts = await process_chart(
                chart_id=chart.id,
                clear=clear,
                dry_run=dry_run,
            )

            for key, value in counts.items():
                grand_total[key] += value

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
    logger.info("\nInterpretations generated:")
    logger.info(f"  Planets: {grand_total['planets']}")
    logger.info(f"  Houses: {grand_total['houses']}")
    logger.info(f"  Aspects: {grand_total['aspects']}")
    logger.info(f"  Arabic Parts: {grand_total['arabic_parts']}")
    logger.info(f"  Growth: {grand_total['growth']}")
    logger.info(f"  TOTAL: {sum(grand_total.values())}")

    elapsed = (datetime.now(UTC) - start_time).total_seconds()
    logger.info(f"\nCompleted in {elapsed:.2f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Populate public chart interpretations")
    parser.add_argument(
        "--chart-id",
        type=str,
        help="Specific chart ID to process (UUID)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing interpretations before generating",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually generating",
    )

    args = parser.parse_args()

    asyncio.run(
        main(
            chart_id=args.chart_id,
            clear=args.clear,
            dry_run=args.dry_run,
        )
    )
