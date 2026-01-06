#!/usr/bin/env python3
"""
Database seed script for exporting and importing user data.

This script allows you to:
1. Export all user-inputted data to a JSON file
2. Import data from a JSON file to replicate the database

Usage:
    # Export data to JSON
    uv run python scripts/seed_database.py export --output backup.json

    # Import data from JSON
    uv run python scripts/seed_database.py import --input backup.json

    # Import with clear (deletes existing data first)
    uv run python scripts/seed_database.py import --input backup.json --clear

    # Export only specific tables
    uv run python scripts/seed_database.py export --output backup.json --tables users,birth_charts

Supported tables:
    - users
    - oauth_accounts
    - user_consents
    - birth_charts
    - public_charts
    - interpretation_cache
    - vector_documents
"""

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

import asyncpg
from loguru import logger

# Default database connection settings (can be overridden via env)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "astro",
    "password": "dev_password",
    "database": "astro_dev",
}

# Tables in dependency order (parent tables first)
TABLE_ORDER = [
    "users",
    "oauth_accounts",
    "user_consents",
    "birth_charts",
    "public_charts",
    "interpretation_cache",
    "vector_documents",
]

# Column definitions for each table (for export/import)
TABLE_COLUMNS = {
    "users": [
        "id", "email", "password_hash", "full_name", "avatar_url",
        "role", "is_active", "is_superuser", "email_verified",
        "timezone", "locale", "time_format", "bio", "website", "instagram", "twitter",
        "location", "specializations", "user_type", "professional_since",
        "profile_public", "allow_email_notifications", "analytics_consent",
        "last_login_at", "last_activity_at", "password_changed_at",
        "created_at", "updated_at", "deleted_at",
    ],
    "oauth_accounts": [
        "id", "user_id", "provider", "provider_user_id", "created_at",
    ],
    "user_consents": [
        "id", "user_id", "consent_type", "version", "accepted",
        "ip_address", "user_agent", "consent_text", "created_at", "revoked_at",
    ],
    "birth_charts": [
        "id", "user_id", "person_name", "birth_datetime", "birth_timezone",
        "latitude", "longitude", "city", "country", "gender", "notes", "tags",
        "house_system", "zodiac_type", "node_type", "chart_data",
        "status", "progress", "error_message", "task_id",
        "pdf_url", "pdf_generated_at", "pdf_generating", "pdf_task_id",
        "visibility", "share_uuid",
        "created_at", "updated_at", "deleted_at",
    ],
    "public_charts": [
        "id", "slug", "full_name", "category", "birth_datetime", "birth_timezone",
        "latitude", "longitude", "city", "country", "photo_url",
        "short_bio", "short_bio_i18n", "highlights", "highlights_i18n",
        "meta_title", "meta_title_i18n", "meta_description", "meta_description_i18n",
        "meta_keywords", "meta_keywords_i18n", "house_system", "chart_data",
        "view_count", "is_published", "featured",
        "created_at", "updated_at",
    ],
    "interpretation_cache": [
        "id", "cache_key", "interpretation_type", "subject", "content",
        "parameters_json", "openai_model", "prompt_version",
        "hit_count", "created_at", "last_accessed_at",
    ],
    "vector_documents": [
        "id", "collection_name", "document_type", "title", "content",
        "chunk_index", "total_chunks", "doc_metadata", "vector_id",
        "embedding_model", "bm25_score", "created_at", "updated_at", "indexed_at",
    ],
}


def serialize_value(value: Any) -> Any:
    """Serialize a value for JSON export."""
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (list, dict)):
        return value  # Already JSON-serializable
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def deserialize_value(value: Any, col_name: str) -> Any:
    """Deserialize a value from JSON import."""
    if value is None:
        return None

    # UUID columns
    uuid_columns = [
        "id", "user_id", "chart_id", "author_id",
        "resource_id", "share_uuid", "document_id",
    ]
    if col_name in uuid_columns and isinstance(value, str):
        return UUID(value)

    # DateTime columns
    datetime_columns = [
        "birth_datetime", "created_at", "updated_at", "deleted_at",
        "last_login_at", "last_activity_at", "password_changed_at",
        "started_at", "expires_at", "revoked_at", "published_at",
        "pdf_generated_at", "last_accessed_at", "indexed_at",
    ]
    if col_name in datetime_columns and isinstance(value, str):
        return datetime.fromisoformat(value)

    # Decimal columns
    decimal_columns = ["latitude", "longitude", "bm25_score"]
    if col_name in decimal_columns and value is not None:
        return Decimal(str(value))

    return value


async def export_table(conn: asyncpg.Connection, table: str) -> list[dict[str, Any]]:
    """Export all rows from a table."""
    columns = TABLE_COLUMNS.get(table, [])
    if not columns:
        logger.warning(f"No column definition for table {table}, skipping")
        return []

    # Build query - exclude soft-deleted records for certain tables
    soft_delete_tables = ["users", "birth_charts"]
    if table in soft_delete_tables:
        query = f"SELECT * FROM {table} WHERE deleted_at IS NULL ORDER BY created_at"
    else:
        query = f"SELECT * FROM {table} ORDER BY created_at"

    rows = await conn.fetch(query)
    result = []

    for row in rows:
        row_dict = {}
        for col in columns:
            if col in row.keys():
                row_dict[col] = serialize_value(row[col])
        result.append(row_dict)

    return result


