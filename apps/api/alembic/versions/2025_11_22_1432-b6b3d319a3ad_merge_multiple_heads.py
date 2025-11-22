"""merge_multiple_heads

Revision ID: b6b3d319a3ad
Revises: 44bae117595b, 99dbbd3990dd, 2f5d48c07f14
Create Date: 2025-11-22 14:32:05.414400

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = 'b6b3d319a3ad'
down_revision: str | None = ('44bae117595b', '99dbbd3990dd', '2f5d48c07f14')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
