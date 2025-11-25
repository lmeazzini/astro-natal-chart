#!/usr/bin/env python
"""
Script to regenerate all interpretations using RAG-enhanced service.

This script:
1. Regenerates RAG interpretations for all birth_charts
2. The interpretation_cache will be populated when charts are accessed

Run inside Docker:
    docker exec astro-api sh -c 'cd /app && .venv/bin/python scripts/regenerate_interpretations.py'
"""

import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import select, text  # noqa: E402

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.models.chart import BirthChart  # noqa: E402
from app.repositories.interpretation_repository import InterpretationRepository  # noqa: E402
from app.services.interpretation_service_rag import InterpretationServiceRAG  # noqa: E402


async def regenerate_all_interpretations():
    """Regenerate RAG interpretations for all birth charts."""

    async with AsyncSessionLocal() as db:
        print("=" * 60)
        print("REGENERATING RAG INTERPRETATIONS FOR BIRTH CHARTS")
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

        rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)
        repo = InterpretationRepository(db)

        for chart in charts:
            print(f"\nProcessing: {chart.person_name} ({chart.id})")

            try:
                # Delete existing interpretations
                existing = await repo.get_by_chart_id(chart.id)
                deleted_count = 0
                for interp in existing:
                    await repo.delete(interp)
                    deleted_count += 1
                if deleted_count > 0:
                    await db.commit()
                print(f"  Deleted {deleted_count} existing interpretations")

                # Generate new RAG interpretations
                await rag_service.generate_all_rag_interpretations(
                    chart=chart,
                    chart_data=chart.chart_data,
                )

                # Count new interpretations
                count_result = await db.execute(
                    text("SELECT COUNT(*) FROM chart_interpretations WHERE chart_id = :chart_id"),
                    {"chart_id": str(chart.id)},
                )
                new_count = count_result.scalar()
                print(f"  Generated {new_count} new RAG interpretations")

            except Exception as e:
                print(f"  ERROR: {e}")
                continue

        # Final count
        result = await db.execute(text("SELECT COUNT(*) FROM chart_interpretations"))
        total = result.scalar()
        print("\n" + "=" * 60)
        print(f"Total interpretations in database: {total}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(regenerate_all_interpretations())
