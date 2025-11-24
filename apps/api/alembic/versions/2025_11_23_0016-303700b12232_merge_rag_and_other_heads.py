"""merge_rag_and_other_heads

Revision ID: 303700b12232
Revises: a353cbccb342
Create Date: 2025-11-23 00:16:31.604960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '303700b12232'
down_revision: Union[str, None] = 'a353cbccb342'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
