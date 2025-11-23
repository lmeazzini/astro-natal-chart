"""merge_migration_heads

Revision ID: 5fb21e5a57d8
Revises: 49c63f382487, time_format_183000
Create Date: 2025-11-23 00:53:20.834944

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = '5fb21e5a57d8'
down_revision: str | None = ('49c63f382487', 'time_format_183000')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
