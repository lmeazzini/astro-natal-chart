"""
API endpoints for interpretation cache management.

These endpoints allow administrators to view cache statistics and manage cache entries.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.rate_limit import RateLimits, limiter
from app.models.chart import AuditLog
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


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


async def _create_audit_log(
    db: AsyncSession,
    user: User,
    action: str,
    extra_data: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Create audit log entry for cache operations."""
    audit_log = AuditLog(
        user_id=user.id,
        action=action,
        resource_type="interpretation_cache",
        ip_address=ip_address,
        extra_data=extra_data,
    )
    db.add(audit_log)
    await db.commit()
    logger.info(f"Audit log created: {action} by user {user.id}")


@router.get("/stats", response_model=CacheStatsResponse)
@limiter.limit(RateLimits.CACHE_STATS)
async def get_cache_stats(
    request: Request,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
@limiter.limit(RateLimits.CACHE_CLEAR)
async def clear_expired_cache(
    request: Request,
    ttl_days: int = 30,
    current_user: Annotated[User, Depends(require_admin)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> CacheClearResponse:
    """
    Clear expired cache entries. **Admin only.**

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

    # Audit log
    await _create_audit_log(
        db=db,
        user=current_user,
        action="cache_cleared_expired",
        extra_data={"ttl_days": ttl_days, "deleted_count": deleted},
        ip_address=_get_client_ip(request),
    )

    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared {deleted} cache entries older than {ttl_days} days",
    )


@router.delete("/prompt-version/{version}", response_model=CacheClearResponse)
@limiter.limit(RateLimits.CACHE_CLEAR)
async def clear_cache_by_prompt_version(
    request: Request,
    version: str,
    current_user: Annotated[User, Depends(require_admin)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> CacheClearResponse:
    """
    Clear cache entries for a specific prompt version. **Admin only.**

    Useful when updating prompts to force regeneration of interpretations.

    Args:
        version: Prompt version to clear (e.g., "1.0", "2.0")
    """
    cache_service = InterpretationCacheService(db)
    deleted = await cache_service.clear_by_prompt_version(version)

    # Audit log
    await _create_audit_log(
        db=db,
        user=current_user,
        action="cache_cleared_by_version",
        extra_data={"prompt_version": version, "deleted_count": deleted},
        ip_address=_get_client_ip(request),
    )

    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared {deleted} cache entries for prompt version {version}",
    )


@router.delete("/all", response_model=CacheClearResponse)
@limiter.limit(RateLimits.CACHE_CLEAR)
async def clear_all_cache(
    request: Request,
    confirm: bool = False,
    current_user: Annotated[User, Depends(require_admin)] = None,  # type: ignore[assignment]
    db: Annotated[AsyncSession, Depends(get_db)] = None,  # type: ignore[assignment]
) -> CacheClearResponse:
    """
    Clear all cache entries. **Admin only.**

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

    # Audit log
    await _create_audit_log(
        db=db,
        user=current_user,
        action="cache_cleared_all",
        extra_data={"deleted_count": deleted},
        ip_address=_get_client_ip(request),
    )

    return CacheClearResponse(
        deleted_count=deleted,
        message=f"Cleared all {deleted} cache entries",
    )
