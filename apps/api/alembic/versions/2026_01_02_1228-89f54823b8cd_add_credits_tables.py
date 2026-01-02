"""add_credits_tables

Revision ID: 89f54823b8cd
Revises: 9d38e6334e7c
Create Date: 2026-01-02 12:28:05.875650

Creates the credit system tables for tracking user credits and transactions.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "89f54823b8cd"
down_revision: str | None = "9d38e6334e7c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create user_credits table
    op.create_table(
        "user_credits",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_type", sa.String(20), nullable=False),
        sa.Column("credits_balance", sa.Integer(), nullable=False),
        sa.Column("credits_limit", sa.Integer(), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="user_credits_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_user_credits_id", "user_credits", ["id"], unique=False)
    op.create_index("ix_user_credits_user_id", "user_credits", ["user_id"], unique=True)
    op.create_index("ix_user_credits_plan_type", "user_credits", ["plan_type"], unique=False)

    # Create credit_transactions table
    op.create_table(
        "credit_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("balance_after", sa.Integer(), nullable=False),
        sa.Column("feature_type", sa.String(50), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="credit_transactions_user_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_credit_transactions_user_id",
        "credit_transactions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_credit_transactions_transaction_type",
        "credit_transactions",
        ["transaction_type"],
        unique=False,
    )
    op.create_index(
        "ix_credit_transactions_feature_type",
        "credit_transactions",
        ["feature_type"],
        unique=False,
    )
    op.create_index(
        "ix_credit_transactions_created_at",
        "credit_transactions",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    # Drop credit_transactions table
    op.drop_index("ix_credit_transactions_created_at", table_name="credit_transactions")
    op.drop_index("ix_credit_transactions_feature_type", table_name="credit_transactions")
    op.drop_index("ix_credit_transactions_transaction_type", table_name="credit_transactions")
    op.drop_index("ix_credit_transactions_user_id", table_name="credit_transactions")
    op.drop_table("credit_transactions")

    # Drop user_credits table
    op.drop_index("ix_user_credits_plan_type", table_name="user_credits")
    op.drop_index("ix_user_credits_user_id", table_name="user_credits")
    op.drop_index("ix_user_credits_id", table_name="user_credits")
    op.drop_table("user_credits")
