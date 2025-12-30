"""add subscription_history table

Revision ID: a1b2c3d4e5f6
Revises: cec026704f64
Create Date: 2025-12-23 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "cec026704f64"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create subscription_history table for tracking subscription changes."""
    op.create_table(
        "subscription_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subscription_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Snapshot of subscription state
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        # Change metadata
        sa.Column("change_type", sa.String(20), nullable=False),
        sa.Column("changed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        # Timestamp
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Foreign keys
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.id"],
            name="fk_subscription_history_subscription_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_subscription_history_user_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["users.id"],
            name="fk_subscription_history_changed_by_user_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_subscription_history_subscription_id"),
        "subscription_history",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_history_user_id"),
        "subscription_history",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_history_created_at"),
        "subscription_history",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop subscription_history table."""
    op.drop_index(
        op.f("ix_subscription_history_created_at"),
        table_name="subscription_history",
    )
    op.drop_index(
        op.f("ix_subscription_history_user_id"),
        table_name="subscription_history",
    )
    op.drop_index(
        op.f("ix_subscription_history_subscription_id"),
        table_name="subscription_history",
    )
    op.drop_table("subscription_history")
