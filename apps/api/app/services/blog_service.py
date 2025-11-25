"""
Blog service for business logic.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

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
)


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
    ) -> BlogPostListResponse:
        """Get paginated list of published posts."""
        posts, total = await self.repo.get_published(
            page=page, page_size=page_size, category=category, tag=tag
        )

        total_pages = (total + page_size - 1) // page_size

        return BlogPostListResponse(
            items=[BlogPostListItem.model_validate(post) for post in posts],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def get_post_by_slug(self, slug: str) -> BlogPostRead | None:
        """Get a published post by slug and increment views."""
        post = await self.repo.get_published_by_slug(slug)
        if post:
            await self.repo.increment_views(post.id)  # type: ignore[arg-type]
            return BlogPostRead.model_validate(post)
        return None

    async def get_post_by_slug_admin(self, slug: str) -> BlogPostRead | None:
        """Get any post by slug (admin view, no view increment)."""
        post = await self.repo.get_by_slug(slug)
        if post:
            return BlogPostRead.model_validate(post)
        return None

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

        # Ensure slug is unique
        counter = 1
        original_slug = slug
        while await self.repo.slug_exists(slug):
            slug = f"{original_slug}-{counter}"
            counter += 1

        # Calculate read time
        read_time = BlogPost.calculate_read_time(data.content)

        post = BlogPost(
            slug=slug,
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
            author_id=author_id,
        )

        # Publish if requested
        if data.published:
            from datetime import UTC, datetime

            post.published_at = datetime.now(UTC)

        created_post = await self.repo.create(post)
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

        return BlogPostRead.model_validate(post)

    async def delete_post(self, post_id: UUID) -> bool:
        """Delete a blog post."""
        post = await self.repo.get_by_id(post_id)
        if not post:
            return False

        await self.repo.delete(post)
        return True

    async def publish_post(self, post_id: UUID) -> BlogPostRead | None:
        """Publish a blog post."""
        post = await self.repo.publish(post_id)
        if post:
            return BlogPostRead.model_validate(post)
        return None

    async def unpublish_post(self, post_id: UUID) -> BlogPostRead | None:
        """Unpublish a blog post."""
        post = await self.repo.unpublish(post_id)
        if post:
            return BlogPostRead.model_validate(post)
        return None

    async def get_blog_metadata(self) -> BlogMetadata:
        """Get blog metadata (categories, tags, total posts)."""
        categories_data = await self.repo.get_categories_with_count()
        tags_data = await self.repo.get_popular_tags(limit=20)
        total = await self.repo.get_total_published_count()

        return BlogMetadata(
            categories=[
                BlogCategoryCount(category=cat, count=count) for cat, count in categories_data
            ],
            popular_tags=[BlogTagCount(tag=tag, count=count) for tag, count in tags_data],
            total_posts=total,
        )

    async def get_recent_posts(self, limit: int = 5) -> list[BlogPostListItem]:
        """Get recent published posts."""
        posts = await self.repo.get_recent_published(limit=limit)
        return [BlogPostListItem.model_validate(post) for post in posts]
