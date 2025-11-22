"""
Celery tasks for interpretation cache management.
"""

import asyncio
from datetime import datetime

from loguru import logger

from app.core.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.services.interpretation_cache_service import InterpretationCacheService


@celery_app.task(name="cache.cleanup_expired_interpretations")
def cleanup_expired_interpretations(ttl_days: int = 30) -> dict[str, int | str]:
    """
    Clean up expired interpretation cache entries.

    Removes cache entries that haven't been accessed within the TTL period.
    This helps manage database size while keeping frequently used interpretations.

    **Process**:
    1. Find cache entries with last_accessed_at older than TTL
    2. Delete expired entries
    3. Log statistics

    **Scheduling**: Run daily at 5 AM (low traffic period).

    Args:
        ttl_days: Time to live in days (default: 30)

    Returns:
        Dict with cleanup statistics
    """
    return asyncio.run(_cleanup_expired_interpretations_async(ttl_days))


async def _cleanup_expired_interpretations_async(ttl_days: int) -> dict[str, int | str]:
    """Async version of the cleanup task."""
    async with AsyncSessionLocal() as db:
        cache_service = InterpretationCacheService(db)

        # Get stats before cleanup
        stats_before = await cache_service.get_stats()
        entries_before = stats_before["total_entries"]

        # Clean up expired entries
        deleted_count = await cache_service.clear_expired(ttl_days)

        # Get stats after cleanup
        stats_after = await cache_service.get_stats()
        entries_after = stats_after["total_entries"]

        result = {
            "entries_before": entries_before,
            "entries_after": entries_after,
            "deleted_count": deleted_count,
            "ttl_days": ttl_days,
            "cleanup_time": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Cache cleanup completed: {deleted_count} entries deleted "
            f"(TTL: {ttl_days} days, {entries_before} -> {entries_after} entries)"
        )

        return result


@celery_app.task(name="cache.get_cache_statistics")
def get_cache_statistics() -> dict:
    """
    Get current cache statistics.

    Useful for monitoring and reporting.

    Returns:
        Dict with cache statistics
    """
    return asyncio.run(_get_cache_statistics_async())


async def _get_cache_statistics_async() -> dict:
    """Async version of the stats task."""
    async with AsyncSessionLocal() as db:
        cache_service = InterpretationCacheService(db)
        stats = await cache_service.get_stats()

        logger.info(
            f"Cache stats: {stats['total_entries']} entries, "
            f"{stats['total_hits']} total hits, "
            f"{stats['cache_hit_ratio']:.1f}% hit ratio, "
            f"~${stats['estimated_cost_savings_usd']:.4f} saved"
        )

        return stats


@celery_app.task(name="cache.clear_by_prompt_version")
def clear_cache_by_prompt_version(prompt_version: str) -> dict[str, int | str]:
    """
    Clear all cache entries for a specific prompt version.

    Call this task when updating prompt templates to force regeneration.

    Args:
        prompt_version: Version string to clear (e.g., "1.0", "2.0")

    Returns:
        Dict with cleanup statistics
    """
    return asyncio.run(_clear_by_prompt_version_async(prompt_version))


async def _clear_by_prompt_version_async(prompt_version: str) -> dict[str, int | str]:
    """Async version of the clear by version task."""
    async with AsyncSessionLocal() as db:
        cache_service = InterpretationCacheService(db)
        deleted_count = await cache_service.clear_by_prompt_version(prompt_version)

        result: dict[str, int | str] = {
            "prompt_version": prompt_version,
            "deleted_count": deleted_count,
            "cleanup_time": datetime.utcnow().isoformat(),
        }

        logger.info(
            f"Cache cleared for prompt version {prompt_version}: "
            f"{deleted_count} entries deleted"
        )

        return result
