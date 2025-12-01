"""
Public blog endpoints for SEO-optimized content.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import (
    BlogMetadata,
    BlogPostListItem,
    BlogPostListResponse,
    BlogPostRead,
)
from app.services.blog_service import BlogService

router = APIRouter(prefix="/blog", tags=["blog"])


@router.get("/posts", response_model=BlogPostListResponse)
async def list_posts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
    tag: str | None = Query(None, description="Filter by tag"),
    db: AsyncSession = Depends(get_db),
) -> BlogPostListResponse:
    """
    Get paginated list of published blog posts.

    Public endpoint - no authentication required.
    Supports filtering by category and tag.
    """
    service = BlogService(db)
    return await service.get_published_posts(
        page=page, page_size=page_size, category=category, tag=tag
    )


@router.get("/posts/{slug}", response_model=BlogPostRead)
async def get_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Get a single published blog post by slug.

    Public endpoint - no authentication required.
    Increments view count on each request.
    """
    service = BlogService(db)
    post = await service.get_post_by_slug(slug)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    return post


@router.get("/metadata", response_model=BlogMetadata)
async def get_blog_metadata(
    db: AsyncSession = Depends(get_db),
) -> BlogMetadata:
    """
    Get blog metadata including categories and popular tags.

    Public endpoint - no authentication required.
    Useful for sidebar navigation and filtering.
    """
    service = BlogService(db)
    return await service.get_blog_metadata()


@router.get("/recent", response_model=list[BlogPostListItem])
async def get_recent_posts(
    limit: int = Query(5, ge=1, le=20, description="Number of posts to return"),
    db: AsyncSession = Depends(get_db),
) -> list[BlogPostListItem]:
    """
    Get most recent published blog posts.

    Public endpoint - no authentication required.
    Useful for homepage widgets and sidebars.
    """
    service = BlogService(db)
    return await service.get_recent_posts(limit=limit)