async def import_table(
    conn: asyncpg.Connection,
    table: str,
    data: list[dict[str, Any]],
    clear: bool = False,
) -> int:
    """Import rows into a table."""
    if not data:
        return 0

    columns = TABLE_COLUMNS.get(table, [])
    if not columns:
        logger.warning(f"No column definition for table {table}, skipping")
        return 0

    # Clear existing data if requested
    if clear:
        # Handle foreign key constraints - disable temporarily
        await conn.execute(f"DELETE FROM {table}")
        logger.info(f"  Cleared existing data from {table}")

    # Insert rows
    count = 0
    for row_data in data:
        # Filter to only columns that exist in this row's data
        available_cols = [c for c in columns if c in row_data]
        values = [deserialize_value(row_data.get(c), c) for c in available_cols]

        # Build INSERT query
        col_names = ", ".join(available_cols)
        placeholders = ", ".join(f"${i+1}" for i in range(len(available_cols)))

        # Use ON CONFLICT DO NOTHING to skip duplicates
        query = f"""
            INSERT INTO {table} ({col_names})
            VALUES ({placeholders})
            ON CONFLICT (id) DO NOTHING
        """

        try:
            await conn.execute(query, *values)
            count += 1
        except Exception as e:
            logger.error(f"  Error inserting into {table}: {e}")
            logger.debug(f"  Row data: {row_data}")

    return count


async def export_database(output_file: str, tables: list[str] | None = None) -> None:
    """Export database to JSON file."""
    logger.info("Connecting to database...")
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        export_data = {
            "exported_at": datetime.now(UTC).isoformat(),
            "version": "1.0",
            "tables": {},
        }

        tables_to_export = tables or TABLE_ORDER

        for table in tables_to_export:
            if table not in TABLE_COLUMNS:
                logger.warning(f"Unknown table: {table}, skipping")
                continue

            logger.info(f"Exporting {table}...")
            rows = await export_table(conn, table)
            export_data["tables"][table] = rows
            logger.success(f"  Exported {len(rows)} rows from {table}")

        # Write to file
        output_path = Path(output_file)
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        total_rows = sum(len(rows) for rows in export_data["tables"].values())
        logger.success(f"\nExport complete!")
        logger.info(f"  Total rows: {total_rows}")
        logger.info(f"  Output file: {output_path.absolute()}")

    finally:
        await conn.close()


async def import_database(input_file: str, clear: bool = False) -> None:
    """Import database from JSON file."""
    # Read input file
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)

    logger.info(f"Reading {input_file}...")
    with input_path.open("r", encoding="utf-8") as f:
        import_data = json.load(f)

    logger.info(f"Export version: {import_data.get('version', 'unknown')}")
    logger.info(f"Exported at: {import_data.get('exported_at', 'unknown')}")

    logger.info("Connecting to database...")
    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        # Import in dependency order
        tables_data = import_data.get("tables", {})

        # If clearing, do it in reverse order (children first)
        if clear:
            logger.warning("Clearing existing data (in reverse dependency order)...")
            for table in reversed(TABLE_ORDER):
                if table in tables_data:
                    await conn.execute(f"DELETE FROM {table}")
                    logger.info(f"  Cleared {table}")

        # Import in correct order
        for table in TABLE_ORDER:
            if table not in tables_data:
                continue

            data = tables_data[table]
            if not data:
                continue

            logger.info(f"Importing {table}...")
            count = await import_table(conn, table, data, clear=False)
            logger.success(f"  Imported {count}/{len(data)} rows into {table}")

        total_rows = sum(len(data) for data in tables_data.values())
        logger.success(f"\nImport complete!")
        logger.info(f"  Total rows processed: {total_rows}")

    finally:
        await conn.close()


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export/import database seed data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to JSON")
    export_parser.add_argument(
        "--output", "-o",
        default="seed_data.json",
        help="Output JSON file (default: seed_data.json)",
    )
    export_parser.add_argument(
        "--tables", "-t",
        help="Comma-separated list of tables to export (default: all)",
    )

    # Import command
    import_parser = subparsers.add_parser("import", help="Import data from JSON")
    import_parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input JSON file",
    )
    import_parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before importing",
    )

    # Database connection options (for both commands)
    for sub in [export_parser, import_parser]:
        sub.add_argument("--host", default="localhost", help="Database host")
        sub.add_argument("--port", type=int, default=5432, help="Database port")
        sub.add_argument("--user", default="astro", help="Database user")
        sub.add_argument("--password", default="dev_password", help="Database password")
        sub.add_argument("--database", default="astro_dev", help="Database name")

    args = parser.parse_args()

    # Update DB config from args
    DB_CONFIG.update({
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": args.password,
        "database": args.database,
    })

    if args.command == "export":
        tables = args.tables.split(",") if args.tables else None
        await export_database(args.output, tables)
    elif args.command == "import":
        await import_database(args.input, args.clear)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DATABASE SEED SCRIPT")
    print("=" * 60 + "\n")
    asyncio.run(main())
