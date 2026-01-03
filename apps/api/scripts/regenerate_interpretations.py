#!/usr/bin/env python
"""
Script to regenerate all interpretations using RAG-enhanced service.

This script:
1. Regenerates RAG interpretations for all birth_charts
2. Supports multiple languages (pt-BR and en-US)
3. The interpretation_cache will be populated when charts are accessed

Run inside Docker:
    docker exec astro-api sh -c 'cd /app && .venv/bin/python scripts/regenerate_interpretations.py'
    docker exec astro-api sh -c 'cd /app && .venv/bin/python scripts/regenerate_interpretations.py --lang both'
"""

import argparse
import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select, text  # noqa: E402

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.chart import BirthChart  # noqa: E402
from app.repositories.interpretation_repository import InterpretationRepository  # noqa: E402
from app.services.interpretation_service_rag import InterpretationServiceRAG  # noqa: E402


async def regenerate_all_interpretations(languages: list[str], clear: bool = True):
    """Regenerate RAG interpretations for all birth charts in multiple languages."""

    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("REGENERATING RAG INTERPRETATIONS FOR BIRTH CHARTS")
        print("=" * 60)
        print(f"Languages: {', '.join(languages)}")
        print(f"Clear existing: {clear}")
        print("=" * 60)

        # Get all birth charts with chart_data
        result = await db.execute(
            select(BirthChart).where(
                BirthChart.deleted_at.is_(None),
                BirthChart.chart_data.isnot(None),
            )
        )

        charts = result.scalars().all()
        print(f"\nFound {len(charts)} birth charts to process")

        repo = InterpretationRepository(db)

        for chart in charts:
            print(f"\n{'─' * 40}")
            print(f"Processing: {chart.person_name} ({chart.id})")

            # Delete existing interpretations once (for all languages)
            if clear:
                existing = await repo.get_by_chart_id(chart.id)
                deleted_count = 0
                for interp in existing:
                    await repo.delete(interp)
                    deleted_count += 1
                if deleted_count > 0:
                    await db.commit()
                print(f"  Deleted {deleted_count} existing interpretations")

            for lang in languages:
                try:
                    print(f"\n  Generating {lang} interpretations...")

                    # Create service with specific language
                    rag_service = InterpretationServiceRAG(
                        db, use_cache=True, use_rag=True, language=lang
                    )

                    # Generate new RAG interpretations
                    await rag_service.generate_all_rag_interpretations(
                        chart=chart,
                        chart_data=chart.chart_data,
                        force=True,  # Force regeneration
                    )

                    # Commit the generated interpretations
                    await db.commit()

                    # Count new interpretations for this language
                    count_result = await db.execute(
                        text(
                            "SELECT COUNT(*) FROM chart_interpretations "
                            "WHERE chart_id = :chart_id AND language = :lang"
                        ),
                        {"chart_id": str(chart.id), "lang": lang},
                    )
                    lang_count = count_result.scalar()
                    print(f"    ✓ Generated {lang_count} {lang} interpretations")

                except Exception as e:
                    print(f"    ✗ ERROR ({lang}): {e}")
                    await db.rollback()
                    continue

        # Final summary
        print("\n" + "=" * 60)
        print("SUMMARY BY LANGUAGE")
        print("=" * 60)

        for lang in languages:
            result = await db.execute(
                text("SELECT COUNT(*) FROM chart_interpretations WHERE language = :lang"),
                {"lang": lang},
            )
            count = result.scalar()
            print(f"  {lang}: {count} interpretations")

        result = await db.execute(text("SELECT COUNT(*) FROM chart_interpretations"))
        total = result.scalar()
        print(f"\nTotal interpretations in database: {total}")
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regenerate RAG interpretations for birth charts")
    parser.add_argument(
        "--lang",
        type=str,
        choices=["pt-BR", "en-US", "both"],
        default="both",
        help="Language for interpretations (default: both)",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Don't delete existing interpretations before regenerating",
    )

    args = parser.parse_args()

    languages = ["pt-BR", "en-US"] if args.lang == "both" else [args.lang]

    asyncio.run(regenerate_all_interpretations(languages, clear=not args.no_clear))
