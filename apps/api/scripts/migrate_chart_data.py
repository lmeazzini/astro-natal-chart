#!/usr/bin/env python3
"""
Script to migrate chart_data to new format with all additional fields.
Run inside API container: docker compose exec api uv run python scripts/migrate_chart_data.py
"""

import asyncio
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, "/app")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.chart import BirthChart
from app.models.public_chart import PublicChart
from app.services.astro_service import calculate_birth_chart


async def migrate_birth_charts(session: AsyncSession) -> int:
    """Migrate all birth_charts to new chart_data format with language-first structure."""
    print("Fetching birth_charts...")

    result = await session.execute(select(BirthChart).where(BirthChart.deleted_at.is_(None)))
    charts = result.scalars().all()

    print(f"Found {len(charts)} birth_charts to migrate")

    migrated = 0
    errors = 0

    for chart in charts:
        try:
            print(f"  Migrating chart {chart.id} ({chart.person_name})...")

            # Calculate chart data for pt-BR
            pt_br_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system or "placidus",
                language="pt-BR",
            )

            # Use language-first format: {"pt-BR": {...}}
            chart.chart_data = {"pt-BR": pt_br_data}
            migrated += 1

        except Exception as e:
            print(f"  ERROR migrating chart {chart.id}: {e}")
            errors += 1

    await session.commit()
    print(f"Birth charts migrated: {migrated}, errors: {errors}")
    return migrated


async def migrate_public_charts(session: AsyncSession) -> int:
    """Migrate all public_charts to new chart_data format with language-first structure."""
    print("\nFetching public_charts...")

    result = await session.execute(select(PublicChart))
    charts = result.scalars().all()

    print(f"Found {len(charts)} public_charts to migrate")

    migrated = 0
    errors = 0

    for chart in charts:
        try:
            print(f"  Migrating public chart {chart.id} ({chart.full_name})...")

            # Calculate chart data for pt-BR
            pt_br_data = calculate_birth_chart(
                birth_datetime=chart.birth_datetime,
                timezone=chart.birth_timezone,
                latitude=float(chart.latitude),
                longitude=float(chart.longitude),
                house_system=chart.house_system or "placidus",
                language="pt-BR",
            )

            # Use language-first format: {"pt-BR": {...}}
            chart.chart_data = {"pt-BR": pt_br_data}
            migrated += 1

        except Exception as e:
            print(f"  ERROR migrating public chart {chart.id}: {e}")
            errors += 1

    await session.commit()
    print(f"Public charts migrated: {migrated}, errors: {errors}")
    return migrated


async def main():
    """Main migration function."""
    print("=" * 60)
    print("Chart Data Migration Script")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)

    # Create async engine
    engine = create_async_engine(str(settings.DATABASE_URL), echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Migrate birth_charts with language-first format
        birth_count = await migrate_birth_charts(session)

        # Migrate public_charts with language-first format
        public_count = await migrate_public_charts(session)

    await engine.dispose()

    print("\n" + "=" * 60)
    print("Migration Complete!")
    print(f"Birth charts: {birth_count}")
    print(f"Public charts: {public_count}")
    print(f"Finished at: {datetime.now().isoformat()}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
