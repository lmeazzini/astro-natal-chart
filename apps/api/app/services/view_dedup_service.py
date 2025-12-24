"""
View deduplication service using Redis.

Prevents view count gaming by tracking recent views per IP/slug combination.
Only allows one view count increment per IP per chart within a time window.
"""

import hashlib

import redis
from loguru import logger

from app.core.config import settings

# View deduplication window in seconds (30 minutes)
VIEW_DEDUP_WINDOW_SECONDS = 30 * 60

# Redis key prefix for view deduplication
VIEW_DEDUP_KEY_PREFIX = "view_dedup:"

# Connection pool singleton (reused across requests for performance)
_redis_pool: redis.ConnectionPool | None = None


def _get_redis_pool() -> redis.ConnectionPool | None:
    """
    Get or create the Redis connection pool (singleton).

    Using a connection pool avoids the overhead of creating new connections
    for each request, significantly improving performance under load.

    Returns:
        Redis connection pool or None if creation fails
    """
    global _redis_pool
    if _redis_pool is None:
        try:
            _redis_pool = redis.ConnectionPool.from_url(
                str(settings.REDIS_URL), decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Failed to create Redis connection pool: {e}")
    return _redis_pool


def _generate_view_key(slug: str, client_ip: str) -> str:
    """
    Generate a unique Redis key for view tracking.

    Uses a hash of the IP to reduce key size and avoid storing raw IPs.

    Args:
        slug: Chart slug
        client_ip: Client IP address

    Returns:
        Redis key string
    """
    # Hash the IP for privacy and to reduce key size
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()[:16]
    return f"{VIEW_DEDUP_KEY_PREFIX}{slug}:{ip_hash}"


def should_increment_view(slug: str, client_ip: str) -> bool:
    """
    Check if view should be incremented (no recent view from this IP).

    Uses atomic SET NX operation to prevent race conditions where two
    concurrent requests could both pass an exists check.

    Args:
        slug: Chart slug
        client_ip: Client IP address

    Returns:
        True if view should be counted, False if already viewed recently
    """
    pool = _get_redis_pool()
    if not pool:
        # If Redis is unavailable, allow the increment (fail open)
        logger.debug("Redis pool unavailable, allowing view increment")
        return True

    try:
        client = redis.Redis(connection_pool=pool)
        key = _generate_view_key(slug, client_ip)

        # Atomic SET NX (set if not exists) with expiration
        # Returns True if key was set (new view), None if key already existed
        result = client.set(key, "1", ex=VIEW_DEDUP_WINDOW_SECONDS, nx=True)

        if result:
            logger.debug(f"View dedup: new view recorded ({slug})")
            return True
        else:
            logger.debug(f"View dedup: already viewed recently ({slug})")
            return False

    except Exception as e:
        logger.warning(f"Redis error in view deduplication: {e}")
        # On error, allow the increment (fail open)
        return True
