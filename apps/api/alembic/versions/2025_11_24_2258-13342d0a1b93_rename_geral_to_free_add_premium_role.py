"""rename_geral_to_free_add_premium_role

Revision ID: 13342d0a1b93
Revises: 9b5e1a052466
Create Date: 2025-11-24 22:58:36.898565

This migration:
1. Renames 'geral' role to 'free' in the users table
2. Adds support for 'premium' role (no schema change needed, just data migration)

The role column is a VARCHAR(20), so no enum constraint exists in the database.
New valid roles: 'free', 'premium', 'admin'
"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "13342d0a1b93"
down_revision: str | None = "9b5e1a052466"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Rename 'geral' to 'free' for all existing users
    op.execute("UPDATE users SET role = 'free' WHERE role = 'geral'")


def downgrade() -> None:
    # Revert 'free' back to 'geral'
    op.execute("UPDATE users SET role = 'geral' WHERE role = 'free'")
