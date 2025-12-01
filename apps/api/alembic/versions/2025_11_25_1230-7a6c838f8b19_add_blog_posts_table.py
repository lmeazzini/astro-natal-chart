"""add blog_posts table

Revision ID: 7a6c838f8b19
Revises: 13342d0a1b93
Create Date: 2025-11-25 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a6c838f8b19"
down_revision: str | None = "13342d0a1b93"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Check if table already exists (for dev environments)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "blog_posts" in inspector.get_table_names():
        return

    op.create_table(
        "blog_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("subtitle", sa.String(500), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("excerpt", sa.String(300), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String(50)), nullable=False, server_default="{}"),
        sa.Column("featured_image_url", sa.String(500), nullable=True),
        sa.Column("seo_title", sa.String(70), nullable=True),
        sa.Column("seo_description", sa.String(160), nullable=True),
        sa.Column("seo_keywords", postgresql.ARRAY(sa.String(50)), nullable=True),
        sa.Column("read_time_minutes", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("views_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_blog_posts_id"), "blog_posts", ["id"], unique=False)
    op.create_index(op.f("ix_blog_posts_slug"), "blog_posts", ["slug"], unique=True)
    op.create_index(op.f("ix_blog_posts_author_id"), "blog_posts", ["author_id"], unique=False)
    op.create_index(
        op.f("ix_blog_posts_published_at"), "blog_posts", ["published_at"], unique=False
    )
    op.create_index(op.f("ix_blog_posts_category"), "blog_posts", ["category"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_blog_posts_category"), table_name="blog_posts")
    op.drop_index(op.f("ix_blog_posts_published_at"), table_name="blog_posts")
    op.drop_index(op.f("ix_blog_posts_author_id"), table_name="blog_posts")
    op.drop_index(op.f("ix_blog_posts_slug"), table_name="blog_posts")
    op.drop_index(op.f("ix_blog_posts_id"), table_name="blog_posts")
    op.drop_table("blog_posts")
