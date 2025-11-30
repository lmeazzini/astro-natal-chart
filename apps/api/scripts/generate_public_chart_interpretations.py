#!/usr/bin/env python3
"""
Generate all interpretations for public charts.

This script generates RAG-enhanced interpretations for all public charts, including:
- Planet interpretations (Sun, Moon, planets in signs and houses)
- House interpretations (12 houses with rulers)
- Aspect interpretations (major aspects between planets)
- Arabic Parts interpretations (Lot of Fortune, Spirit, etc.)
- Growth suggestions (personal development insights)

Supports multiple languages: pt-BR and en-US

Usage:
    uv run python scripts/generate_public_chart_interpretations.py [--clear] [--verbose] [--lang LANG]

Arguments:
    --clear: Delete existing interpretations before generating new ones
    --verbose: Enable verbose logging
    --lang: Language code (pt-BR or en-US, default: both)
    --chart: Generate for specific chart slug only
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.public_chart import PublicChart
from app.models.public_chart_interpretation import PublicChartInterpretation
from app.services.interpretation_service_rag import InterpretationServiceRAG
from app.services.personal_growth_service import PersonalGrowthService


async def clear_chart_interpretations(db: AsyncSession, chart_id: UUID) -> int:
    """Delete all existing interpretations for a chart."""
    stmt = select(PublicChartInterpretation).where(PublicChartInterpretation.chart_id == chart_id)
    result = await db.execute(stmt)
    interpretations = result.scalars().all()

    count = 0
    for interp in interpretations:
        await db.delete(interp)
        count += 1

    await db.commit()
    return count


async def generate_planet_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    rag_service: InterpretationServiceRAG,
    language: str,
) -> int:
    """Generate interpretations for all planets."""
    chart_data = chart.chart_data
    if not chart_data:
        return 0

    planets_data = chart_data.get("planets", [])
    sect = chart_data.get("sect", "diurnal")
    count = 0

    for planet in planets_data:
        planet_name = planet.get("name", "")
        if not planet_name:
            continue

        sign = planet.get("sign", "")
        house = planet.get("house", 1)
        retrograde = planet.get("retrograde", False)
        dignities = planet.get("dignities", {})

        interpretation = await rag_service.generate_planet_interpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            dignities=dignities,
            sect=sect,
            retrograde=retrograde,
        )

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="planet",
            subject=planet_name,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)
        count += 1

    await db.commit()
    return count


async def generate_house_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    rag_service: InterpretationServiceRAG,
    language: str,
) -> int:
    """Generate interpretations for all houses."""
    chart_data = chart.chart_data
    if not chart_data:
        return 0

    houses_data = chart_data.get("houses", [])
    planets_data = chart_data.get("planets", [])
    sect = chart_data.get("sect", "diurnal")
    count = 0

    for house in houses_data:
        house_number = house.get("house", 0) or house.get("number", 0)
        house_sign = house.get("sign", "")

        if not house_number or not house_sign:
            continue

        from app.astro.dignities import get_sign_ruler

        ruler = get_sign_ruler(house_sign) or "Unknown"

        # Find ruler's dignities
        ruler_dignities: dict[str, Any] = {}
        for planet_data in planets_data:
            if planet_data.get("name") == ruler:
                ruler_dignities = planet_data.get("dignities", {})
                break

        interpretation = await rag_service.generate_house_interpretation(
            house=house_number,
            sign=house_sign,
            ruler=ruler,
            ruler_dignities=ruler_dignities,
            sect=sect,
        )

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="house",
            subject=str(house_number),
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)
        count += 1

    await db.commit()
    return count


async def generate_aspect_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    rag_service: InterpretationServiceRAG,
    language: str,
) -> int:
    """Generate interpretations for aspects."""
    chart_data = chart.chart_data
    if not chart_data:
        return 0

    aspects_list = chart_data.get("aspects", [])
    planets_data = chart_data.get("planets", [])
    sect = chart_data.get("sect", "diurnal")
    max_aspects = settings.RAG_MAX_ASPECTS
    count = 0

    for aspect in aspects_list[:max_aspects]:
        planet1 = aspect.get("planet1", "")
        planet2 = aspect.get("planet2", "")
        aspect_name = aspect.get("aspect", "")
        orb = aspect.get("orb", 0.0)

        if not all([planet1, planet2, aspect_name]):
            continue

        planet1_data: dict[str, Any] = next(
            (p for p in planets_data if p.get("name") == planet1), {}
        )
        planet2_data: dict[str, Any] = next(
            (p for p in planets_data if p.get("name") == planet2), {}
        )

        sign1 = planet1_data.get("sign", "")
        sign2 = planet2_data.get("sign", "")
        dignities1 = planet1_data.get("dignities", {})
        dignities2 = planet2_data.get("dignities", {})
        applying = aspect.get("applying", False)

        interpretation = await rag_service.generate_aspect_interpretation(
            planet1=planet1,
            planet2=planet2,
            aspect=aspect_name,
            sign1=sign1,
            sign2=sign2,
            orb=orb,
            applying=applying,
            sect=sect,
            dignities1=dignities1,
            dignities2=dignities2,
        )

        aspect_key = f"{planet1}-{aspect_name}-{planet2}"

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="aspect",
            subject=aspect_key,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)
        count += 1

    await db.commit()
    return count


async def generate_arabic_parts_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    rag_service: InterpretationServiceRAG,
    language: str,
) -> int:
    """Generate interpretations for Arabic Parts."""
    chart_data = chart.chart_data
    if not chart_data:
        return 0

    arabic_parts_data = chart_data.get("arabic_parts", {})
    if not arabic_parts_data:
        return 0

    from app.services.interpretation_service_rag import ARABIC_PARTS

    count = 0

    sect = chart_data.get("sect", "diurnal")

    for part_key, part_data in arabic_parts_data.items():
        if part_key not in ARABIC_PARTS:
            continue

        sign = part_data.get("sign", "")
        house = part_data.get("house", 1)
        degree = part_data.get("degree", 0.0)

        interpretation = await rag_service.generate_arabic_part_interpretation(
            part_key=part_key,
            sign=sign,
            house=house,
            degree=degree,
            sect=sect,
        )

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="arabic_part",
            subject=part_key,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)
        count += 1

    await db.commit()
    return count


async def generate_growth_interpretation(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
) -> int:
    """Generate growth suggestions interpretation."""
    chart_data = chart.chart_data
    if not chart_data:
        return 0

    growth_service = PersonalGrowthService(language=language, db=None)

    try:
        # Generate growth suggestions
        growth_response = await growth_service.generate_growth_suggestions(
            chart_data=chart_data,
            focus_areas=None,
        )

        # Combine all growth suggestions into a single text
        sections = []

        if growth_response.get("growth_points"):
            sections.append("## Pontos de Crescimento\n")
            for point in growth_response["growth_points"]:
                sections.append(f"### {point['title']}\n{point['description']}\n")
                if point.get("action_steps"):
                    sections.append("**Passos de Ação:**\n")
                    for step in point["action_steps"]:
                        sections.append(f"- {step}\n")

        if growth_response.get("challenges"):
            sections.append("\n## Desafios\n")
            for challenge in growth_response["challenges"]:
                sections.append(f"### {challenge['title']}\n{challenge['description']}\n")
                if challenge.get("strategies"):
                    sections.append("**Estratégias:**\n")
                    for strategy in challenge["strategies"]:
                        sections.append(f"- {strategy}\n")

        if growth_response.get("opportunities"):
            sections.append("\n## Oportunidades\n")
            for opportunity in growth_response["opportunities"]:
                sections.append(f"### {opportunity['title']}\n{opportunity['description']}\n")
                if opportunity.get("how_to_leverage"):
                    sections.append("**Como Aproveitar:**\n")
                    for leverage in opportunity["how_to_leverage"]:
                        sections.append(f"- {leverage}\n")

        if growth_response.get("purpose"):
            sections.append(f"\n## Propósito de Vida\n{growth_response['purpose']}\n")

        growth_text = "\n".join(sections)

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="growth",
            subject="personal_development",
            content=growth_text,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)
        await db.commit()
        return 1

    except Exception as e:
        logger.error(f"Failed to generate growth interpretation: {e}")
        return 0


async def generate_chart_interpretations(
    db: AsyncSession,
    chart: PublicChart,
    language: str,
    clear: bool = False,
) -> dict[str, int]:
    """Generate all interpretations for a single chart."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Chart: {chart.full_name} ({chart.slug})")
    logger.info(f"Language: {language}")
    logger.info(f"{'='*60}")

    # Clear existing interpretations if requested
    if clear:
        deleted = await clear_chart_interpretations(db, chart.id)
        logger.info(f"Deleted {deleted} existing interpretations")

    # Initialize RAG service
    rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True, language=language)

    # Generate all interpretation types
    counts = {}

    logger.info("Generating planet interpretations...")
    counts["planets"] = await generate_planet_interpretations(db, chart, rag_service, language)
    logger.success(f"✓ Generated {counts['planets']} planet interpretations")

    logger.info("Generating house interpretations...")
    counts["houses"] = await generate_house_interpretations(db, chart, rag_service, language)
    logger.success(f"✓ Generated {counts['houses']} house interpretations")

    logger.info("Generating aspect interpretations...")
    counts["aspects"] = await generate_aspect_interpretations(db, chart, rag_service, language)
    logger.success(f"✓ Generated {counts['aspects']} aspect interpretations")

    logger.info("Generating Arabic Parts interpretations...")
    counts["arabic_parts"] = await generate_arabic_parts_interpretations(
        db, chart, rag_service, language
    )
    logger.success(f"✓ Generated {counts['arabic_parts']} Arabic Parts interpretations")

    # Skip growth for now - requires additional OpenAI credits and is optional
    # logger.info("Generating growth suggestions...")
    # counts["growth"] = await generate_growth_interpretation(db, chart, language)
    # logger.success(f"✓ Generated {counts['growth']} growth interpretation")
    counts["growth"] = 0

    total = sum(counts.values())
    logger.info(f"\nTotal interpretations generated: {total}")

    return counts


