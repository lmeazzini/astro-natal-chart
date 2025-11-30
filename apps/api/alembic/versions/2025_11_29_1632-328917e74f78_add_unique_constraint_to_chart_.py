"""add_unique_constraint_to_chart_interpretations

Revision ID: 328917e74f78
Revises: 6965ccdd2487
Create Date: 2025-11-29 16:32:57.956392

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "328917e74f78"
down_revision: str | None = "6965ccdd2487"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add unique constraint to prevent duplicate interpretations."""
    # Add unique constraint on (chart_id, interpretation_type, subject, language)
    # This ensures only ONE interpretation per element per language per chart
    op.create_unique_constraint(
        "uq_chart_interpretation",
        "chart_interpretations",
        ["chart_id", "interpretation_type", "subject", "language"],
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_constraint("uq_chart_interpretation", "chart_interpretations", type_="unique")
