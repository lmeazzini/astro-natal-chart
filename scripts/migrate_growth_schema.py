#!/usr/bin/env python3
"""
Migration script to fix growth interpretations schema.

Old schema:
- interpretation_type: "growth_points", "growth_challenges", "growth_opportunities", "growth_purpose"
- subject: "growth_analysis"

New schema:
- interpretation_type: "growth"
- subject: "points", "challenges", "opportunities", "purpose"
"""
import asyncio
import os
import sys
from pathlib import Path

import asyncpg


async def get_db_connection():
    """Create database connection from environment variables."""
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent / "apps" / "api" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment")

    # Convert asyncpg URL format
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

    return await asyncpg.connect(database_url)


async def migrate_growth_interpretations() -> None:
    """Migrate existing growth interpretations to new schema."""
    print("🔄 Starting growth interpretations migration...")

    conn = await get_db_connection()

    try:
        # Find all growth interpretations with old schema
        rows = await conn.fetch("""
            SELECT id, interpretation_type, subject
            FROM chart_interpretations
            WHERE interpretation_type IN (
                'growth_points',
                'growth_challenges',
                'growth_opportunities',
                'growth_purpose'
            )
        """)

        if not rows:
            print("✅ No growth interpretations found to migrate.")
            return

        print(f"📊 Found {len(rows)} growth interpretations to migrate")

        # Map old interpretation_type to new subject
        subject_map = {
            "growth_points": "points",
            "growth_challenges": "challenges",
            "growth_opportunities": "opportunities",
            "growth_purpose": "purpose",
        }

        updated_count = 0
        for row in rows:
            old_type = row["interpretation_type"]
            new_subject = subject_map.get(old_type)

            if not new_subject:
                print(f"⚠️  Unknown type: {old_type}, skipping...")
                continue

            # Update the interpretation
            await conn.execute("""
                UPDATE chart_interpretations
                SET interpretation_type = 'growth',
                    subject = $1,
                    updated_at = NOW()
                WHERE id = $2
            """, new_subject, row["id"])

            updated_count += 1
            print(f"  ✓ Updated {old_type} → interpretation_type='growth', subject='{new_subject}'")

        print(f"\n✅ Migration complete! Updated {updated_count} interpretations.")

    finally:
        await conn.close()


async def verify_migration() -> None:
    """Verify the migration was successful."""
    print("\n🔍 Verifying migration...")

    conn = await get_db_connection()

    try:
        # Check for old schema entries
        old_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM chart_interpretations
            WHERE interpretation_type IN (
                'growth_points',
                'growth_challenges',
                'growth_opportunities',
                'growth_purpose'
            )
        """)

        if old_count > 0:
            print(f"❌ Found {old_count} entries still using old schema!")
            return

        # Check for new schema entries
        new_count = await conn.fetchval("""
            SELECT COUNT(*)
            FROM chart_interpretations
            WHERE interpretation_type = 'growth'
        """)

        print(f"✅ Verification complete!")
        print(f"   - Old schema entries: {old_count}")
        print(f"   - New schema entries: {new_count}")

        # Group by subject
        subjects = await conn.fetch("""
            SELECT subject, COUNT(*) as count
            FROM chart_interpretations
            WHERE interpretation_type = 'growth'
            GROUP BY subject
            ORDER BY subject
        """)

        if subjects:
            print(f"\n📊 Breakdown by subject:")
            for row in subjects:
                print(f"   - {row['subject']}: {row['count']}")

    finally:
        await conn.close()


async def main() -> None:
    """Run migration and verification."""
    try:
        await migrate_growth_interpretations()
        await verify_migration()
        print("\n🎉 Migration successful!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