async def main(
    clear: bool = False,
    verbose: bool = False,
    languages: list[str] | None = None,
    chart_slug: str | None = None,
    skip_completed: bool = False,
) -> None:
    """Main entry point."""
    if verbose:
        logger.enable("app")
    else:
        logger.disable("app")

    if languages is None:
        languages = ["pt-BR", "en-US"]

    if not settings.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not configured - cannot generate interpretations!")
        return

    logger.info(f"\n{'='*60}")
    logger.info("PUBLIC CHARTS INTERPRETATIONS GENERATOR")
    logger.info(f"{'='*60}")
    logger.info(f"Languages: {', '.join(languages)}")
    logger.info(f"Clear existing: {clear}")
    logger.info(f"Skip completed: {skip_completed}")
    if chart_slug:
        logger.info(f"Specific chart: {chart_slug}")
    logger.info(f"{'='*60}\n")

    async with AsyncSessionLocal() as db:
        try:
            # Get charts to process
            stmt = select(PublicChart).where(PublicChart.is_published == True)  # noqa: E712
            if chart_slug:
                stmt = stmt.where(PublicChart.slug == chart_slug)

            result = await db.execute(stmt)
            charts = result.scalars().all()

            if not charts:
                logger.warning("No charts found to process!")
                return

            # Filter out already completed charts if skip_completed is True
            if skip_completed:
                from sqlalchemy import func

                charts_to_process = []
                for chart in charts:
                    count_stmt = select(func.count(PublicChartInterpretation.id)).where(
                        PublicChartInterpretation.chart_id == chart.id
                    )
                    count_result = await db.execute(count_stmt)
                    count = count_result.scalar()

                    if count == 0:
                        charts_to_process.append(chart)
                    else:
                        logger.info(
                            f"Skipping {chart.slug} ({count} interpretations already exist)"
                        )

                charts = charts_to_process

            if not charts:
                logger.warning("No charts to process after filtering!")
                return

            logger.info(f"Found {len(charts)} charts to process\n")

            # Process each chart in each language
            total_counts: dict[str, int] = {}
            success_count = 0
            fail_count = 0

            for i, chart in enumerate(charts, 1):
                logger.info(f"\n[{i}/{len(charts)}] Processing {chart.full_name}...")

                for language in languages:
                    try:
                        counts = await generate_chart_interpretations(db, chart, language, clear)

                        # Aggregate counts
                        for key, value in counts.items():
                            total_counts[key] = total_counts.get(key, 0) + value

                        success_count += 1

                    except Exception as e:
                        logger.error(f"Failed to generate {language} interpretations: {e}")
                        fail_count += 1
                        continue

            # Final summary
            logger.info(f"\n{'='*60}")
            logger.info("GENERATION COMPLETE")
            logger.info(f"{'='*60}")
            logger.info(f"Charts processed: {len(charts)}")
            logger.info(f"Languages: {len(languages)}")
            logger.info(f"✓ Success: {success_count}/{len(charts) * len(languages)}")
            if fail_count > 0:
                logger.warning(f"✗ Failed: {fail_count}/{len(charts) * len(languages)}")
            logger.info("\nInterpretations by type:")
            for key, value in sorted(total_counts.items()):
                logger.info(f"  • {key}: {value}")
            logger.info(f"{'='*60}\n")

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate interpretations for public charts")
    parser.add_argument("--clear", action="store_true", help="Clear existing interpretations")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--lang",
        type=str,
        choices=["pt-BR", "en-US", "both"],
        default="both",
        help="Language for interpretations (default: both)",
    )
    parser.add_argument("--chart", type=str, help="Generate for specific chart slug only")
    parser.add_argument(
        "--skip-completed",
        action="store_true",
        help="Skip charts that already have interpretations",
    )

    args = parser.parse_args()

    languages = ["pt-BR", "en-US"] if args.lang == "both" else [args.lang]

    asyncio.run(main(args.clear, args.verbose, languages, args.chart, args.skip_completed))
