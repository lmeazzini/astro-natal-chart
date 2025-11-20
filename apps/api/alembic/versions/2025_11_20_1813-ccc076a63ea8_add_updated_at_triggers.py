"""add_updated_at_triggers

Revision ID: ccc076a63ea8
Revises: b0ef95f73d85
Create Date: 2025-11-20 18:13:17.272364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccc076a63ea8'
down_revision: Union[str, None] = 'b0ef95f73d85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a reusable trigger function for updating updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create triggers for each table with updated_at column
    # Users table
    op.execute("""
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Birth charts table
    op.execute("""
        CREATE TRIGGER update_birth_charts_updated_at
        BEFORE UPDATE ON birth_charts
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

    # Chart interpretations table
    op.execute("""
        CREATE TRIGGER update_chart_interpretations_updated_at
        BEFORE UPDATE ON chart_interpretations
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Drop all triggers
    op.execute("DROP TRIGGER IF EXISTS update_chart_interpretations_updated_at ON chart_interpretations")
    op.execute("DROP TRIGGER IF EXISTS update_birth_charts_updated_at ON birth_charts")
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users")

    # Drop the trigger function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
