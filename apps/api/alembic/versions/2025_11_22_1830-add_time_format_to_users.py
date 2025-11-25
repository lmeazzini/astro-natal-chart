"""add_time_format_to_users

Revision ID: time_format_183000
Revises: add_rag_160000
Create Date: 2025-11-22 18:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "time_format_183000"
down_revision: str | None = "add_rag_160000"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add time_format column to users table with default value '24h'
    op.add_column(
        "users", sa.Column("time_format", sa.String(length=5), nullable=False, server_default="24h")
    )


def downgrade() -> None:
    # Remove time_format column from users table
    op.drop_column("users", "time_format")
