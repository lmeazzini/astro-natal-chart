"""add_public_chart_interpretations_table

Revision ID: 782ba409672f
Revises: 61837bbf83a1
Create Date: 2025-11-23 19:53:36.631755

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '782ba409672f'
down_revision: Union[str, None] = '61837bbf83a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create public_chart_interpretations table
    op.create_table('public_chart_interpretations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('chart_id', sa.UUID(), nullable=False),
        sa.Column('interpretation_type', sa.String(length=20), nullable=False, comment="Type: 'planet', 'house', 'aspect', or 'arabic_part'"),
        sa.Column('subject', sa.String(length=100), nullable=False, comment="e.g., 'Sun', '1', 'Sun-Trine-Moon', 'fortune'"),
        sa.Column('content', sa.Text(), nullable=False, comment='AI-generated interpretation text'),
        sa.Column('openai_model', sa.String(length=50), nullable=False, comment="OpenAI model used (e.g., 'gpt-4o-mini')"),
        sa.Column('prompt_version', sa.String(length=20), nullable=False, comment='Prompt version for tracking changes'),
        sa.Column('rag_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='RAG document sources used for this interpretation'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chart_id'], ['public_charts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_public_chart_interpretations_chart_id'), 'public_chart_interpretations', ['chart_id'], unique=False)
    op.create_index(op.f('ix_public_chart_interpretations_id'), 'public_chart_interpretations', ['id'], unique=False)
    op.create_index(op.f('ix_public_chart_interpretations_interpretation_type'), 'public_chart_interpretations', ['interpretation_type'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_public_chart_interpretations_interpretation_type'), table_name='public_chart_interpretations')
    op.drop_index(op.f('ix_public_chart_interpretations_id'), table_name='public_chart_interpretations')
    op.drop_index(op.f('ix_public_chart_interpretations_chart_id'), table_name='public_chart_interpretations')
    op.drop_table('public_chart_interpretations')
