"""
Blog post model for SEO-optimized content.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BlogPost(Base):
    """Blog post model for public content with SEO optimization."""

    __tablename__ = "blog_posts"
    __table_args__ = (
        # Composite unique constraint: slug must be unique per locale
        {"info": {"unique_constraints": [("slug", "locale")]}},
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # URL-friendly slug (e.g., "introducao-casas-astrologicas")
    # Note: Unique constraint is (slug, locale) - handled by migration
    slug: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
    )

    # Internationalization support
    locale: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="pt-BR",
        index=True,
    )
    translation_key: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # Content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Markdown content
    excerpt: Mapped[str] = mapped_column(
        String(300), nullable=False
    )  # Summary for meta description

    # Author (optional - for admin users)
    author_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Publishing
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Featured flag (for highlighting certain posts)
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    # Categorization
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        default=[],
        nullable=False,
    )

    # Media
    featured_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # SEO fields
    seo_title: Mapped[str | None] = mapped_column(String(70), nullable=True)  # Custom <title> tag
    seo_description: Mapped[str | None] = mapped_column(
        String(160), nullable=True
    )  # Meta description
    seo_keywords: Mapped[list[str] | None] = mapped_column(
        ARRAY(String(50)),
        nullable=True,
    )

    # Metrics
    read_time_minutes: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )  # Calculated from content
    views_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    author: Mapped["User | None"] = relationship("User", backref="blog_posts")

    def __repr__(self) -> str:
        return f"<BlogPost {self.slug}>"

    @property
    def is_published(self) -> bool:
        """Check if the post is published."""
        return self.published_at is not None

    @property
    def effective_seo_title(self) -> str:
        """Get the SEO title or fallback to regular title."""
        return self.seo_title or self.title

    @property
    def effective_seo_description(self) -> str:
        """Get the SEO description or fallback to excerpt."""
        return self.seo_description or self.excerpt

    @staticmethod
    def calculate_read_time(content: str) -> int:
        """Calculate read time in minutes (250 words per minute)."""
        word_count = len(content.split())
        return max(1, round(word_count / 250))

    @staticmethod
    def generate_slug(title: str) -> str:
        """Generate URL-friendly slug from title."""
        import re
        import unicodedata

        # Normalize unicode characters
        slug = unicodedata.normalize("NFKD", title.lower())
        # Remove accents
        slug = slug.encode("ascii", "ignore").decode("ascii")
        # Replace spaces and special characters with hyphens
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[-\s]+", "-", slug).strip("-")
        return slug
