"""
RAG-based interpretation generator adapter.

This module implements the IInterpretationGenerator interface using
the InterpretationServiceRAG for RAG-enhanced AI generation.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger

from app.domain.interfaces.interpretation_generator import IInterpretationGenerator
from app.domain.interpretation import InterpretationResult
from app.services.interpretation_service_rag import (
    RAG_MODEL_ID,
    RAG_PROMPT_VERSION,
    InterpretationServiceRAG,
)


class RAGInterpretationGenerator(IInterpretationGenerator):
    """
    RAG adapter implementing IInterpretationGenerator.

    This adapter wraps the InterpretationServiceRAG to provide
    domain-layer access to RAG-enhanced interpretation generation.
    """

    def __init__(self, rag_service: InterpretationServiceRAG):
        """
        Initialize RAG generator adapter.

        Args:
            rag_service: Configured InterpretationServiceRAG instance
        """
        self.rag_service = rag_service

    async def generate(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str = "pt-BR",
    ) -> InterpretationResult:
        """
        Generate interpretation using RAG service.

        Delegates to the appropriate RAG method based on interpretation type.

        Args:
            chart_data: Complete birth chart data
            interpretation_type: Type to generate ('planet', 'house', 'aspect', 'arabic_part')
            subject: Subject identifier (e.g., 'Sun', '1', 'Sun-trine-Moon', 'fortune')
            language: Language code for generation

        Returns:
            InterpretationResult with generated content

        Raises:
            ValueError: If interpretation_type is unsupported
        """
        try:
            # Delegate to appropriate generator method
            if interpretation_type == "planet":
                content = await self._generate_planet(chart_data, subject)
            elif interpretation_type == "house":
                content = await self._generate_house(chart_data, subject)
            elif interpretation_type == "aspect":
                content = await self._generate_aspect(chart_data, subject)
            elif interpretation_type == "arabic_part":
                content = await self._generate_arabic_part(chart_data, subject)
            else:
                raise ValueError(f"Unsupported interpretation type: {interpretation_type}")

            return InterpretationResult(
                content=content,
                subject=subject,
                interpretation_type=interpretation_type,
                source="rag",
                rag_sources=None,  # RAG sources tracked separately in service
                prompt_version=self.get_prompt_version(),
                is_outdated=False,
                cached=False,
                generated_at=datetime.now(UTC),
                openai_model=self.get_model_id(),
            )

        except Exception as e:
            logger.error(
                f"Error generating {interpretation_type} interpretation for {subject}: {e}"
            )
            raise

    async def _generate_planet(self, chart_data: dict[str, Any], planet_name: str) -> str:
        """
        Generate planet interpretation.

        Args:
            chart_data: Complete chart data
            planet_name: Planet name (e.g., 'Sun', 'Moon')

        Returns:
            Generated interpretation text
        """
        # Find planet data
        planets = chart_data.get("planets", [])
        planet_data = next((p for p in planets if p.get("name") == planet_name), None)

        if not planet_data:
            raise ValueError(f"Planet {planet_name} not found in chart data")

        # Extract parameters
        sign = planet_data.get("sign", "")
        house = planet_data.get("house", 1)
        retrograde = planet_data.get("retrograde", False)
        dignities = planet_data.get("dignities", {})
        sect = chart_data.get("sect", "diurnal")

        # Call RAG service
        return await self.rag_service.generate_planet_interpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            dignities=dignities,
            sect=sect,
            retrograde=retrograde,
        )

    async def _generate_house(self, chart_data: dict[str, Any], house_number_str: str) -> str:
        """
        Generate house interpretation.

        Args:
            chart_data: Complete chart data
            house_number_str: House number as string (e.g., '1', '12')

        Returns:
            Generated interpretation text
        """
        from app.astro.dignities import get_sign_ruler

        house_number = int(house_number_str)

        # Find house data
        houses = chart_data.get("houses", [])
        house_data = next(
            (
                h
                for h in houses
                if h.get("house", 0) == house_number or h.get("number", 0) == house_number
            ),
            None,
        )

        if not house_data:
            raise ValueError(f"House {house_number} not found in chart data")

        # Extract parameters
        house_sign = house_data.get("sign", "")
        ruler = get_sign_ruler(house_sign) or "Unknown"
        sect = chart_data.get("sect", "diurnal")

        # Find ruler's dignities from planet data
        planets = chart_data.get("planets", [])
        ruler_dignities: dict[str, Any] = {}
        for planet_data in planets:
            if planet_data.get("name") == ruler:
                ruler_dignities = planet_data.get("dignities", {})
                break

        # Call RAG service
        return await self.rag_service.generate_house_interpretation(
            house=house_number,
            sign=house_sign,
            ruler=ruler,
            ruler_dignities=ruler_dignities,
            sect=sect,
        )

    async def _generate_aspect(self, chart_data: dict[str, Any], aspect_key: str) -> str:
        """
        Generate aspect interpretation.

        Args:
            chart_data: Complete chart data
            aspect_key: Aspect key (e.g., 'Sun-trine-Moon')

        Returns:
            Generated interpretation text
        """
        # Parse aspect key
        parts = aspect_key.split("-")
        if len(parts) != 3:
            raise ValueError(f"Invalid aspect key format: {aspect_key}")

        planet1_name, aspect_name, planet2_name = parts

        # Find aspect data
        aspects = chart_data.get("aspects", [])
        aspect_data = next(
            (
                a
                for a in aspects
                if a.get("planet1") == planet1_name
                and a.get("aspect") == aspect_name
                and a.get("planet2") == planet2_name
            ),
            None,
        )

        if not aspect_data:
            raise ValueError(f"Aspect {aspect_key} not found in chart data")

        # Extract parameters
        orb = aspect_data.get("orb", 0.0)
        applying = aspect_data.get("applying", False)
        sect = chart_data.get("sect", "diurnal")

        # Get planet data for signs and dignities
        planets = chart_data.get("planets", [])
        planet1_data: dict[str, Any] = next(
            (p for p in planets if p.get("name") == planet1_name), {}
        )
        planet2_data: dict[str, Any] = next(
            (p for p in planets if p.get("name") == planet2_name), {}
        )

        sign1 = planet1_data.get("sign", "")
        sign2 = planet2_data.get("sign", "")
        dignities1 = planet1_data.get("dignities", {})
        dignities2 = planet2_data.get("dignities", {})

        # Call RAG service
        return await self.rag_service.generate_aspect_interpretation(
            planet1=planet1_name,
            planet2=planet2_name,
            aspect=aspect_name,
            sign1=sign1,
            sign2=sign2,
            orb=orb,
            applying=applying,
            sect=sect,
            dignities1=dignities1,
            dignities2=dignities2,
        )

    async def _generate_arabic_part(self, chart_data: dict[str, Any], part_key: str) -> str:
        """
        Generate Arabic Part interpretation.

        Args:
            chart_data: Complete chart data
            part_key: Arabic Part key (e.g., 'fortune', 'spirit')

        Returns:
            Generated interpretation text
        """
        # Find Arabic Part data
        arabic_parts = chart_data.get("arabic_parts", {})
        part_data = arabic_parts.get(part_key)

        if not part_data:
            raise ValueError(f"Arabic Part {part_key} not found in chart data")

        # Extract parameters
        sign = part_data.get("sign", "")
        house = part_data.get("house", 1)
        degree = part_data.get("degree", 0.0)
        sect = chart_data.get("sect", "diurnal")

        # Call RAG service
        return await self.rag_service.generate_arabic_part_interpretation(
            part_key=part_key,
            sign=sign,
            house=house,
            degree=degree,
            sect=sect,
        )

    def get_prompt_version(self) -> str:
        """
        Get current prompt version.

        Returns:
            Prompt version string
        """
        return RAG_PROMPT_VERSION

    def get_model_id(self) -> str:
        """
        Get OpenAI model identifier.

        Returns:
            Model ID string
        """
        return RAG_MODEL_ID
