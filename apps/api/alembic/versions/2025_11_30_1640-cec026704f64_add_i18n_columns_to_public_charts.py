"""add_i18n_columns_to_public_charts

Revision ID: cec026704f64
Revises: 328917e74f78
Create Date: 2025-11-30 16:40:14.994395

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cec026704f64"
down_revision: str | None = "328917e74f78"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add new i18n JSONB columns
    op.add_column(
        "public_charts",
        sa.Column(
            "short_bio_i18n",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Multilingual short bio: {language: content}",
        ),
    )
    op.add_column(
        "public_charts",
        sa.Column(
            "highlights_i18n",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Multilingual highlights: {language: [items]}",
        ),
    )
    op.add_column(
        "public_charts",
        sa.Column(
            "meta_title_i18n",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Multilingual meta title: {language: title}",
        ),
    )
    op.add_column(
        "public_charts",
        sa.Column(
            "meta_description_i18n",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Multilingual meta description: {language: description}",
        ),
    )
    op.add_column(
        "public_charts",
        sa.Column(
            "meta_keywords_i18n",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Multilingual meta keywords: {language: [keywords]}",
        ),
    )

    # Backfill existing data to pt-BR (default language)
    op.execute("""
        UPDATE public_charts
        SET short_bio_i18n = jsonb_build_object('pt-BR', short_bio)
        WHERE short_bio IS NOT NULL AND short_bio_i18n IS NULL;
    """)
    op.execute("""
        UPDATE public_charts
        SET highlights_i18n = jsonb_build_object('pt-BR', highlights)
        WHERE highlights IS NOT NULL AND highlights_i18n IS NULL;
    """)
    op.execute("""
        UPDATE public_charts
        SET meta_title_i18n = jsonb_build_object('pt-BR', meta_title)
        WHERE meta_title IS NOT NULL AND meta_title_i18n IS NULL;
    """)
    op.execute("""
        UPDATE public_charts
        SET meta_description_i18n = jsonb_build_object('pt-BR', meta_description)
        WHERE meta_description IS NOT NULL AND meta_description_i18n IS NULL;
    """)
    op.execute("""
        UPDATE public_charts
        SET meta_keywords_i18n = jsonb_build_object('pt-BR', meta_keywords)
        WHERE meta_keywords IS NOT NULL AND meta_keywords_i18n IS NULL;
    """)


def downgrade() -> None:
    # Drop i18n JSONB columns
    op.drop_column("public_charts", "meta_keywords_i18n")
    op.drop_column("public_charts", "meta_description_i18n")
    op.drop_column("public_charts", "meta_title_i18n")
    op.drop_column("public_charts", "highlights_i18n")
    op.drop_column("public_charts", "short_bio_i18n")
