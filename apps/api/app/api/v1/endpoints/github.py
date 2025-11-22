"""
GitHub API integration endpoints for dynamic feature lists.
"""

import json
from datetime import UTC, datetime
from typing import Any

import httpx
import redis.asyncio as aioredis
from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from app.core.config import settings

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


async def get_redis_client() -> Any | None:
    """Get Redis client for caching."""
    try:
        redis = aioredis.from_url(
            str(settings.REDIS_URL),
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await redis.ping()
        return redis
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {e}")
        return None


async def fetch_features_from_github() -> FeaturesResponse:
    """
    Fetch features from GitHub API based on issue labels.

    Labels expected:
    - 'implemented' or 'done': Completed features
    - 'in-progress' or 'doing': Features in development
    - 'planned' or 'backlog': Planned features
    """
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Add authentication if token is available (increases rate limit from 60 to 5000/hour)
    if settings.GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Fetch issues with 'feature' label
            response = await client.get(
                f"{GITHUB_API_URL}/repos/{settings.GITHUB_REPO}/issues",
                params={
                    "state": "all",
                    "labels": "feature",
                    "per_page": 100,
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
                logger.error(
                    f"GitHub API error: {response.status_code} - {response.text}"
                )
                raise HTTPException(
                    status_code=502,
                    detail="Failed to fetch from GitHub API",
                )

            issues = response.json()

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

    # Categorize by labels
    implemented: list[Feature] = []
    in_progress: list[Feature] = []
    planned: list[Feature] = []

    for issue in issues:
        labels = [label["name"].lower() for label in issue.get("labels", [])]

        feature = Feature(
            title=issue["title"],
            number=issue["number"],
            url=issue["html_url"],
            created_at=issue["created_at"],
            closed_at=issue.get("closed_at"),
        )

        if "implemented" in labels or "done" in labels:
            implemented.append(feature)
        elif "in-progress" in labels or "doing" in labels:
            in_progress.append(feature)
        elif "planned" in labels or "backlog" in labels:
            planned.append(feature)

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
    redis = await get_redis_client()

    # Try to get from cache
    if redis:
        try:
            cached = await redis.get(CACHE_KEY)
            if cached:
                logger.debug("Returning cached GitHub features")
                data = json.loads(cached)
                return FeaturesResponse(**data)
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")
        finally:
            await redis.aclose()

    # Fetch from GitHub API
    logger.info("Fetching features from GitHub API")
    features = await fetch_features_from_github()

    # Save to cache
    redis = await get_redis_client()
    if redis:
        try:
            await redis.setex(
                CACHE_KEY,
                settings.GITHUB_FEATURES_CACHE_TTL,
                features.model_dump_json(),
            )
            logger.debug(
                f"Cached GitHub features for {settings.GITHUB_FEATURES_CACHE_TTL}s"
            )
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")
        finally:
            await redis.aclose()

    return features


@router.delete(
    "/features/cache",
    status_code=204,
    summary="Clear features cache",
    description="Clears the cached GitHub features to force a refresh.",
)
async def clear_features_cache() -> None:
    """
    Clear the features cache.

    Useful for forcing a refresh after updating issue labels on GitHub.
    """
    redis = await get_redis_client()
    if redis:
        try:
            await redis.delete(CACHE_KEY)
            logger.info("GitHub features cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear Redis cache: {e}")
        finally:
            await redis.aclose()
