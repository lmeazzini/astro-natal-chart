"""
Unified interpretation service coordinating all interpretation types.

This facade service orchestrates fetching all 5 interpretation types
(planets, houses, aspects, arabic_parts, growth) with intelligent caching.
"""

import asyncio
from typing import Any

from loguru import logger

from app.core.config import settings
from app.domain.interpretation import InterpretationMetadata, InterpretationResult
from app.services.unified.interpretation_fetcher_service import InterpretationFetcherService


class UnifiedInterpretationService:
    """
    Facade service coordinating all interpretation types.

    Responsibilities:
    - Orchestrate fetching all 5 types in parallel
    - Handle partial regeneration logic
    - Collect metadata statistics
    - Group results by type
    """

    def __init__(
        self,
        planet_fetcher: InterpretationFetcherService,
        house_fetcher: InterpretationFetcherService,
        aspect_fetcher: InterpretationFetcherService,
        arabic_part_fetcher: InterpretationFetcherService,
        growth_fetcher: InterpretationFetcherService,
    ):
        """
        Initialize unified service with fetchers for each type.

        Args:
            planet_fetcher: Fetcher for planet interpretations
            house_fetcher: Fetcher for house interpretations
            aspect_fetcher: Fetcher for aspect interpretations
            arabic_part_fetcher: Fetcher for Arabic Part interpretations
            growth_fetcher: Fetcher for growth suggestions
        """
        self.fetchers = {
            "planets": planet_fetcher,
            "houses": house_fetcher,
            "aspects": aspect_fetcher,
            "arabic_parts": arabic_part_fetcher,
            "growth": growth_fetcher,
        }

    async def get_all_interpretations(
        self,
        chart_id: Any,  # UUID
        chart_data: dict[str, Any],
        language: str = "pt-BR",
        regenerate_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Get all interpretation types with intelligent caching.

        This method:
        1. Prepares parallel fetch tasks for each interpretation
        2. Executes all tasks concurrently
        3. Groups results by type
        4. Calculates metadata statistics

        Args:
            chart_id: Chart UUID
            chart_data: Full chart data from BirthChart.chart_data
            language: Language code ('pt-BR' or 'en-US')
            regenerate_types: Optional list of types to force regenerate

        Returns:
            Dictionary with grouped interpretations and metadata
        """
        regenerate_types = regenerate_types or []

        # Prepare parallel tasks for each interpretation type
        tasks: list[asyncio.Task] = []

        # Planets (11 items)
        planets = chart_data.get("planets", [])
        for planet in planets:
            subject = planet.get("name", "")
            if not subject:
                continue
            force_regen = "planets" in regenerate_types
            task = asyncio.create_task(
                self.fetchers["planets"].fetch_or_generate(
                    chart_id=chart_id,
                    chart_data=chart_data,
                    interpretation_type="planet",
                    subject=subject,
                    language=language,
                    force_regenerate=force_regen,
                )
            )
            tasks.append(task)

        # Houses (12 items)
        houses = chart_data.get("houses", [])
        for house in houses:
            house_number = house.get("house", 0) or house.get("number", 0)
            if not house_number:
                continue
            subject = str(house_number)
            force_regen = "houses" in regenerate_types
            task = asyncio.create_task(
                self.fetchers["houses"].fetch_or_generate(
                    chart_id=chart_id,
                    chart_data=chart_data,
                    interpretation_type="house",
                    subject=subject,
                    language=language,
                    force_regenerate=force_regen,
                )
            )
            tasks.append(task)

        # Aspects (limited by RAG_MAX_ASPECTS)
        aspects = chart_data.get("aspects", [])
        max_aspects = getattr(settings, "RAG_MAX_ASPECTS", 30)
        for aspect in aspects[:max_aspects]:
            planet1 = aspect.get("planet1", "")
            planet2 = aspect.get("planet2", "")
            aspect_name = aspect.get("aspect", "")
            if not all([planet1, planet2, aspect_name]):
                continue
            subject = f"{planet1}-{aspect_name}-{planet2}"
            force_regen = "aspects" in regenerate_types
            task = asyncio.create_task(
                self.fetchers["aspects"].fetch_or_generate(
                    chart_id=chart_id,
                    chart_data=chart_data,
                    interpretation_type="aspect",
                    subject=subject,
                    language=language,
                    force_regenerate=force_regen,
                )
            )
            tasks.append(task)

        # Arabic Parts (4-14 items)
        arabic_parts = chart_data.get("arabic_parts", {})
        for part_key in arabic_parts:
            force_regen = "arabic_parts" in regenerate_types
            task = asyncio.create_task(
                self.fetchers["arabic_parts"].fetch_or_generate(
                    chart_id=chart_id,
                    chart_data=chart_data,
                    interpretation_type="arabic_part",
                    subject=part_key,
                    language=language,
                    force_regenerate=force_regen,
                )
            )
            tasks.append(task)

        # Growth Suggestions (1 item)
        force_regen_growth = "growth" in regenerate_types
        growth_task = asyncio.create_task(
            self.fetchers["growth"].fetch_or_generate(
                chart_id=chart_id,
                chart_data=chart_data,
                interpretation_type="growth",
                subject="summary",
                language=language,
                force_regenerate=force_regen_growth,
            )
        )
        tasks.append(growth_task)

        # Execute all tasks in parallel
        logger.info(f"Fetching {len(tasks)} interpretations in parallel for chart {chart_id}")
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Cast to expected type for mypy
        results: list[InterpretationResult | Exception] = [
            r
            if isinstance(r, InterpretationResult | Exception)
            else InterpretationResult(
                content="Error",
                subject="unknown",
                interpretation_type="unknown",
                source="error",
                prompt_version="unknown",
            )
            for r in raw_results
        ]

        # Group results by type
        grouped = self._group_results(results)

        # Calculate metadata
        metadata = self._calculate_metadata(results)

        return {
            **grouped,
            "metadata": metadata,
        }

    def _group_results(self, results: list[InterpretationResult | Exception]) -> dict[str, Any]:
        """
        Group interpretation results by type.

        Args:
            results: List of InterpretationResult or Exception

        Returns:
            Dictionary grouped by interpretation type
        """
        grouped: dict[str, Any] = {
            "planets": {},
            "houses": {},
            "aspects": {},
            "arabic_parts": {},
            "growth": None,
        }

        for result in results:
            # Handle exceptions
            if isinstance(result, Exception):
                logger.error(f"Interpretation generation failed: {result}")
                continue

            # Group by type
            if result.interpretation_type == "planet":
                grouped["planets"][result.subject] = result.to_dict()
            elif result.interpretation_type == "house":
                grouped["houses"][result.subject] = result.to_dict()
            elif result.interpretation_type == "aspect":
                grouped["aspects"][result.subject] = result.to_dict()
            elif result.interpretation_type == "arabic_part":
                grouped["arabic_parts"][result.subject] = result.to_dict()
            elif result.interpretation_type == "growth":
                # Growth is single object, not dict
                # rag_sources is a list containing the structured data dict
                growth_dict = result.to_dict()
                rag_sources_list = growth_dict.get("rag_sources", [])
                growth_data = rag_sources_list[0] if rag_sources_list else {}

                grouped["growth"] = {
                    "growth_points": growth_data.get("growth_points", []),
                    "challenges": growth_data.get("challenges", []),
                    "opportunities": growth_data.get("opportunities", []),
                    "purpose": growth_data.get("purpose"),
                    "summary": growth_dict.get("content", ""),
                }

        return grouped

    def _calculate_metadata(
        self, results: list[InterpretationResult | Exception]
    ) -> InterpretationMetadata:
        """
        Calculate metadata statistics from results.

        Args:
            results: List of InterpretationResult or Exception

        Returns:
            InterpretationMetadata with statistics
        """
        metadata = InterpretationMetadata()

        for result in results:
            if isinstance(result, Exception):
                continue

            metadata.total_items += 1

            # Count by source
            if result.source == "database":
                metadata.cache_hits_db += 1
            elif result.source == "cache":
                metadata.cache_hits_cache += 1
            elif result.source == "rag":
                metadata.rag_generations += 1

            # Count outdated
            if result.is_outdated:
                metadata.outdated_count += 1

            # Count RAG documents used
            if result.rag_sources:
                if isinstance(result.rag_sources, list):
                    metadata.documents_used += len(result.rag_sources)
                elif isinstance(result.rag_sources, dict):
                    # For growth suggestions, estimate document count
                    metadata.documents_used += 1

        # Set current prompt version (from first result)
        for result in results:
            if isinstance(result, Exception):
                continue
            metadata.prompt_version_current = result.prompt_version
            break

        logger.info(
            f"Interpretation stats: {metadata.total_items} total, "
            f"{metadata.cache_hits_db} DB, "
            f"{metadata.cache_hits_cache} cache, "
            f"{metadata.rag_generations} generated, "
            f"{metadata.outdated_count} outdated"
        )

        return metadata
