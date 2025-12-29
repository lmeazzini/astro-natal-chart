"""
Blog service for business logic.
"""

import json
from uuid import UUID

import redis.asyncio as aioredis
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.blog_post import BlogPost
from app.repositories.blog_repository import BlogRepository
from app.schemas.blog import (
    BlogCategoryCount,
    BlogMetadata,
    BlogPostCreate,
    BlogPostListItem,
    BlogPostListResponse,
    BlogPostRead,
    BlogPostUpdate,
    BlogTagCount,
    TranslationInfo,
)

# Redis connection pool (singleton)
_redis_pool: aioredis.ConnectionPool | None = None

# Cache settings
BLOG_METADATA_CACHE_KEY_PREFIX = "blog:metadata"
BLOG_METADATA_CACHE_TTL = 300  # 5 minutes


def _get_metadata_cache_key(locale: str | None) -> str:
    """Get cache key for blog metadata by locale."""
    if locale:
        return f"{BLOG_METADATA_CACHE_KEY_PREFIX}:{locale}"
    return f"{BLOG_METADATA_CACHE_KEY_PREFIX}:all"


def _get_redis_pool() -> aioredis.ConnectionPool:
    """Get or create Redis connection pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.ConnectionPool.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
            max_connections=10,
        )
    return _redis_pool


class BlogService:
    """Service for blog post operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = BlogRepository(db)

    async def get_published_posts(
        self,
        page: int = 1,
        page_size: int = 10,
        category: str | None = None,
        tag: str | None = None,
        locale: str | None = None,
    ) -> BlogPostListResponse:
        """Get paginated list of published posts."""
        posts, total = await self.repo.get_published(
            page=page, page_size=page_size, category=category, tag=tag, locale=locale
        )

        total_pages = (total + page_size - 1) // page_size

        return BlogPostListResponse(
            items=[BlogPostListItem.model_validate(post) for post in posts],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_post_by_slug(self, slug: str, locale: str | None = None) -> BlogPostRead | None:
        """Get a published post by slug and increment views."""
        post = await self.repo.get_published_by_slug(slug, locale=locale)
        if post:
            post_id = post.id  # type: ignore[assignment]
            await self.repo.increment_views(post_id)
            # Refetch post with relationships after increment_views commits
            post = await self.repo.get_published_by_slug(slug, locale=locale)
            if post:
                post_read = BlogPostRead.model_validate(post)
                # Fetch available translations
                post_read.available_translations = await self._get_translations(
                    post.translation_key, exclude_locale=post.locale
                )
                return post_read
        return None

    async def get_post_by_slug_admin(
        self, slug: str, locale: str | None = None
    ) -> BlogPostRead | None:
        """Get any post by slug (admin view, no view increment)."""
        post = await self.repo.get_by_slug(slug, locale=locale)
        if post:
            post_read = BlogPostRead.model_validate(post)
            # Fetch available translations
            post_read.available_translations = await self._get_translations(
                post.translation_key, exclude_locale=post.locale
            )
            return post_read
        return None

    async def _get_translations(
        self, translation_key: str | None, exclude_locale: str | None = None
    ) -> list[TranslationInfo]:
        """Get available translations for a post."""
        if not translation_key:
            return []
        translations = await self.repo.get_translations(
            translation_key, exclude_locale=exclude_locale
        )
        return [TranslationInfo(locale=t.locale, slug=t.slug, title=t.title) for t in translations]

    async def get_post_by_id(self, post_id: UUID) -> BlogPostRead | None:
        """Get a post by ID (admin view)."""
        post = await self.repo.get_by_id(post_id)
        if post:
            return BlogPostRead.model_validate(post)
        return None

    async def get_all_posts_admin(
        self,
        page: int = 1,
        page_size: int = 10,
        include_drafts: bool = True,
    ) -> BlogPostListResponse:
        """Get all posts including drafts (admin view)."""
        posts, total = await self.repo.get_all_admin(
            page=page, page_size=page_size, include_drafts=include_drafts
        )

        total_pages = (total + page_size - 1) // page_size

        return BlogPostListResponse(
            items=[BlogPostListItem.model_validate(post) for post in posts],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def create_post(
        self, data: BlogPostCreate, author_id: UUID | None = None
    ) -> BlogPostRead:
        """Create a new blog post."""
        # Generate slug if not provided
        slug = data.slug or BlogPost.generate_slug(data.title)

        # Ensure slug is unique for this locale
        counter = 1
        original_slug = slug
        while await self.repo.slug_exists(slug, locale=data.locale):
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Calculate read time
        read_time = BlogPost.calculate_read_time(data.content)

        post = BlogPost(
            slug=slug,
            locale=data.locale,
            translation_key=data.translation_key,
            title=data.title,
            subtitle=data.subtitle,
            content=data.content,
            excerpt=data.excerpt,
            category=data.category,
            tags=data.tags,
            featured_image_url=data.featured_image_url,
            seo_title=data.seo_title,
            seo_description=data.seo_description,
            seo_keywords=data.seo_keywords,
            read_time_minutes=read_time,
            is_featured=data.is_featured,
            author_id=author_id,
        )

        # Publish if requested
        if data.published:
            from datetime import UTC, datetime

            post.published_at = datetime.now(UTC)

        created_post = await self.repo.create(post)

        # Invalidate metadata cache when a new post is created
        await self.invalidate_metadata_cache()

        return BlogPostRead.model_validate(created_post)

    async def update_post(self, post_id: UUID, data: BlogPostUpdate) -> BlogPostRead | None:
        """Update a blog post."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle publishing/unpublishing
        if "published" in update_data:
            if update_data["published"] and not post.published_at:
                from datetime import UTC, datetime

                post.published_at = datetime.now(UTC)
            elif not update_data["published"] and post.published_at:
                post.published_at = None
            del update_data["published"]

        # Update fields
        for field, value in update_data.items():
            if hasattr(post, field):
                setattr(post, field, value)

        # Recalculate read time if content changed
        if "content" in update_data:
            post.read_time_minutes = BlogPost.calculate_read_time(post.content)

        await self.db.commit()
        await self.db.refresh(post)

        # Invalidate metadata cache when a post is updated
        await self.invalidate_metadata_cache()

        return BlogPostRead.model_validate(post)

    async def delete_post(self, post_id: UUID) -> bool:
        """Delete a blog post."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            return False

        await self.repo.delete(post)

        # Invalidate metadata cache when a post is deleted
        await self.invalidate_metadata_cache()

        return True

    async def publish_post(self, post_id: UUID) -> BlogPostRead | None:
        """Publish a blog post."""
        post = await self.repo.publish(post_id)
        if post:
            # Invalidate metadata cache when a post is published
            await self.invalidate_metadata_cache()
            return BlogPostRead.model_validate(post)
        return None

    async def unpublish_post(self, post_id: UUID) -> BlogPostRead | None:
        """Unpublish a blog post."""
        post = await self.repo.unpublish(post_id)
        if post:
            # Invalidate metadata cache when a post is unpublished
            await self.invalidate_metadata_cache()
            return BlogPostRead.model_validate(post)
        return None

    async def get_blog_metadata(self, locale: str | None = None) -> BlogMetadata:
        """Get blog metadata (categories, tags, total posts) with caching."""
        cache_key = _get_metadata_cache_key(locale)

        # Try to get from Redis cache
        try:
            redis_client = aioredis.Redis(connection_pool=_get_redis_pool())
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Blog metadata cache hit for locale={locale}")
                data = json.loads(cached_data)
                return BlogMetadata(**data)
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")

        # Cache miss - fetch from database
        logger.debug(f"Blog metadata cache miss for locale={locale}, fetching from database")
        categories_data = await self.repo.get_categories_with_count(locale=locale)
        tags_data = await self.repo.get_popular_tags(limit=20, locale=locale)
        total = await self.repo.get_total_published_count(locale=locale)

        metadata = BlogMetadata(
            categories=[
                BlogCategoryCount(category=cat, count=count) for cat, count in categories_data
            ],
            popular_tags=[BlogTagCount(tag=tag, count=count) for tag, count in tags_data],
            total_posts=total,
        )

        # Store in Redis cache
        try:
            redis_client = aioredis.Redis(connection_pool=_get_redis_pool())
            await redis_client.setex(
                cache_key,
                BLOG_METADATA_CACHE_TTL,
                metadata.model_dump_json(),
            )
            logger.debug(f"Blog metadata cached successfully for locale={locale}")
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")

        return metadata

    async def invalidate_metadata_cache(self) -> None:
        """Invalidate all blog metadata caches (all locales)."""
        try:
            redis_client = aioredis.Redis(connection_pool=_get_redis_pool())
            # Delete all locale-specific caches
            keys_to_delete = [
                _get_metadata_cache_key(None),  # "all" cache
                _get_metadata_cache_key("pt-BR"),
                _get_metadata_cache_key("en-US"),
            ]
            for key in keys_to_delete:
                await redis_client.delete(key)
            logger.debug("Blog metadata caches invalidated")
        except Exception as e:
            logger.warning(f"Redis cache invalidation failed: {e}")

    async def get_recent_posts(
        self, limit: int = 5, locale: str | None = None
    ) -> list[BlogPostListItem]:
        """Get recent published posts."""
        posts = await self.repo.get_recent_published(limit=limit, locale=locale)
        return [BlogPostListItem.model_validate(post) for post in posts]
