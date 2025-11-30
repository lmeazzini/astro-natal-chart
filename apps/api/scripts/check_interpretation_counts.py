#!/usr/bin/env python3
"""Check interpretation counts per chart."""

import asyncio
from collections import defaultdict

from sqlalchemy import and_, func, select

from app.core.database import AsyncSessionLocal
from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation


async def main():
    """Check interpretation counts."""
    async with AsyncSessionLocal() as db:
        # Get all non-deleted charts
        stmt = select(BirthChart).where(
            and_(
                BirthChart.chart_data.isnot(None),
                BirthChart.deleted_at.is_(None),
            )
        )
        result = await db.execute(stmt)
        charts = result.scalars().all()

        print(f"Analyzing {len(charts)} charts...\n")

        for chart in charts:
            # Get counts by type and language
            stmt = (
                select(
                    ChartInterpretation.interpretation_type,
                    ChartInterpretation.language,
                    func.count(ChartInterpretation.id),
                )
                .where(ChartInterpretation.chart_id == chart.id)
                .group_by(
                    ChartInterpretation.interpretation_type,
                    ChartInterpretation.language,
                )
                .order_by(
                    ChartInterpretation.interpretation_type,
                    ChartInterpretation.language,
                )
            )
            result = await db.execute(stmt)
            rows = result.fetchall()

            total = sum(row[2] for row in rows)
            print(f"Chart: {chart.person_name} ({chart.id})")
            print(f"Total: {total} interpretations")

            # Group by type and language
            by_type = defaultdict(dict)
            for interp_type, lang, count in rows:
                by_type[interp_type][lang] = count

            for interp_type in sorted(by_type.keys()):
                langs = by_type[interp_type]
                print(f"  {interp_type}:", end=" ")
                for lang in ["pt-BR", "en-US"]:
                    count = langs.get(lang, 0)
                    print(f"{lang}={count}", end=" ")
                print()
            print()


if __name__ == "__main__":
    asyncio.run(main())
