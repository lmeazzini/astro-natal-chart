"""
Blog post schemas for request/response validation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BlogPostBase(BaseModel):
    """Base schema for blog posts."""

    title: str = Field(..., min_length=1, max_length=255)
    subtitle: str | None = Field(None, max_length=500)
    content: str = Field(..., min_length=1)
    excerpt: str = Field(..., min_length=1, max_length=300)
    category: str = Field(..., min_length=1, max_length=50)
    tags: list[str] = Field(default_factory=list)
    featured_image_url: str | None = Field(None, max_length=500)
    seo_title: str | None = Field(None, max_length=70)
    seo_description: str | None = Field(None, max_length=160)
    seo_keywords: list[str] | None = None


class BlogPostCreate(BlogPostBase):
    """Schema for creating a blog post."""

    slug: str | None = Field(None, max_length=255)
    published: bool = False


class BlogPostUpdate(BaseModel):
    """Schema for updating a blog post."""

    title: str | None = Field(None, min_length=1, max_length=255)
    subtitle: str | None = Field(None, max_length=500)
    content: str | None = Field(None, min_length=1)
    excerpt: str | None = Field(None, min_length=1, max_length=300)
    category: str | None = Field(None, min_length=1, max_length=50)
    tags: list[str] | None = None
    featured_image_url: str | None = Field(None, max_length=500)
    seo_title: str | None = Field(None, max_length=70)
    seo_description: str | None = Field(None, max_length=160)
    seo_keywords: list[str] | None = None
    published: bool | None = None


class AuthorInfo(BaseModel):
    """Author information for blog posts."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str | None = None


class BlogPostRead(BaseModel):
    """Schema for reading a blog post (public view)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    subtitle: str | None
    content: str
    excerpt: str
    category: str
    tags: list[str]
    featured_image_url: str | None
    seo_title: str | None
    seo_description: str | None
    seo_keywords: list[str] | None
    read_time_minutes: int
    views_count: int
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: AuthorInfo | None = None

    @property
    def effective_seo_title(self) -> str:
        """Get the SEO title or fallback to regular title."""
        return self.seo_title or self.title

    @property
    def effective_seo_description(self) -> str:
        """Get the SEO description or fallback to excerpt."""
        return self.seo_description or self.excerpt


class BlogPostListItem(BaseModel):
    """Schema for blog post list item (summary view)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    title: str
    subtitle: str | None
    excerpt: str
    category: str
    tags: list[str]
    featured_image_url: str | None
    read_time_minutes: int
    views_count: int
    published_at: datetime | None
    created_at: datetime
    author: AuthorInfo | None = None


class BlogPostListResponse(BaseModel):
    """Response schema for paginated blog post list."""

    items: list[BlogPostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class BlogCategoryCount(BaseModel):
    """Category with post count."""

    category: str
    count: int


class BlogTagCount(BaseModel):
    """Tag with post count."""

    tag: str
    count: int


class BlogMetadata(BaseModel):
    """Blog metadata for sidebar/navigation."""

    categories: list[BlogCategoryCount]
    popular_tags: list[BlogTagCount]
    total_posts: int
