"""add subscriptions table

Revision ID: 6965ccdd2487
Revises: 55361a122379
Create Date: 2025-11-25 19:36:03.114737

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6965ccdd2487"
down_revision: str | None = "55361a122379"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create subscriptions table."""
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"], unique=False)
    op.create_index(op.f("ix_subscriptions_user_id"), "subscriptions", ["user_id"], unique=True)
    op.create_index(op.f("ix_subscriptions_status"), "subscriptions", ["status"], unique=False)
    op.create_index(
        op.f("ix_subscriptions_expires_at"), "subscriptions", ["expires_at"], unique=False
    )


def downgrade() -> None:
    """Drop subscriptions table."""
    op.drop_index(op.f("ix_subscriptions_expires_at"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_status"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_user_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")
    op.drop_table("subscriptions")
