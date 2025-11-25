"""
Blog post repository for database operations.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.blog_post import BlogPost
from app.repositories.base import BaseRepository


class BlogRepository(BaseRepository[BlogPost]):
    """Repository for blog post database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(BlogPost, db)

    def _base_query(self) -> Select[tuple[BlogPost]]:
        """Base query with author relationship loaded."""
        return select(BlogPost).options(selectinload(BlogPost.author))

    async def get_by_slug(self, slug: str) -> BlogPost | None:
        """Get a blog post by its URL slug."""
        stmt = self._base_query().where(BlogPost.slug == slug)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published_by_slug(self, slug: str) -> BlogPost | None:
        """Get a published blog post by its URL slug."""
        stmt = self._base_query().where(BlogPost.slug == slug, BlogPost.published_at.isnot(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_published(
        self,
        page: int = 1,
        page_size: int = 10,
        category: str | None = None,
        tag: str | None = None,
    ) -> tuple[list[BlogPost], int]:
        """
        Get paginated list of published blog posts.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            category: Optional category filter
            tag: Optional tag filter

        Returns:
            Tuple of (list of posts, total count)
        """
        base_filter = BlogPost.published_at.isnot(None)

        # Build query
        stmt = self._base_query().where(base_filter)

        if category:
            stmt = stmt.where(BlogPost.category == category)

        if tag:
            stmt = stmt.where(BlogPost.tags.contains([tag]))

        # Get total count
        count_stmt = select(func.count(BlogPost.id)).where(base_filter)
        if category:
            count_stmt = count_stmt.where(BlogPost.category == category)
        if tag:
            count_stmt = count_stmt.where(BlogPost.tags.contains([tag]))

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        stmt = stmt.order_by(BlogPost.published_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(stmt)
        posts = list(result.scalars().all())

        return posts, total

    async def get_all_admin(
        self,
        page: int = 1,
        page_size: int = 10,
        include_drafts: bool = True,
    ) -> tuple[list[BlogPost], int]:
        """
        Get paginated list of all blog posts (admin view).

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_drafts: Whether to include unpublished posts

        Returns:
            Tuple of (list of posts, total count)
        """
        stmt = self._base_query()
        count_stmt = select(func.count(BlogPost.id))

        if not include_drafts:
            stmt = stmt.where(BlogPost.published_at.isnot(None))
            count_stmt = count_stmt.where(BlogPost.published_at.isnot(None))

        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0

        # Order by created_at (most recent first), then published_at
        stmt = stmt.order_by(BlogPost.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(stmt)
        posts = list(result.scalars().all())

        return posts, total

    async def get_by_category(
        self, category: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[BlogPost], int]:
        """Get published posts by category."""
        return await self.get_published(page=page, page_size=page_size, category=category)

    async def get_by_tag(
        self, tag: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[BlogPost], int]:
        """Get published posts by tag."""
        return await self.get_published(page=page, page_size=page_size, tag=tag)

    async def get_categories_with_count(self) -> list[tuple[str, int]]:
        """Get all categories with their post counts (published only)."""
        stmt = (
            select(BlogPost.category, func.count(BlogPost.id))
            .where(BlogPost.published_at.isnot(None))
            .group_by(BlogPost.category)
            .order_by(func.count(BlogPost.id).desc())
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_popular_tags(self, limit: int = 20) -> list[tuple[str, int]]:
        """
        Get popular tags with their counts (published posts only).

        Uses PostgreSQL unnest to flatten the tags array.
        """
        stmt = (
            select(func.unnest(BlogPost.tags).label("tag"), func.count().label("count"))
            .where(BlogPost.published_at.isnot(None))
            .group_by("tag")
            .order_by(func.count().desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def get_recent_published(self, limit: int = 5) -> list[BlogPost]:
        """Get most recent published posts."""
        stmt = (
            self._base_query()
            .where(BlogPost.published_at.isnot(None))
            .order_by(BlogPost.published_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def increment_views(self, post_id: UUID) -> None:
        """Increment the view count for a post."""
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if post:
            post.views_count += 1
            await self.db.commit()

    async def publish(self, post_id: UUID) -> BlogPost | None:
        """Publish a blog post (set published_at to now)."""
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if post and not post.published_at:
            post.published_at = datetime.now(UTC)
            await self.db.commit()
            await self.db.refresh(post)
        return post

    async def unpublish(self, post_id: UUID) -> BlogPost | None:
        """Unpublish a blog post (set published_at to None)."""
        stmt = select(BlogPost).where(BlogPost.id == post_id)
        result = await self.db.execute(stmt)
        post = result.scalar_one_or_none()
        if post and post.published_at:
            post.published_at = None
            await self.db.commit()
            await self.db.refresh(post)
        return post

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Check if a slug already exists."""
        stmt = select(func.count(BlogPost.id)).where(BlogPost.slug == slug)
        if exclude_id:
            stmt = stmt.where(BlogPost.id != exclude_id)
        result = await self.db.execute(stmt)
        count = result.scalar() or 0
        return count > 0

    async def get_total_published_count(self) -> int:
        """Get total count of published posts."""
        stmt = select(func.count(BlogPost.id)).where(BlogPost.published_at.isnot(None))
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_all_published_for_sitemap(self) -> list[Row[Any]]:
        """Get all published posts for sitemap generation (minimal data)."""
        stmt = (
            select(BlogPost.slug, BlogPost.updated_at)
            .where(BlogPost.published_at.isnot(None))
            .order_by(BlogPost.published_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.all())

    async def get_all_published_for_rss(self, limit: int = 20) -> list[BlogPost]:
        """Get recent published posts for RSS feed."""
        stmt = (
            self._base_query()
            .where(BlogPost.published_at.isnot(None))
            .order_by(BlogPost.published_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
