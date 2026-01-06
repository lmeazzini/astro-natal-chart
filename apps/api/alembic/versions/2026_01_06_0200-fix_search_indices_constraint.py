"""fix_search_indices_unique_constraint

Revision ID: fix_search_indices_constraint
Revises: 9245212a9357
Create Date: 2026-01-06 02:00:00.000000

Fixes the unique constraint on search_indices table.
The original constraint on (index_name) was incorrect - it should be on
(index_name, document_id) to allow multiple documents per index while
preventing duplicate entries for the same document.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_search_indices_constraint"
down_revision: str | None = "9245212a9357"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Drop the incorrect unique constraint on index_name only
    op.drop_constraint("search_indices_index_name_key", "search_indices", type_="unique")

    # Create correct unique constraint on (index_name, document_id)
    op.create_unique_constraint(
        "uq_search_indices_index_document",
        "search_indices",
        ["index_name", "document_id"],
    )


def downgrade() -> None:
    # Drop the correct constraint
    op.drop_constraint("uq_search_indices_index_document", "search_indices", type_="unique")

    # Recreate the original (incorrect) constraint
    op.create_unique_constraint(
        "search_indices_index_name_key",
        "search_indices",
        ["index_name"],
    )
