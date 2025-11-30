"""
Interpretation fetcher service implementing 3-tier cache hierarchy.

This service orchestrates the intelligent caching strategy:
Database → InterpretationCache → RAG Generation
"""

from typing import Any
from uuid import UUID

from loguru import logger

from app.domain.interfaces.interpretation_generator import IInterpretationGenerator
from app.domain.interfaces.interpretation_storage import IInterpretationStorage
from app.domain.interpretation import InterpretationResult


class InterpretationFetcherService:
    """
    Core service implementing 3-tier cache hierarchy.

    Hierarchy:
    1. Database (ChartInterpretation table) - fastest, chart-specific
    2. InterpretationCache - fast, shared across users
    3. RAG Generation - slowest, most expensive

    This service also handles:
    - Prompt version detection (marks outdated interpretations)
    - Async cache-to-DB backfill via Celery
    - Immediate DB persistence for fresh generations
    """

    def __init__(
        self,
        db_storage: IInterpretationStorage,
        cache_storage: IInterpretationStorage,
        generator: IInterpretationGenerator,
        current_prompt_version: str,
    ):
        """
        Initialize fetcher service.

        Args:
            db_storage: Database storage adapter
            cache_storage: Cache storage adapter
            generator: Interpretation generator adapter
            current_prompt_version: Current prompt version for outdated detection
        """
        self.db_storage = db_storage
        self.cache_storage = cache_storage
        self.generator = generator
        self.current_version = current_prompt_version

    async def fetch_or_generate(
        self,
        chart_id: UUID,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str = "pt-BR",
        force_regenerate: bool = False,
    ) -> InterpretationResult:
        """
        Fetch interpretation with 3-tier fallback.

        Flow:
        1. Check database → return if found (mark outdated if needed)
        2. Check cache → queue backfill + return if found
        3. Generate with RAG → save to DB + return

        Args:
            chart_id: Chart UUID
            chart_data: Complete chart data
            interpretation_type: Type to fetch/generate
            subject: Subject identifier
            language: Language code
            force_regenerate: If True, skip cache tiers and regenerate

        Returns:
            InterpretationResult from DB, cache, or fresh generation
        """
        if not force_regenerate:
            # Tier 1: Database lookup
            db_result = await self._check_database(chart_id, interpretation_type, subject, language)
            if db_result:
                return db_result

            # Tier 2: Cache lookup
            cache_result = await self._check_cache(
                chart_data, interpretation_type, subject, language
            )
            if cache_result:
                # Queue async backfill to database
                await self._queue_backfill(chart_id, cache_result, language)
                return cache_result

        # Tier 3: Generate with RAG
        result = await self._generate_fresh(chart_data, interpretation_type, subject, language)

        # Save to database immediately
        await self._save_to_database(chart_id, result, language)

        return result

    async def _check_database(
        self,
        chart_id: UUID,
        interpretation_type: str,
        subject: str,
        language: str,
    ) -> InterpretationResult | None:
        """
        Check database tier for interpretation.

        Args:
            chart_id: Chart UUID
            interpretation_type: Type to check
            subject: Subject identifier
            language: Language code

        Returns:
            InterpretationResult if found, None otherwise
        """
        try:
            db_results = await self.db_storage.get_by_chart(
                chart_id=chart_id,
                interpretation_type=interpretation_type,
                language=language,
            )

            # Find matching subject
            for result in db_results:
                if result.subject == subject:
                    # Mark as outdated if prompt version changed
                    result.is_outdated = result.prompt_version != self.current_version
                    result.source = "database"

                    if result.is_outdated:
                        logger.debug(
                            f"DB HIT (outdated): {interpretation_type}:{subject} "
                            f"(version: {result.prompt_version} vs {self.current_version})"
                        )
                    else:
                        logger.debug(f"DB HIT: {interpretation_type}:{subject}")

                    return result

            logger.debug(f"DB MISS: {interpretation_type}:{subject}")
            return None

        except Exception as e:
            logger.error(f"Database lookup error: {e}")
            return None

    async def _check_cache(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str,
    ) -> InterpretationResult | None:
        """
        Check cache tier for interpretation.

        Args:
            chart_data: Chart data for parameter extraction
            interpretation_type: Type to check
            subject: Subject identifier
            language: Language code

        Returns:
            InterpretationResult if found in cache, None otherwise
        """
        try:
            # Extract parameters for cache lookup
            parameters = self._extract_parameters(chart_data, interpretation_type, subject)

            # Lookup in cache
            cache_result = await self.cache_storage.get_single(
                interpretation_type=interpretation_type,
                parameters=parameters,
                model=self.generator.get_model_id(),
                version=self.current_version,
                language=language,
            )

            if cache_result:
                cache_result.source = "cache"
                logger.debug(f"Cache HIT: {interpretation_type}:{subject}")
                return cache_result

            logger.debug(f"Cache MISS: {interpretation_type}:{subject}")
            return None

        except Exception as e:
            logger.error(f"Cache lookup error: {e}")
            return None

    async def _generate_fresh(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str,
    ) -> InterpretationResult:
        """
        Generate fresh interpretation with RAG.

        Args:
            chart_data: Complete chart data
            interpretation_type: Type to generate
            subject: Subject identifier
            language: Language code

        Returns:
            Newly generated InterpretationResult
        """
        logger.debug(f"Generating fresh: {interpretation_type}:{subject}")

        result = await self.generator.generate(
            chart_data=chart_data,
            interpretation_type=interpretation_type,
            subject=subject,
            language=language,
        )

        result.source = "rag"
        return result

    async def _save_to_database(
        self,
        chart_id: UUID,
        interpretation: InterpretationResult,
        language: str,
    ) -> None:
        """
        Save interpretation to database.

        Args:
            chart_id: Chart UUID
            interpretation: InterpretationResult to save
            language: Language code
        """
        try:
            await self.db_storage.save(chart_id, interpretation, language)
            logger.debug(
                f"Saved to DB: {interpretation.interpretation_type}:{interpretation.subject}"
            )
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            # Don't raise - generation succeeded, just save failed

    async def _queue_backfill(
        self,
        chart_id: UUID,
        interpretation: InterpretationResult,
        language: str,
    ) -> None:
        """
        Queue Celery task to backfill cache→DB asynchronously.

        Args:
            chart_id: Chart UUID
            interpretation: InterpretationResult from cache
            language: Language code
        """
        try:
            from app.tasks.interpretation_tasks import backfill_interpretation_task

            # Queue async task
            backfill_interpretation_task.delay(
                chart_id=str(chart_id),
                interpretation_data=interpretation.to_dict(),
                language=language,
            )

            logger.debug(
                f"Queued backfill: {interpretation.interpretation_type}:{interpretation.subject}"
            )

        except Exception as e:
            logger.warning(f"Failed to queue backfill task: {e}")
            # Don't raise - cache hit succeeded, just backfill queuing failed

    def _extract_parameters(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
    ) -> dict[str, Any]:
        """
        Extract parameters for cache key generation.

        Args:
            chart_data: Complete chart data
            interpretation_type: Type of interpretation
            subject: Subject identifier

        Returns:
            Parameters dict for cache lookup
        """
        parameters: dict[str, Any] = {}

        if interpretation_type == "planet":
            planets = chart_data.get("planets", [])
            planet_data = next((p for p in planets if p.get("name") == subject), None)
            if planet_data:
                parameters = {
                    "sign": planet_data.get("sign", ""),
                    "house": planet_data.get("house", 1),
                    "retrograde": planet_data.get("retrograde", False),
                    "dignities": planet_data.get("dignities", {}),
                    "sect": chart_data.get("sect", "diurnal"),
                }

        elif interpretation_type == "house":
            houses = chart_data.get("houses", [])
            house_number = int(subject)
            house_data = next(
                (
                    h
                    for h in houses
                    if h.get("house", 0) == house_number or h.get("number", 0) == house_number
                ),
                None,
            )
            if house_data:
                parameters = {
                    "sign": house_data.get("sign", ""),
                    "sect": chart_data.get("sect", "diurnal"),
                }

        elif interpretation_type == "aspect":
            parts = subject.split("-")
            if len(parts) == 3:
                planet1, aspect_name, planet2 = parts
                parameters = {
                    "planet1": planet1,
                    "planet2": planet2,
                    "aspect": aspect_name,
                    "sect": chart_data.get("sect", "diurnal"),
                }

        elif interpretation_type == "arabic_part":
            arabic_parts = chart_data.get("arabic_parts", {})
            part_data = arabic_parts.get(subject, {})
            parameters = {
                "sign": part_data.get("sign", ""),
                "house": part_data.get("house", 1),
                "sect": chart_data.get("sect", "diurnal"),
            }

        elif interpretation_type == "growth":
            # Growth doesn't use cache (too complex, chart-specific)
            parameters = {}

        return parameters
