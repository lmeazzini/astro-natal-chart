"""
GitHub API integration endpoints for dynamic feature lists.
"""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException, Request, Response
from loguru import logger
from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.config import settings
from app.core.rate_limit import RateLimits, limiter

router = APIRouter()


class Feature(BaseModel):
    """Feature item from GitHub issue."""

    title: str
    number: int
    url: str
    created_at: str
    closed_at: str | None = None


class FeaturesResponse(BaseModel):
    """Response with categorized features."""

    implemented: list[Feature]
    in_progress: list[Feature]
    planned: list[Feature]
    last_updated: str


CACHE_KEY = "github:features"
GITHUB_API_URL = "https://api.github.com"

# Redis connection pool (singleton)
_redis_pool: aioredis.ConnectionPool | None = None


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


@asynccontextmanager
async def get_redis_client() -> AsyncGenerator[Redis | None, None]:
    """Get Redis client from connection pool with automatic cleanup."""
    try:
        pool = _get_redis_pool()
        redis_client: Redis = Redis(connection_pool=pool)
        # Test connection
        await redis_client.ping()
        yield redis_client
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        yield None


async def fetch_all_feature_issues() -> list[dict]:
    """
    Fetch ALL issues with 'enhancement' label using pagination.

    GitHub API returns max 100 issues per page.
    Uses 'enhancement' label which is GitHub's default for new features.
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    all_issues: list[dict] = []
    page = 1
    per_page = 100

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                response = await client.get(
                    f"{GITHUB_API_URL}/repos/{settings.GITHUB_REPO}/issues",
                    params={
                        "state": "all",
                        "labels": "enhancement",
                        "per_page": per_page,
                        "page": page,
                    },
                    headers=headers,
                )

                if response.status_code == 403:
                    logger.warning("GitHub API rate limit exceeded")
                    raise HTTPException(
                        status_code=429,
                        detail="GitHub API rate limit exceeded. Try again later.",
                    )

                if response.status_code == 404:
                    logger.error(f"GitHub repository not found: {settings.GITHUB_REPO}")
                    raise HTTPException(
                        status_code=502,
                        detail="GitHub repository not found",
                    )

                if response.status_code != 200:
                    logger.error(f"GitHub API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=502,
                        detail="Failed to fetch from GitHub API",
                    )

                issues = response.json()

                if not issues:
                    break

                all_issues.extend(issues)

                # Check if there are more pages
                if len(issues) < per_page:
                    break

                page += 1

                # Safety limit to avoid infinite loops
                if page > 10:  # Max 1000 issues
                    logger.warning("Reached pagination limit (10 pages)")
                    break

            except httpx.TimeoutException as e:
                logger.error("GitHub API request timed out")
                raise HTTPException(
                    status_code=504,
                    detail="GitHub API request timed out",
                ) from e
            except httpx.RequestError as e:
                logger.error(f"GitHub API request failed: {e}")
                raise HTTPException(
                    status_code=502,
                    detail="Failed to connect to GitHub API",
                ) from e

    return all_issues


async def fetch_features_from_github() -> FeaturesResponse:
    """
    Fetch features from GitHub API based on issue state and labels.

    Categorization:
    - Closed issues → Implemented
    - Open issues with 'in-progress' or 'doing' label → In Progress
    - Open issues without those labels → Planned

    Falls back to state-based categorization if no status labels exist.
    """
    issues = await fetch_all_feature_issues()

    # Categorize by state and labels
    implemented: list[Feature] = []
    in_progress: list[Feature] = []
    planned: list[Feature] = []

    for issue in issues:
        labels = [label["name"].lower() for label in issue.get("labels", [])]
        state = issue.get("state", "").lower()

        feature = Feature(
            title=issue["title"],
            number=issue["number"],
            url=issue["html_url"],
            created_at=issue["created_at"],
            closed_at=issue.get("closed_at"),
        )

        # Check if it's closed (implemented)
        if state == "closed":
            implemented.append(feature)
        # Check for in-progress labels
        elif "in-progress" in labels or "doing" in labels:
            in_progress.append(feature)
        # Open issues without in-progress are planned
        else:
            planned.append(feature)

    # Sort by most recent first
    implemented.sort(key=lambda f: f.closed_at or f.created_at, reverse=True)
    in_progress.sort(key=lambda f: f.created_at, reverse=True)
    planned.sort(key=lambda f: f.created_at, reverse=True)

    return FeaturesResponse(
        implemented=implemented,
        in_progress=in_progress,
        planned=planned,
        last_updated=datetime.now(UTC).isoformat(),
    )


@router.get(
    "/features",
    response_model=FeaturesResponse,
    summary="Get project features",
    description="Fetches project features from GitHub issues, categorized by status labels.",
)
async def get_features() -> FeaturesResponse:
    """
    Get project features from GitHub.

    Features are categorized based on issue labels:
    - implemented/done: Completed features
    - in-progress/doing: Features in development
    - planned/backlog: Planned features

    Results are cached in Redis for 5 minutes to avoid hitting GitHub rate limits.
    """
    # Try to get from cache
    async with get_redis_client() as redis:
        if redis:
            try:
                cached = await redis.get(CACHE_KEY)
                if cached:
                    logger.debug("Returning cached GitHub features")
                    data = json.loads(cached)
                    return FeaturesResponse(**data)
            except Exception as e:
                logger.warning(f"Redis cache read failed: {e}")

    # Fetch from GitHub API
    logger.info("Fetching features from GitHub API")
    features = await fetch_features_from_github()

    # Save to cache
    async with get_redis_client() as redis:
        if redis:
            try:
                await redis.setex(
                    CACHE_KEY,
                    settings.GITHUB_FEATURES_CACHE_TTL,
                    features.model_dump_json(),
                )
                logger.debug(f"Cached GitHub features for {settings.GITHUB_FEATURES_CACHE_TTL}s")
            except Exception as e:
                logger.warning(f"Redis cache write failed: {e}")

    return features


@router.delete(
    "/features/cache",
    status_code=204,
    summary="Clear features cache",
    description="Clears the cached GitHub features to force a refresh. Rate limited to prevent abuse.",
)
@limiter.limit(RateLimits.CHART_DELETE)  # 30/hour - reasonable for cache clearing
async def clear_features_cache(request: Request, response: Response) -> None:
    """
    Clear the features cache.

    Useful for forcing a refresh after updating issue labels on GitHub.
    Rate limited to prevent abuse.
    """
    async with get_redis_client() as redis:
        if redis:
            try:
                await redis.delete(CACHE_KEY)
                logger.info("GitHub features cache cleared")
            except Exception as e:
                logger.warning(f"Failed to clear Redis cache: {e}")
