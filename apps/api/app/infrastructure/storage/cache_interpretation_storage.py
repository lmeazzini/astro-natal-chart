"""
Cache storage adapter for interpretations.

This module implements the IInterpretationStorage interface using
the InterpretationCacheService for fast, parameter-based lookups.
"""

from typing import Any
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interfaces.interpretation_storage import IInterpretationStorage
from app.domain.interpretation import InterpretationResult
from app.services.interpretation_cache_service import InterpretationCacheService


class CacheInterpretationStorage(IInterpretationStorage):
    """
    Cache adapter implementing IInterpretationStorage.

    This adapter wraps the InterpretationCacheService to provide
    domain-layer access to cached interpretations with parameter-based lookups.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize cache storage adapter.

        Args:
            db: SQLAlchemy async database session (for cache table access)
        """
        self.cache_service = InterpretationCacheService(db)

    async def get_by_chart(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str = "pt-BR",
    ) -> list[InterpretationResult]:
        """
        Get interpretations from cache by chart ID.

        Note: InterpretationCache doesn't store by chart_id, only by parameters.
        This method returns empty list. Use get_single() for cache lookups.

        Args:
            chart_id: Chart UUID (not used for cache lookups)
            interpretation_type: Type filter (not used for cache lookups)
            language: Language code (not used for cache lookups)

        Returns:
            Empty list (cache doesn't support chart-based retrieval)
        """
        # Cache storage doesn't support chart-based lookups
        # It only supports parameter-based lookups via get_single()
        return []

    async def save(
        self,
        chart_id: UUID,
        interpretation: InterpretationResult,
        language: str = "pt-BR",
    ) -> None:
        """
        Save interpretation to cache.

        Note: Cache saves happen automatically during generation.
        This method is a no-op for cache storage.

        Args:
            chart_id: Chart UUID (not used)
            interpretation: InterpretationResult (not used)
            language: Language code (not used)
        """
        # Cache storage saves happen during RAG generation
        # via InterpretationServiceRAG, not through this interface
        pass

    async def delete(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str | None = None,
    ) -> int:
        """
        Delete interpretations from cache.

        Note: Cache deletion is not chart-specific.
        This method is a no-op for cache storage.

        Args:
            chart_id: Chart UUID (not used)
            interpretation_type: Type filter (not used)
            language: Language filter (not used)

        Returns:
            0 (cache doesn't support chart-based deletion)
        """
        # Cache storage doesn't support chart-based deletion
        # Cache entries are managed by TTL and prompt version invalidation
        return 0

    async def get_single(
        self,
        interpretation_type: str,
        parameters: dict[str, Any],
        model: str,
        version: str,
        language: str,
    ) -> InterpretationResult | None:
        """
        Get single interpretation from cache by parameters.

        This is the primary cache lookup method, using parameter hashing
        to find cached interpretations.

        Args:
            interpretation_type: Type of interpretation
            parameters: Parameters dict for cache key generation
            model: OpenAI model identifier
            version: Prompt version
            language: Language code

        Returns:
            InterpretationResult if found in cache, None otherwise
        """
        try:
            # Lookup in cache using parameters
            # Note: cache_service.get() returns just content string, not full model
            cache_content = await self.cache_service.get(
                interpretation_type=interpretation_type,
                parameters=parameters,
                model=model,
                prompt_version=version,
                language=language,
            )

            if not cache_content:
                logger.debug(
                    f"Cache MISS: {interpretation_type} with params {list(parameters.keys())}"
                )
                return None

            # Cache HIT - construct domain model from cached content
            # Extract subject from parameters (best effort - different types have different keys)
            subject: str = "unknown"
            if "planet" in parameters:
                subject = str(parameters["planet"])
            elif "house" in parameters:
                subject = str(parameters["house"])
            elif "planet1" in parameters and "planet2" in parameters:
                subject = f"{parameters['planet1']}-{parameters.get('aspect', 'unknown')}-{parameters['planet2']}"  # noqa: E501
            elif "part_key" in parameters:
                subject = str(parameters["part_key"])

            logger.debug(f"Cache HIT: {interpretation_type}:{subject}")

            return InterpretationResult(
                content=cache_content,
                subject=subject,
                interpretation_type=interpretation_type,
                source="cache",
                rag_sources=None,  # Cache doesn't store RAG sources
                prompt_version=version,
                is_outdated=False,
                cached=True,
                generated_at=None,  # Cache service doesn't track generation time
                openai_model=model,
            )

        except Exception as e:
            logger.error(f"Error fetching from cache for {interpretation_type}: {e}")
            # Return None on cache errors (fallback to RAG generation)
            return None
