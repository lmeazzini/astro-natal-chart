"""
Tests for the InterpretationCacheService.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.interpretation_cache_service import InterpretationCacheService


class TestCacheKeyGeneration:
    """Tests for cache key generation."""

    def test_generate_cache_key_consistency(self):
        """Test that same parameters always generate same key."""
        params = {
            "planet": "Sun",
            "sign": "Aries",
            "house": 1,
            "dignities": {"is_exalted": True},
            "sect": "diurnal",
            "retrograde": False,
        }

        key1 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        key2 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        assert key1 == key2
        assert len(key1) == 64  # SHA-256 hex digest

    def test_generate_cache_key_different_params(self):
        """Test that different parameters generate different keys."""
        params1 = {"planet": "Sun", "sign": "Aries"}
        params2 = {"planet": "Moon", "sign": "Aries"}

        key1 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params1,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        key2 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params2,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        assert key1 != key2

    def test_generate_cache_key_different_model(self):
        """Test that different models generate different keys."""
        params = {"planet": "Sun", "sign": "Aries"}

        key1 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        key2 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o",
            prompt_version="1.0",
        )

        assert key1 != key2

    def test_generate_cache_key_different_prompt_version(self):
        """Test that different prompt versions generate different keys."""
        params = {"planet": "Sun", "sign": "Aries"}

        key1 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        key2 = InterpretationCacheService.generate_cache_key(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="2.0",
        )

        assert key1 != key2


class TestCacheOperations:
    """Tests for cache operations with database."""

    @pytest.mark.asyncio
    async def test_cache_miss_returns_none(self, db_session: AsyncSession):
        """Test that cache miss returns None."""
        cache_service = InterpretationCacheService(db_session)

        result = await cache_service.get(
            interpretation_type="planet",
            parameters={"planet": "Sun", "sign": "Aries"},
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_cache(self, db_session: AsyncSession):
        """Test storing and retrieving from cache."""
        cache_service = InterpretationCacheService(db_session)

        params = {"planet": "Sun", "sign": "Aries"}
        content = "This is a test interpretation for Sun in Aries."

        # Set cache
        cache_entry = await cache_service.set(
            interpretation_type="planet",
            subject="Sun",
            parameters=params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        assert cache_entry is not None
        assert cache_entry.content == content

        # Get from cache
        cached_content = await cache_service.get(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        assert cached_content == content

    @pytest.mark.asyncio
    async def test_hit_count_increments(self, db_session: AsyncSession):
        """Test that hit count increments on cache access."""
        cache_service = InterpretationCacheService(db_session)

        params = {"planet": "Moon", "sign": "Cancer"}
        content = "Moon in Cancer interpretation."

        # Set cache
        await cache_service.set(
            interpretation_type="planet",
            subject="Moon",
            parameters=params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        # Access multiple times
        await cache_service.get(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )
        await cache_service.get(
            interpretation_type="planet",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="1.0",
        )

        # Get stats to verify hit count
        stats = await cache_service.get_stats()
        assert stats["total_hits"] >= 2

    @pytest.mark.asyncio
    async def test_get_stats_empty_cache(self, db_session: AsyncSession):
        """Test getting stats from empty cache."""
        cache_service = InterpretationCacheService(db_session)

        stats = await cache_service.get_stats()

        assert stats["total_entries"] == 0
        assert stats["total_hits"] == 0
        assert stats["cache_hit_ratio"] == 0

    @pytest.mark.asyncio
    async def test_clear_all(self, db_session: AsyncSession):
        """Test clearing all cache entries."""
        cache_service = InterpretationCacheService(db_session)

        # Add some entries
        for planet in ["Sun", "Moon", "Mars"]:
            await cache_service.set(
                interpretation_type="planet",
                subject=planet,
                parameters={"planet": planet, "sign": "Aries"},
                content=f"{planet} interpretation",
                model="gpt-4o-mini",
                prompt_version="1.0",
            )

        # Verify entries exist
        stats_before = await cache_service.get_stats()
        assert stats_before["total_entries"] == 3

        # Clear all
        deleted = await cache_service.clear_all()
        assert deleted == 3

        # Verify empty
        stats_after = await cache_service.get_stats()
        assert stats_after["total_entries"] == 0

    @pytest.mark.asyncio
    async def test_clear_by_prompt_version(self, db_session: AsyncSession):
        """Test clearing cache by prompt version."""
        cache_service = InterpretationCacheService(db_session)

        # Add entries with different versions
        await cache_service.set(
            interpretation_type="planet",
            subject="Sun",
            parameters={"planet": "Sun"},
            content="v1.0 interpretation",
            model="gpt-4o-mini",
            prompt_version="1.0",
        )
        await cache_service.set(
            interpretation_type="planet",
            subject="Moon",
            parameters={"planet": "Moon"},
            content="v2.0 interpretation",
            model="gpt-4o-mini",
            prompt_version="2.0",
        )

        # Clear only v1.0
        deleted = await cache_service.clear_by_prompt_version("1.0")
        assert deleted == 1

        # Verify v2.0 still exists
        stats = await cache_service.get_stats()
        assert stats["total_entries"] == 1
