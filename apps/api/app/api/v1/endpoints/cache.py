"""
API endpoints for interpretation cache management.

These endpoints allow administrators to view cache statistics and manage cache entries.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db  # type: ignore[import-untyped]
from app.models.user import User
from app.services.interpretation_cache_service import InterpretationCacheService

router = APIRouter()


class CacheStatsResponse(BaseModel):
    """Response model for cache statistics."""

    total_entries: int
    total_hits: int
    cache_hit_ratio: float
    entries_by_type: dict[str, int]
    oldest_entry: str | None
    newest_entry: str | None
    average_hits_per_entry: float
    estimated_cost_savings_usd: float
    openai_model: str


class CacheClearResponse(BaseModel):
    """Response model for cache clear operations."""

    deleted_count: int
    message: str


@router.get("/stats", response_model=CacheStatsResponse)
async def get_cache_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CacheStatsResponse:
    """
    Get interpretation cache statistics.

    Returns cache usage metrics including hit rates, entry counts,
    and estimated cost savings from caching.
    """
    cache_service = InterpretationCacheService(db)
    stats = await cache_service.get_stats()
    return CacheStatsResponse(**stats)


@router.delete("/expired", response_model=CacheClearResponse)
async def clear_expired_cache(
    ttl_days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CacheClearResponse:
    """
    Clear expired cache entries.

    Removes cache entries that haven't been accessed within the specified TTL.

    Args:
        ttl_days: Time to live in days (default: 30)
    """
    if ttl_days < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TTL must be at least 1 day",
        )

    cache_service = InterpretationCacheService(db)
    deleted = await cache_service.clear_expired(ttl_days)
    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared {deleted} cache entries older than {ttl_days} days",
    )


@router.delete("/prompt-version/{version}", response_model=CacheClearResponse)
async def clear_cache_by_prompt_version(
    version: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CacheClearResponse:
    """
    Clear cache entries for a specific prompt version.

    Useful when updating prompts to force regeneration of interpretations.

    Args:
        version: Prompt version to clear (e.g., "1.0", "2.0")
    """
    cache_service = InterpretationCacheService(db)
    deleted = await cache_service.clear_by_prompt_version(version)
    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared {deleted} cache entries for prompt version {version}",
    )


@router.delete("/all", response_model=CacheClearResponse)
async def clear_all_cache(
    confirm: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CacheClearResponse:
    """
    Clear all cache entries.

    WARNING: This will delete all cached interpretations and may increase
    OpenAI API costs significantly until the cache is rebuilt.

    Args:
        confirm: Must be True to confirm the operation
    """
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must pass confirm=true to clear all cache entries",
        )

    cache_service = InterpretationCacheService(db)
    deleted = await cache_service.clear_all()
    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared all {deleted} cache entries",
    )
