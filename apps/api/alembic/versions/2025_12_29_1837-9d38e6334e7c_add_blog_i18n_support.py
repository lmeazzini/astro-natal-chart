"""add_blog_i18n_support

Revision ID: 9d38e6334e7c
Revises: a1b2c3d4e5f6
Create Date: 2025-12-29 18:37:18.885524

This migration adds internationalization (i18n) support to blog posts:
- locale: Language code (pt-BR or en-US)
- translation_key: Groups posts that are translations of each other

Default locale is pt-BR because:
1. The application was originally developed for Brazilian Portuguese users
2. All existing blog posts in the database are in Portuguese
3. The primary target audience is Portuguese-speaking

To add support for additional locales, update:
- apps/api/app/api/deps.py (SUPPORTED_LOCALES, LOCALE_PATTERN)
- apps/web/src/locales/ (add new language files)
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d38e6334e7c"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add locale column with default value
    op.add_column(
        "blog_posts", sa.Column("locale", sa.String(10), nullable=False, server_default="pt-BR")
    )

    # Add translation_key column for linking translations
    op.add_column("blog_posts", sa.Column("translation_key", sa.String(100), nullable=True))

    # Drop old unique index on slug
    # The unique constraint was created as an index named 'ix_blog_posts_slug'
    op.drop_index("ix_blog_posts_slug", table_name="blog_posts")

    # Add composite unique constraint (slug + locale)
    op.create_unique_constraint("blog_posts_slug_locale_key", "blog_posts", ["slug", "locale"])

    # Add indexes for efficient queries
    op.create_index("idx_blog_posts_locale", "blog_posts", ["locale"])
    op.create_index("idx_blog_posts_translation_key", "blog_posts", ["translation_key"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_blog_posts_translation_key", table_name="blog_posts")
    op.drop_index("idx_blog_posts_locale", table_name="blog_posts")

    # Drop composite unique constraint
    op.drop_constraint("blog_posts_slug_locale_key", "blog_posts", type_="unique")

    # Restore original unique index on slug
    op.create_index("ix_blog_posts_slug", "blog_posts", ["slug"], unique=True)

    # Drop columns
    op.drop_column("blog_posts", "translation_key")
    op.drop_column("blog_posts", "locale")
