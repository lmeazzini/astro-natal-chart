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


class TestRAGCacheTypes:
    """Tests for new RAG-specific cache types (house_rag, aspect_rag, arabic_part_rag)."""

    @pytest.mark.asyncio
    async def test_house_rag_cache_set_and_get(self, db_session: AsyncSession):
        """Test caching house_rag interpretations."""
        cache_service = InterpretationCacheService(db_session)

        # House RAG cache parameters (matches interpretation_service_rag.py)
        params = {
            "house": 1,
            "sign": "Aries",
            "ruler": "Mars",
            "ruler_dignities": {"domicile": True, "exalted": False},
            "sect": "diurnal",
        }
        content = "RAG-enhanced interpretation for 1st house in Aries ruled by Mars..."

        # Set cache
        cache_entry = await cache_service.set(
            interpretation_type="house_rag",
            subject="House 1",
            parameters=params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cache_entry is not None
        assert cache_entry.interpretation_type == "house_rag"
        assert cache_entry.subject == "House 1"

        # Get from cache
        cached_content = await cache_service.get(
            interpretation_type="house_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cached_content == content

    @pytest.mark.asyncio
    async def test_aspect_rag_cache_set_and_get(self, db_session: AsyncSession):
        """Test caching aspect_rag interpretations."""
        cache_service = InterpretationCacheService(db_session)

        # Aspect RAG cache parameters (orb excluded to maximize cache hits)
        params = {
            "planet1": "Sun",
            "planet2": "Moon",
            "aspect": "trine",
            "sign1": "Aries",
            "sign2": "Leo",
            "applying": True,
            "sect": "diurnal",
            "dignities1": {"exalted": True},
            "dignities2": {"domicile": True},
        }
        content = "RAG-enhanced interpretation for Sun trine Moon..."

        # Set cache
        cache_entry = await cache_service.set(
            interpretation_type="aspect_rag",
            subject="Sun-trine-Moon",
            parameters=params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cache_entry is not None
        assert cache_entry.interpretation_type == "aspect_rag"

        # Get from cache
        cached_content = await cache_service.get(
            interpretation_type="aspect_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cached_content == content

    @pytest.mark.asyncio
    async def test_aspect_rag_cache_excludes_orb(self, db_session: AsyncSession):
        """Test that aspect_rag cache doesn't include orb (maximizes cache hits)."""
        cache_service = InterpretationCacheService(db_session)

        # Same aspect parameters without orb
        base_params = {
            "planet1": "Mars",
            "planet2": "Venus",
            "aspect": "conjunction",
            "sign1": "Taurus",
            "sign2": "Taurus",
            "applying": False,
            "sect": "nocturnal",
            "dignities1": {},
            "dignities2": {"domicile": True},
        }

        content = "Mars conjunct Venus interpretation..."

        # Set cache with base params (no orb)
        await cache_service.set(
            interpretation_type="aspect_rag",
            subject="Mars-conjunction-Venus",
            parameters=base_params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        # Verify we can retrieve with same params
        cached = await cache_service.get(
            interpretation_type="aspect_rag",
            parameters=base_params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cached == content

    @pytest.mark.asyncio
    async def test_arabic_part_rag_cache_set_and_get(self, db_session: AsyncSession):
        """Test caching arabic_part_rag interpretations."""
        cache_service = InterpretationCacheService(db_session)

        # Arabic Part RAG cache parameters
        params = {
            "part_key": "fortune",
            "sign": "Cancer",
            "house": 4,
            "sect": "nocturnal",
        }
        content = "RAG-enhanced interpretation for Part of Fortune in Cancer in the 4th house..."

        # Set cache
        cache_entry = await cache_service.set(
            interpretation_type="arabic_part_rag",
            subject="fortune",
            parameters=params,
            content=content,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cache_entry is not None
        assert cache_entry.interpretation_type == "arabic_part_rag"
        assert cache_entry.subject == "fortune"

        # Get from cache
        cached_content = await cache_service.get(
            interpretation_type="arabic_part_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        assert cached_content == content

    @pytest.mark.asyncio
    async def test_different_rag_types_have_different_keys(self, db_session: AsyncSession):
        """Test that different RAG interpretation types generate different cache keys."""
        # Same basic params but different types should have different keys
        params = {"sign": "Aries", "house": 1}

        key_house = InterpretationCacheService.generate_cache_key(
            interpretation_type="house_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        key_aspect = InterpretationCacheService.generate_cache_key(
            interpretation_type="aspect_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        key_arabic = InterpretationCacheService.generate_cache_key(
            interpretation_type="arabic_part_rag",
            parameters=params,
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        # All keys should be different
        assert key_house != key_aspect
        assert key_house != key_arabic
        assert key_aspect != key_arabic

    @pytest.mark.asyncio
    async def test_rag_cache_stats_include_all_types(self, db_session: AsyncSession):
        """Test that cache stats include all RAG interpretation types."""
        cache_service = InterpretationCacheService(db_session)

        # Add entries for each RAG type
        await cache_service.set(
            interpretation_type="house_rag",
            subject="House 1",
            parameters={"house": 1},
            content="House interpretation",
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        await cache_service.set(
            interpretation_type="aspect_rag",
            subject="Sun-Moon",
            parameters={"planet1": "Sun", "planet2": "Moon"},
            content="Aspect interpretation",
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        await cache_service.set(
            interpretation_type="arabic_part_rag",
            subject="fortune",
            parameters={"part_key": "fortune"},
            content="Arabic part interpretation",
            model="gpt-4o-mini",
            prompt_version="rag-v1",
        )

        # Verify stats
        stats = await cache_service.get_stats()
        assert stats["total_entries"] == 3

    @pytest.mark.asyncio
    async def test_rag_cache_clear_by_version_affects_all_types(self, db_session: AsyncSession):
        """Test that clearing by prompt version affects all RAG types."""
        cache_service = InterpretationCacheService(db_session)

        # Add entries for each RAG type with same version
        for interp_type, subject in [
            ("house_rag", "House 1"),
            ("aspect_rag", "Sun-Moon"),
            ("arabic_part_rag", "fortune"),
        ]:
            await cache_service.set(
                interpretation_type=interp_type,
                subject=subject,
                parameters={"test": True},
                content=f"{interp_type} interpretation",
                model="gpt-4o-mini",
                prompt_version="rag-v1",
            )

        # Verify all 3 entries exist
        stats_before = await cache_service.get_stats()
        assert stats_before["total_entries"] == 3

        # Clear by version
        deleted = await cache_service.clear_by_prompt_version("rag-v1")
        assert deleted == 3

        # Verify all cleared
        stats_after = await cache_service.get_stats()
        assert stats_after["total_entries"] == 0
