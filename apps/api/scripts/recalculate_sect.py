#!/usr/bin/env python
"""
Script to recalculate sect for all charts after the sect calculation fix.

This script:
1. Recalculates sect for all public_charts
2. Recalculates sect for all birth_charts
3. Reports which charts had their sect corrected

Run inside Docker:
    docker exec astro-api sh -c 'cd /app && .venv/bin/python scripts/recalculate_sect.py'
"""

import asyncio
import sys

sys.path.insert(0, "/app")

from sqlalchemy import text  # noqa: E402

from app.core.database import AsyncSessionLocal  # noqa: E402
from app.services.astro_service import calculate_sect  # noqa: E402


async def recalculate_all_sects():
    """Recalculate sect for all charts."""

    async with AsyncSessionLocal() as db:
        # Track changes
        public_updated = 0
        public_unchanged = 0
        birth_updated = 0
        birth_unchanged = 0

        print("=" * 60)
        print("RECALCULATING SECT FOR ALL CHARTS")
        print("=" * 60)

        # 1. Process public_charts
        print("\nProcessing public_charts...")

        # Ascendant is in houses[0].longitude (House 1 cusp = ASC)
        result = await db.execute(
            text(
                "SELECT id, full_name, "
                "chart_data->>'sect' as current_sect, "
                "(chart_data->'houses'->0->>'longitude')::float as ascendant, "
                "(SELECT (p->>'longitude')::float "
                "FROM jsonb_array_elements(chart_data->'planets') p "
                "WHERE p->>'name' = 'Sun' LIMIT 1) as sun_longitude "
                "FROM public_charts "
                "WHERE chart_data IS NOT NULL"
            )
        )

        public_charts = result.fetchall()

        for chart in public_charts:
            chart_id, name, current_sect, ascendant, sun_lon = chart

            if ascendant is None or sun_lon is None:
                print(f"  [SKIP] {name}: Missing ascendant or sun longitude")
                continue

            # Calculate correct sect
            correct_sect = calculate_sect(ascendant, sun_lon)

            if current_sect != correct_sect:
                # Update the chart_data
                await db.execute(
                    text(
                        "UPDATE public_charts "
                        "SET chart_data = jsonb_set(chart_data, '{sect}', :new_sect::jsonb), "
                        "updated_at = NOW() "
                        "WHERE id = :chart_id"
                    ),
                    {"chart_id": str(chart_id), "new_sect": f'"{correct_sect}"'},
                )

                print(f"  [UPDATED] {name}: {current_sect} -> {correct_sect}")
                public_updated += 1
            else:
                print(f"  [OK] {name}: already correct ({current_sect})")
                public_unchanged += 1

        # 2. Process birth_charts
        print("\nProcessing birth_charts...")

        # Try both structures: chart_info.ascendant OR houses[0].longitude
        result = await db.execute(
            text(
                "SELECT id, person_name, "
                "chart_data->>'sect' as current_sect, "
                "COALESCE("
                "  (chart_data->'chart_info'->>'ascendant')::float, "
                "  (chart_data->'houses'->0->>'longitude')::float"
                ") as ascendant, "
                "(SELECT (p->>'longitude')::float "
                "FROM jsonb_array_elements(chart_data->'planets') p "
                "WHERE p->>'name' = 'Sun' LIMIT 1) as sun_longitude "
                "FROM birth_charts "
                "WHERE deleted_at IS NULL "
                "AND chart_data IS NOT NULL"
            )
        )

        birth_charts = result.fetchall()

        for chart in birth_charts:
            chart_id, name, current_sect, ascendant, sun_lon = chart

            if ascendant is None or sun_lon is None:
                print(f"  [SKIP] {name}: Missing ascendant or sun longitude")
                continue

            # Calculate correct sect
            correct_sect = calculate_sect(ascendant, sun_lon)

            if current_sect != correct_sect:
                # Update the chart_data
                await db.execute(
                    text(
                        "UPDATE birth_charts "
                        "SET chart_data = jsonb_set(chart_data, '{sect}', :new_sect::jsonb), "
                        "updated_at = NOW() "
                        "WHERE id = :chart_id"
                    ),
                    {"chart_id": str(chart_id), "new_sect": f'"{correct_sect}"'},
                )

                print(f"  [UPDATED] {name}: {current_sect} -> {correct_sect}")
                birth_updated += 1
            else:
                print(f"  [OK] {name}: already correct ({current_sect})")
                birth_unchanged += 1

        # Commit all changes
        await db.commit()

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("\nPublic Charts:")
        print(f"  Updated: {public_updated}")
        print(f"  Unchanged: {public_unchanged}")
        print("\nBirth Charts:")
        print(f"  Updated: {birth_updated}")
        print(f"  Unchanged: {birth_unchanged}")
        print(f"\nTotal updated: {public_updated + birth_updated}")


if __name__ == "__main__":
    asyncio.run(recalculate_all_sects())
