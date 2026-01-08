"""add_purchased_credits_to_user_credits

Revision ID: dfcc6df55b0d
Revises: fix_search_indices_constraint
Create Date: 2026-01-08 13:14:51.726819

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dfcc6df55b0d"
down_revision: str | None = "fix_search_indices_constraint"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add purchased_credits column to user_credits table
    op.add_column(
        "user_credits",
        sa.Column("purchased_credits", sa.Integer(), nullable=False, server_default="0"),
    )
    # Remove the server_default after column is created
    op.alter_column("user_credits", "purchased_credits", server_default=None)


def downgrade() -> None:
    op.drop_column("user_credits", "purchased_credits")
