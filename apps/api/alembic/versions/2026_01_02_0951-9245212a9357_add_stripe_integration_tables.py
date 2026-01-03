"""add_stripe_integration_tables

Revision ID: 9245212a9357
Revises: 89f54823b8cd
Create Date: 2026-01-02 09:51:46.383808

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9245212a9357"
down_revision: str | None = "89f54823b8cd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add Stripe columns to subscriptions table (if not exist)
    conn = op.get_bind()

    # Check if plan_type column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'plan_type'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions",
            sa.Column("plan_type", sa.String(length=50), nullable=False, server_default="free"),
        )
        op.create_index(
            op.f("ix_subscriptions_plan_type"), "subscriptions", ["plan_type"], unique=False
        )

    # Check if stripe_customer_id column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_customer_id'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions", sa.Column("stripe_customer_id", sa.String(length=255), nullable=True)
        )
        op.create_index(
            op.f("ix_subscriptions_stripe_customer_id"),
            "subscriptions",
            ["stripe_customer_id"],
            unique=False,
        )

    # Check if stripe_subscription_id column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_subscription_id'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions",
            sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        )
        op.create_index(
            op.f("ix_subscriptions_stripe_subscription_id"),
            "subscriptions",
            ["stripe_subscription_id"],
            unique=True,
        )

    # Check if stripe_price_id column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_price_id'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions", sa.Column("stripe_price_id", sa.String(length=255), nullable=True)
        )

    # Check if current_period_start column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_start'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions",
            sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        )

    # Check if current_period_end column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_end'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions",
            sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        )

    # Check if cancel_at_period_end column exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'cancel_at_period_end'
    """)
    )
    if not result.fetchone():
        op.add_column(
            "subscriptions",
            sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default="false"),
        )

    # Tables payments and webhook_events were created manually - skip creation if they exist
    # (Tables already exist from previous session, just verify they have correct structure)


def downgrade() -> None:
    # Drop subscription columns
    conn = op.get_bind()

    # Check and drop each column if exists
    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'cancel_at_period_end'
    """)
    )
    if result.fetchone():
        op.drop_column("subscriptions", "cancel_at_period_end")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_end'
    """)
    )
    if result.fetchone():
        op.drop_column("subscriptions", "current_period_end")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'current_period_start'
    """)
    )
    if result.fetchone():
        op.drop_column("subscriptions", "current_period_start")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_price_id'
    """)
    )
    if result.fetchone():
        op.drop_column("subscriptions", "stripe_price_id")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_subscription_id'
    """)
    )
    if result.fetchone():
        op.drop_index(op.f("ix_subscriptions_stripe_subscription_id"), table_name="subscriptions")
        op.drop_column("subscriptions", "stripe_subscription_id")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'stripe_customer_id'
    """)
    )
    if result.fetchone():
        op.drop_index(op.f("ix_subscriptions_stripe_customer_id"), table_name="subscriptions")
        op.drop_column("subscriptions", "stripe_customer_id")

    result = conn.execute(
        sa.text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'subscriptions' AND column_name = 'plan_type'
    """)
    )
    if result.fetchone():
        op.drop_index(op.f("ix_subscriptions_plan_type"), table_name="subscriptions")
        op.drop_column("subscriptions", "plan_type")
