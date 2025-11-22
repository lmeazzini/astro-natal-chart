"""add_rag_vector_documents_and_search_indices

Revision ID: add_rag_160000
Revises: 93b7ace49920
Create Date: 2025-11-22 16:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'add_rag_160000'
down_revision: str | None = '93b7ace49920'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create vector_documents table
    op.create_table('vector_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collection_name', sa.String(100), nullable=False),
        sa.Column('document_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False, default=0),
        sa.Column('total_chunks', sa.Integer(), nullable=False, default=1),
        sa.Column('doc_metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('vector_id', sa.String(100), nullable=True),
        sa.Column('embedding_model', sa.String(100), nullable=True),
        sa.Column('bm25_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('vector_id')
    )

    # Create indexes for vector_documents
    op.create_index('idx_vector_documents_collection_type', 'vector_documents', ['collection_name', 'document_type'])
    op.create_index('idx_vector_documents_vector_id', 'vector_documents', ['vector_id'])
    op.create_index('idx_vector_documents_created_at', 'vector_documents', ['created_at'])
    op.create_index('idx_vector_documents_collection_name', 'vector_documents', ['collection_name'])
    op.create_index('idx_vector_documents_document_type', 'vector_documents', ['document_type'])

    # Create search_indices table
    op.create_table('search_indices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('index_name', sa.String(100), nullable=False),
        sa.Column('index_type', sa.String(50), nullable=False, default='bm25'),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tokens', sa.Text(), nullable=False),
        sa.Column('token_frequencies', sa.JSON(), nullable=False, default={}),
        sa.Column('k1', sa.Float(), nullable=False, default=1.2),
        sa.Column('b', sa.Float(), nullable=False, default=0.75),
        sa.Column('doc_length', sa.Integer(), nullable=False, default=0),
        sa.Column('doc_metadata', sa.JSON(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('index_name')
    )

    # Create indexes for search_indices
    op.create_index('idx_search_indices_document_id', 'search_indices', ['document_id'])
    op.create_index('idx_search_indices_index_name', 'search_indices', ['index_name'])


def downgrade() -> None:
    # Drop indexes for search_indices
    op.drop_index('idx_search_indices_index_name', 'search_indices')
    op.drop_index('idx_search_indices_document_id', 'search_indices')

    # Drop search_indices table
    op.drop_table('search_indices')

    # Drop indexes for vector_documents
    op.drop_index('idx_vector_documents_document_type', 'vector_documents')
    op.drop_index('idx_vector_documents_collection_name', 'vector_documents')
    op.drop_index('idx_vector_documents_created_at', 'vector_documents')
    op.drop_index('idx_vector_documents_vector_id', 'vector_documents')
    op.drop_index('idx_vector_documents_collection_type', 'vector_documents')

    # Drop vector_documents table
    op.drop_table('vector_documents')
