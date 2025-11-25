"""
Service for managing AI interpretation cache.

This service provides caching functionality to reduce OpenAI API costs
by storing and reusing interpretations for identical inputs.
"""

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.interpretation_cache import InterpretationCache


class InterpretationCacheService:
    """Service for managing interpretation cache operations."""

    # Default cache TTL: 30 days
    DEFAULT_TTL_DAYS = 30

    def __init__(self, db: AsyncSession):
        """
        Initialize cache service.

        Args:
            db: Database session
        """
        self.db = db

    @staticmethod
    def generate_cache_key(
        interpretation_type: str,
        parameters: dict[str, Any],
        model: str,
        prompt_version: str,
        language: str = "pt-BR",
    ) -> str:
        """
        Generate a unique cache key from interpretation parameters.

        Args:
            interpretation_type: Type of interpretation ('planet', 'house', 'aspect')
            parameters: Dictionary of parameters used for interpretation
            model: OpenAI model name
            prompt_version: Version of the prompt template
            language: Language code for the interpretation (e.g., 'pt-BR', 'en-US')

        Returns:
            SHA-256 hash string (64 characters)
        """
        # Create a normalized, deterministic string from parameters
        key_data = {
            "type": interpretation_type,
            "params": parameters,
            "model": model,
            "prompt_version": prompt_version,
            "language": language,
        }
        # Sort keys to ensure consistent ordering
        key_string = json.dumps(key_data, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def get(
        self,
        interpretation_type: str,
        parameters: dict[str, Any],
        model: str,
        prompt_version: str,
        language: str = "pt-BR",
    ) -> str | None:
        """
        Get cached interpretation if available.

        Args:
            interpretation_type: Type of interpretation
            parameters: Dictionary of parameters
            model: OpenAI model name
            prompt_version: Version of prompt template
            language: Language code for the interpretation (e.g., 'pt-BR', 'en-US')

        Returns:
            Cached interpretation content or None if not found
        """
        cache_key = self.generate_cache_key(
            interpretation_type, parameters, model, prompt_version, language
        )

        stmt = select(InterpretationCache).where(
            InterpretationCache.cache_key == cache_key
        )
        result = await self.db.execute(stmt)
        cache_entry = result.scalar_one_or_none()

        if cache_entry:
            # Update hit count and last accessed time
            update_stmt = (
                update(InterpretationCache)
                .where(InterpretationCache.id == cache_entry.id)
                .values(
                    hit_count=InterpretationCache.hit_count + 1,
                    last_accessed_at=func.now(),
                )
            )
            await self.db.execute(update_stmt)
            await self.db.commit()

            logger.debug(
                f"Cache HIT for {interpretation_type}: {cache_entry.subject} "
                f"(hits: {cache_entry.hit_count + 1})"
            )
            return cache_entry.content

        logger.debug(f"Cache MISS for {interpretation_type} with key {cache_key[:8]}...")
        return None

    async def set(
        self,
        interpretation_type: str,
        subject: str,
        parameters: dict[str, Any],
        content: str,
        model: str,
        prompt_version: str,
        language: str = "pt-BR",
    ) -> InterpretationCache:
        """
        Store interpretation in cache.

        Args:
            interpretation_type: Type of interpretation
            subject: Subject identifier (e.g., 'Sun', '1', 'Sun-Trine-Moon')
            parameters: Dictionary of parameters
            content: Generated interpretation text
            model: OpenAI model name
            prompt_version: Version of prompt template
            language: Language code for the interpretation (e.g., 'pt-BR', 'en-US')

        Returns:
            Created cache entry
        """
        cache_key = self.generate_cache_key(
            interpretation_type, parameters, model, prompt_version, language
        )

        cache_entry = InterpretationCache(
            cache_key=cache_key,
            interpretation_type=interpretation_type,
            subject=subject,
            content=content,
            parameters_json=json.dumps(parameters, ensure_ascii=False),
            openai_model=model,
            prompt_version=prompt_version,
        )

        try:
            self.db.add(cache_entry)
            await self.db.commit()
            await self.db.refresh(cache_entry)

            logger.info(
                f"Cached new interpretation for {interpretation_type}: {subject}"
            )
            return cache_entry
        except IntegrityError:
            # Race condition: another request already created this entry
            await self.db.rollback()
            logger.debug(f"Cache entry already exists for key {cache_key[:8]}... (race condition)")

            # Fetch and return the existing entry
            existing = await self.db.execute(
                select(InterpretationCache).where(
                    InterpretationCache.cache_key == cache_key
                )
            )
            existing_entry = existing.scalar_one_or_none()
            if existing_entry:
                return existing_entry

            # If somehow still not found, re-raise (shouldn't happen)
            raise

    async def delete(self, cache_id: UUID) -> bool:
        """
        Delete a specific cache entry.

        Args:
            cache_id: UUID of cache entry to delete

        Returns:
            True if deleted, False if not found
        """
        stmt = delete(InterpretationCache).where(InterpretationCache.id == cache_id)
        result = await self.db.execute(stmt)
        await self.db.commit()

        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted cache entry {cache_id}")
        return deleted

    async def clear_expired(self, ttl_days: int | None = None) -> int:
        """
        Clear cache entries older than TTL.

        Args:
            ttl_days: Time to live in days (default: 30)

        Returns:
            Number of entries deleted
        """
        ttl = ttl_days or self.DEFAULT_TTL_DAYS
        cutoff_date = datetime.now(UTC) - timedelta(days=ttl)

        stmt = delete(InterpretationCache).where(
            InterpretationCache.last_accessed_at < cutoff_date
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleared {count} expired cache entries (TTL: {ttl} days)")
        return count

    async def clear_by_prompt_version(self, prompt_version: str) -> int:
        """
        Clear all cache entries for a specific prompt version.

        Useful when updating prompts to force regeneration.

        Args:
            prompt_version: Prompt version to clear

        Returns:
            Number of entries deleted
        """
        stmt = delete(InterpretationCache).where(
            InterpretationCache.prompt_version == prompt_version
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        count = result.rowcount
        if count > 0:
            logger.info(f"Cleared {count} cache entries for prompt version {prompt_version}")
        return count

    async def clear_all(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries deleted
        """
        stmt = delete(InterpretationCache)
        result = await self.db.execute(stmt)
        await self.db.commit()

        count = result.rowcount
        logger.warning(f"Cleared ALL {count} cache entries")
        return count

    async def get_stats(self) -> dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        # Total entries
        total_stmt = select(func.count(InterpretationCache.id))
        total_result = await self.db.execute(total_stmt)
        total_entries = total_result.scalar() or 0

        # Total hits
        hits_stmt = select(func.sum(InterpretationCache.hit_count))
        hits_result = await self.db.execute(hits_stmt)
        total_hits = hits_result.scalar() or 0

        # Entries by type
        type_stmt = select(
            InterpretationCache.interpretation_type,
            func.count(InterpretationCache.id).label("count"),
        ).group_by(InterpretationCache.interpretation_type)
        type_result = await self.db.execute(type_stmt)
        entries_by_type = {row.interpretation_type: row.count for row in type_result}

        # Oldest and newest entries
        oldest_stmt = select(func.min(InterpretationCache.created_at))
        oldest_result = await self.db.execute(oldest_stmt)
        oldest_entry = oldest_result.scalar()

        newest_stmt = select(func.max(InterpretationCache.created_at))
        newest_result = await self.db.execute(newest_stmt)
        newest_entry = newest_result.scalar()

        # Average hit count
        avg_hits_stmt = select(func.avg(InterpretationCache.hit_count))
        avg_hits_result = await self.db.execute(avg_hits_stmt)
        avg_hits = avg_hits_result.scalar() or 0

        # Estimated cost savings (assuming $0.00015 per 1K input tokens, $0.0006 per 1K output)
        # Average prompt ~500 tokens, response ~300 tokens
        # Cost per call: (0.5 * 0.00015) + (0.3 * 0.0006) = $0.000255
        estimated_savings = (total_hits - total_entries) * 0.000255 if total_hits > total_entries else 0

        return {
            "total_entries": total_entries,
            "total_hits": total_hits,
            "cache_hit_ratio": round(
                (total_hits - total_entries) / total_hits * 100, 2
            ) if total_hits > 0 else 0,
            "entries_by_type": entries_by_type,
            "oldest_entry": oldest_entry.isoformat() if oldest_entry else None,
            "newest_entry": newest_entry.isoformat() if newest_entry else None,
            "average_hits_per_entry": round(float(avg_hits), 2),
            "estimated_cost_savings_usd": round(estimated_savings, 4),
            "openai_model": settings.OPENAI_MODEL,
        }
