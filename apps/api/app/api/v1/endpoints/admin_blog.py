"""
Admin blog endpoints for content management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.schemas.blog import (
    BlogPostCreate,
    BlogPostListResponse,
    BlogPostRead,
    BlogPostUpdate,
)
from app.services.blog_service import BlogService

router = APIRouter(prefix="/admin/blog", tags=["admin-blog"])


@router.get("/posts", response_model=BlogPostListResponse)
async def list_posts_admin(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=50, description="Items per page"),
    include_drafts: bool = Query(True, description="Include unpublished posts"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostListResponse:
    """
    Get paginated list of all blog posts (admin view).

    Requires admin role.
    Includes drafts by default.
    """
    service = BlogService(db)
    return await service.get_all_posts_admin(
        page=page, page_size=page_size, include_drafts=include_drafts
    )


@router.get("/posts/{post_id}", response_model=BlogPostRead)
async def get_post_admin(
    post_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Get a single blog post by ID (admin view).

    Requires admin role.
    Returns post regardless of published status.
    """
    service = BlogService(db)
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    return post


@router.post("/posts", response_model=BlogPostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: BlogPostCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Create a new blog post.

    Requires admin role.
    Slug is auto-generated from title if not provided.
    Set published=true to publish immediately.
    """
    service = BlogService(db)
    return await service.create_post(data, author_id=current_user.id)  # type: ignore[arg-type]


@router.put("/posts/{post_id}", response_model=BlogPostRead)
async def update_post(
    post_id: UUID,
    data: BlogPostUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Update a blog post.

    Requires admin role.
    Only provided fields are updated.
    """
    service = BlogService(db)
    post = await service.update_post(post_id, data)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a blog post.

    Requires admin role.
    This is a permanent deletion.
    """
    service = BlogService(db)
    deleted = await service.delete_post(post_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )


@router.post("/posts/{post_id}/publish", response_model=BlogPostRead)
async def publish_post(
    post_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Publish a blog post.

    Requires admin role.
    Sets published_at to current time.
    """
    service = BlogService(db)
    post = await service.publish_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    return post


@router.post("/posts/{post_id}/unpublish", response_model=BlogPostRead)
async def unpublish_post(
    post_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> BlogPostRead:
    """
    Unpublish a blog post.

    Requires admin role.
    Sets published_at to null.
    """
    service = BlogService(db)
    post = await service.unpublish_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found",
        )
    return post
