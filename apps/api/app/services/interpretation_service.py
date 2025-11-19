"""
Service for generating AI-powered astrological interpretations using OpenAI.
"""

from pathlib import Path
from typing import Any, Callable
from uuid import UUID

import yaml
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.interpretation import ChartInterpretation
from app.repositories.interpretation_repository import InterpretationRepository

# Classical 7 planets only (no modern planets)
CLASSICAL_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


class InterpretationService:
    """Service for generating and managing astrological interpretations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize interpretation service.

        Args:
            db: Database session
        """
        self.db = db
        self.repository = InterpretationRepository(db)
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> dict[str, Any]:
        """
        Load interpretation prompts from YAML file.

        Returns:
            Dictionary containing prompt templates
        """
        prompts_path = Path(__file__).parent.parent / "astro" / "interpretation_prompts.yaml"
        with open(prompts_path, encoding="utf-8") as f:
            result = yaml.safe_load(f)
            return result if isinstance(result, dict) else {}

    async def generate_planet_interpretation(
        self,
        planet: str,
        sign: str,
        house: int,
        dignities: dict[str, Any],
        sect: str,
        retrograde: bool,
    ) -> str:
        """
        Generate interpretation for a planet position.

        Args:
            planet: Planet name (e.g., "Sun", "Moon")
            sign: Zodiac sign
            house: House number (1-12)
            dignities: Dictionary of essential dignities
            sect: Chart sect ("diurnal" or "nocturnal")
            retrograde: Whether planet is retrograde

        Returns:
            Generated interpretation text
        """
        # Skip modern planets
        if planet not in CLASSICAL_PLANETS:
            return ""

        # Build context from dignities
        dignity_context = self._format_dignities(dignities)

        # Format the prompt
        prompt = self.prompts["planet_prompts"]["base"].format(
            planet=planet,
            sign=sign,
            house=house,
            dignities=dignity_context,
            sect=sect,
            retrograde="Sim" if retrograde else "Não",
        )

        # Generate interpretation using OpenAI
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            interpretation = response.choices[0].message.content
            return interpretation.strip() if interpretation else ""

        except Exception as e:
            logger.error(f"Error generating interpretation for {planet}: {e}")
            return f"Erro ao gerar interpretação para {planet}."

    async def generate_house_interpretation(
        self,
        house: int,
        sign: str,
        ruler: str,
        ruler_dignities: dict[str, Any],
        sect: str,
    ) -> str:
        """
        Generate interpretation for a house.

        Args:
            house: House number (1-12)
            sign: Sign on the cusp
            ruler: Planet ruling the sign
            ruler_dignities: Dignities of the ruler
            sect: Chart sect

        Returns:
            Generated interpretation text
        """
        ruler_context = self._format_dignities(ruler_dignities)

        prompt = self.prompts["house_prompts"]["base"].format(
            house=house,
            sign=sign,
            ruler=ruler,
            ruler_dignities=ruler_context,
            sect=sect,
        )

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            interpretation = response.choices[0].message.content
            return interpretation.strip() if interpretation else ""

        except Exception as e:
            logger.error(f"Error generating interpretation for house {house}: {e}")
            return f"Erro ao gerar interpretação para casa {house}."

    async def generate_aspect_interpretation(
        self,
        planet1: str,
        planet2: str,
        aspect: str,
        sign1: str,
        sign2: str,
        orb: float,
        applying: bool,
        sect: str,
        dignities1: dict[str, Any],
        dignities2: dict[str, Any],
    ) -> str:
        """
        Generate interpretation for an aspect between two planets.

        Args:
            planet1: First planet name
            planet2: Second planet name
            aspect: Aspect type (e.g., "Trine", "Square")
            sign1: Sign of first planet
            sign2: Sign of second planet
            orb: Orb in degrees
            applying: Whether aspect is applying
            sect: Chart sect
            dignities1: Dignities of first planet
            dignities2: Dignities of second planet

        Returns:
            Generated interpretation text
        """
        # Skip if either planet is not classical
        if planet1 not in CLASSICAL_PLANETS or planet2 not in CLASSICAL_PLANETS:
            return ""

        dignities1_context = self._format_dignities(dignities1)
        dignities2_context = self._format_dignities(dignities2)

        prompt = self.prompts["aspect_prompts"]["base"].format(
            aspect=aspect,
            planet1=planet1,
            planet2=planet2,
            sign1=sign1,
            sign2=sign2,
            orb=round(orb, 1),
            applying="Sim" if applying else "Não",
            sect=sect,
            dignities1=dignities1_context,
            dignities2=dignities2_context,
        )

        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts["system_prompt"]},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS,
                temperature=settings.OPENAI_TEMPERATURE,
            )

            interpretation = response.choices[0].message.content
            return interpretation.strip() if interpretation else ""

        except Exception as e:
            logger.error(
                f"Error generating aspect interpretation {planet1}-{aspect}-{planet2}: {e}"
            )
            return f"Erro ao gerar interpretação para aspecto {planet1}-{aspect}-{planet2}."

    async def generate_all_interpretations(
        self,
        chart_id: UUID,
        chart_data: dict[str, Any],
        progress_callback: Callable[[int], Any] | None = None,
    ) -> list[ChartInterpretation]:
        """
        Generate all interpretations for a birth chart.

        Args:
            chart_id: UUID of the birth chart
            chart_data: Complete chart data dictionary
            progress_callback: Optional async callback for progress updates (40-90%)

        Returns:
            List of created interpretation instances
        """
        interpretations: list[ChartInterpretation] = []
        sect = chart_data.get("sect", "diurnal")

        # Count total items for progress calculation
        planet_count = len([p for p in chart_data.get("planets", []) if p["name"] in CLASSICAL_PLANETS])
        house_count = len(chart_data.get("houses", []))
        aspect_count = len([a for a in chart_data.get("aspects", [])
                           if a["planet1"] in CLASSICAL_PLANETS and a["planet2"] in CLASSICAL_PLANETS])
        total_count = planet_count + house_count + aspect_count
        current_item = 0

        # Generate planet interpretations (classical 7 only) - Progress 50-65%
        for planet_data in chart_data.get("planets", []):
            planet_name = planet_data["name"]
            if planet_name not in CLASSICAL_PLANETS:
                continue

            interpretation_text = await self.generate_planet_interpretation(
                planet=planet_name,
                sign=planet_data["sign"],
                house=planet_data["house"],
                dignities=planet_data.get("dignities", {}),
                sect=sect,
                retrograde=planet_data.get("retrograde", False),
            )

            if interpretation_text:
                interp = ChartInterpretation(
                    chart_id=chart_id,
                    interpretation_type="planet",
                    subject=planet_name,
                    content=interpretation_text,
                    openai_model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                )
                interpretations.append(interp)
                await self.repository.create(interp)

            # Update progress (50-65%)
            current_item += 1
            if progress_callback and total_count > 0:
                progress = 50 + int((current_item / total_count) * 40)
                await progress_callback(min(progress, 90))

        # Generate house interpretations - Progress 65-80%
        for house_data in chart_data.get("houses", []):
            house_num = house_data["house"]
            sign = house_data["sign"]

            # Get ruler from dignities module
            from app.astro.dignities import get_sign_ruler

            ruler = get_sign_ruler(sign)
            if not ruler:
                current_item += 1
                continue

            # Find ruler's dignities from planet data
            ruler_dignities = {}
            for planet_data in chart_data.get("planets", []):
                if planet_data["name"] == ruler:
                    ruler_dignities = planet_data.get("dignities", {})
                    break

            interpretation_text = await self.generate_house_interpretation(
                house=house_num,
                sign=sign,
                ruler=ruler,
                ruler_dignities=ruler_dignities,
                sect=sect,
            )

            if interpretation_text:
                interp = ChartInterpretation(
                    chart_id=chart_id,
                    interpretation_type="house",
                    subject=str(house_num),
                    content=interpretation_text,
                    openai_model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                )
                interpretations.append(interp)
                await self.repository.create(interp)

            # Update progress
            current_item += 1
            if progress_callback and total_count > 0:
                progress = 50 + int((current_item / total_count) * 40)
                await progress_callback(min(progress, 90))

        # Generate aspect interpretations (classical planets only) - Progress 80-90%
        for aspect_data in chart_data.get("aspects", []):
            planet1 = aspect_data["planet1"]
            planet2 = aspect_data["planet2"]

            if planet1 not in CLASSICAL_PLANETS or planet2 not in CLASSICAL_PLANETS:
                continue

            # Find planet data for dignities
            dignities1 = {}
            dignities2 = {}
            sign1 = ""
            sign2 = ""

            for planet_data in chart_data.get("planets", []):
                if planet_data["name"] == planet1:
                    dignities1 = planet_data.get("dignities", {})
                    sign1 = planet_data["sign"]
                elif planet_data["name"] == planet2:
                    dignities2 = planet_data.get("dignities", {})
                    sign2 = planet_data["sign"]

            interpretation_text = await self.generate_aspect_interpretation(
                planet1=planet1,
                planet2=planet2,
                aspect=aspect_data["aspect"],
                sign1=sign1,
                sign2=sign2,
                orb=aspect_data["orb"],
                applying=aspect_data["applying"],
                sect=sect,
                dignities1=dignities1,
                dignities2=dignities2,
            )

            if interpretation_text:
                subject = f"{planet1}-{aspect_data['aspect']}-{planet2}"
                interp = ChartInterpretation(
                    chart_id=chart_id,
                    interpretation_type="aspect",
                    subject=subject,
                    content=interpretation_text,
                    openai_model=settings.OPENAI_MODEL,
                    prompt_version=self.prompts.get("version", "1.0"),
                )
                interpretations.append(interp)
                await self.repository.create(interp)

            # Update progress
            current_item += 1
            if progress_callback and total_count > 0:
                progress = 50 + int((current_item / total_count) * 40)
                await progress_callback(min(progress, 90))

        logger.info(f"Generated {len(interpretations)} interpretations for chart {chart_id}")
        return interpretations

    async def get_interpretations_by_chart(self, chart_id: UUID) -> dict[str, dict[str, str]]:
        """
        Get all interpretations for a chart, grouped by type.

        Args:
            chart_id: Chart UUID

        Returns:
            Dictionary with planets, houses, and aspects interpretations
        """
        all_interps = await self.repository.get_by_chart_id(chart_id)

        result: dict[str, dict[str, str]] = {
            "planets": {},
            "houses": {},
            "aspects": {},
        }

        for interp in all_interps:
            if interp.interpretation_type == "planet":
                result["planets"][interp.subject] = interp.content
            elif interp.interpretation_type == "house":
                result["houses"][interp.subject] = interp.content
            elif interp.interpretation_type == "aspect":
                result["aspects"][interp.subject] = interp.content

        return result

    def _format_dignities(self, dignities: dict[str, Any]) -> str:
        """
        Format dignities dictionary into readable text.

        Args:
            dignities: Dignities dictionary

        Returns:
            Formatted dignity text
        """
        if not dignities:
            return "Sem dignidades essenciais"

        parts = []
        score = dignities.get("score", 0)
        classification = dignities.get("classification", "peregrine")

        if dignities.get("is_ruler"):
            parts.append("domicílio")
        if dignities.get("is_exalted"):
            parts.append("exaltação")
        if dignities.get("is_detriment"):
            parts.append("detrimento")
        if dignities.get("is_fall"):
            parts.append("queda")
        if dignities.get("triplicity_ruler"):
            parts.append(f"triplicidade ({dignities['triplicity_ruler']})")

        if parts:
            dignity_list = ", ".join(parts)
            return f"{dignity_list} (score: {score}, {classification})"
        else:
            return f"Peregrino (score: {score})"
