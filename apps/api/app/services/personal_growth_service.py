"""
Personal Growth Service - AI-powered development suggestions based on natal charts.

This service analyzes natal chart data to generate personalized growth suggestions,
challenges to overcome, opportunities to leverage, and life purpose insights.
Uses OpenAI GPT-4o-mini with structured outputs for consistent response formats.

Supports caching via InterpretationCacheService to reduce API costs.
"""

import asyncio
import json
from typing import Any

from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.interpretation_cache_service import InterpretationCacheService

# Prompt version for cache invalidation (bump when prompts change)
GROWTH_PROMPT_VERSION = "1.0.0"


class PersonalGrowthService:
    """Service for generating personal development suggestions from natal charts."""

    def __init__(
        self,
        language: str = "pt-BR",
        db: AsyncSession | None = None,
    ):
        """
        Initialize the PersonalGrowthService.

        Args:
            language: Language for suggestions ('pt-BR' or 'en-US')
            db: Optional database session for caching
        """
        self.language = language
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.db = db
        self.cache_service = InterpretationCacheService(db) if db else None

    def _get_language_instruction(self) -> str:
        """Get language instruction for the AI model."""
        if self.language.startswith("en"):
            return (
                "You MUST respond entirely in English (en-US). "
                "Use natural, fluent English for all content."
            )
        return (
            "Você DEVE responder inteiramente em Português (pt-BR). "
            "Use português natural e fluente para todo o conteúdo."
        )

    def analyze_chart_patterns(self, chart_data: dict[str, Any]) -> dict[str, Any]:
        """
        Identify significant astrological patterns in the chart.

        Args:
            chart_data: Complete birth chart data

        Returns:
            Dictionary with categorized patterns for AI context
        """
        patterns: dict[str, Any] = {
            "difficult_aspects": [],
            "harmonious_aspects": [],
            "retrogrades": [],
            "strong_dignities": [],
            "weak_dignities": [],
            "stelliums": [],
            "sect": chart_data.get("sect", "diurnal"),
            "big_three": {},
        }

        planets = chart_data.get("planets", [])
        aspects = chart_data.get("aspects", [])

        # Extract Big Three (Sun, Moon, Ascendant)
        for planet in planets:
            name = planet.get("name", "")
            if name == "Sun":
                patterns["big_three"]["sun"] = {
                    "sign": planet.get("sign"),
                    "house": planet.get("house"),
                }
            elif name == "Moon":
                patterns["big_three"]["moon"] = {
                    "sign": planet.get("sign"),
                    "house": planet.get("house"),
                }

        # Ascendant from chart_info
        if "ascendant" in chart_data:
            asc_lon = chart_data["ascendant"]
            signs = [
                "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
            ]
            asc_sign = signs[int(asc_lon / 30) % 12]
            patterns["big_three"]["ascendant"] = {"sign": asc_sign}

        # Categorize aspects
        for aspect in aspects:
            aspect_type = aspect.get("aspect", "")
            aspect_info = {
                "planets": f"{aspect.get('planet1')} {aspect_type} {aspect.get('planet2')}",
                "orb": aspect.get("orb", 0),
                "applying": aspect.get("applying", False),
            }

            if aspect_type in ["square", "opposition"]:
                patterns["difficult_aspects"].append(aspect_info)
            elif aspect_type in ["trine", "sextile", "conjunction"]:
                patterns["harmonious_aspects"].append(aspect_info)

        # Retrograde planets
        for planet in planets:
            if planet.get("retrograde"):
                patterns["retrogrades"].append({
                    "planet": planet.get("name"),
                    "sign": planet.get("sign"),
                    "house": planet.get("house"),
                })

        # Analyze dignities
        for planet in planets:
            dignities = planet.get("dignities", {})
            planet_info = {
                "planet": planet.get("name"),
                "sign": planet.get("sign"),
                "house": planet.get("house"),
            }

            # Strong dignities
            if dignities.get("ruler") or dignities.get("exalted"):
                planet_info["dignity"] = "domicile" if dignities.get("ruler") else "exaltation"
                patterns["strong_dignities"].append(planet_info)

            # Weak dignities
            if dignities.get("detriment") or dignities.get("fall"):
                planet_info["dignity"] = "detriment" if dignities.get("detriment") else "fall"
                patterns["weak_dignities"].append(planet_info)

        # Detect stelliums (3+ planets in same sign)
        sign_counts: dict[str, list[str]] = {}
        for planet in planets:
            sign = planet.get("sign", "")
            if sign:
                if sign not in sign_counts:
                    sign_counts[sign] = []
                sign_counts[sign].append(planet.get("name", ""))

        for sign, planet_list in sign_counts.items():
            if len(planet_list) >= 3:
                patterns["stelliums"].append({
                    "sign": sign,
                    "planets": planet_list,
                })

        return patterns

    def _build_chart_summary(
        self, chart_data: dict[str, Any], patterns: dict[str, Any]
    ) -> str:
        """Build a text summary of the chart for the AI prompt."""
        planets = chart_data.get("planets", [])
        big_three = patterns.get("big_three", {})

        summary_parts = []

        # Big Three
        if big_three:
            sun = big_three.get("sun", {})
            moon = big_three.get("moon", {})
            asc = big_three.get("ascendant", {})
            summary_parts.append(
                f"Big Three: Sun in {sun.get('sign', 'Unknown')} (House {sun.get('house', '?')}), "
                f"Moon in {moon.get('sign', 'Unknown')} (House {moon.get('house', '?')}), "
                f"Ascendant in {asc.get('sign', 'Unknown')}"
            )

        # Sect
        summary_parts.append(f"Chart Sect: {patterns.get('sect', 'diurnal')}")

        # Key planets summary
        key_planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for planet in planets:
            if planet.get("name") in key_planets:
                retro = " (R)" if planet.get("retrograde") else ""
                summary_parts.append(
                    f"{planet['name']}: {planet.get('sign')}{retro} in House {planet.get('house')}"
                )

        # Difficult aspects
        if patterns.get("difficult_aspects"):
            diff_aspects = [a["planets"] for a in patterns["difficult_aspects"][:5]]
            summary_parts.append(f"Challenging Aspects: {', '.join(diff_aspects)}")

        # Harmonious aspects
        if patterns.get("harmonious_aspects"):
            harm_aspects = [a["planets"] for a in patterns["harmonious_aspects"][:5]]
            summary_parts.append(f"Supportive Aspects: {', '.join(harm_aspects)}")

        # Retrogrades
        if patterns.get("retrogrades"):
            retros = [f"{r['planet']} in {r['sign']}" for r in patterns["retrogrades"]]
            summary_parts.append(f"Retrograde Planets: {', '.join(retros)}")

        # Strong dignities
        if patterns.get("strong_dignities"):
            strong = [f"{d['planet']} ({d['dignity']})" for d in patterns["strong_dignities"]]
            summary_parts.append(f"Strong Placements: {', '.join(strong)}")

        # Weak dignities
        if patterns.get("weak_dignities"):
            weak = [f"{d['planet']} ({d['dignity']})" for d in patterns["weak_dignities"]]
            summary_parts.append(f"Challenging Placements: {', '.join(weak)}")

        # Stelliums
        if patterns.get("stelliums"):
            stelliums = [f"{s['sign']} ({', '.join(s['planets'])})" for s in patterns["stelliums"]]
            summary_parts.append(f"Stelliums: {', '.join(stelliums)}")

        return "\n".join(summary_parts)

    def _get_focus_areas_instruction(self, focus_areas: list[str] | None) -> str:
        """Get focus areas instruction for prompts."""
        if not focus_areas:
            return ""

        areas_str = ", ".join(focus_areas)
        if self.language.startswith("en"):
            return (
                f"\n\nFOCUS AREAS: The user wants to focus on: {areas_str}. "
                "Prioritize insights related to these areas while still providing "
                "a balanced analysis."
            )
        return (
            f"\n\nÁREAS DE FOCO: O usuário quer focar em: {areas_str}. "
            "Priorize insights relacionados a essas áreas, mantendo uma "
            "análise equilibrada."
        )

    async def generate_growth_suggestions(
        self,
        chart_data: dict[str, Any],
        focus_areas: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate personalized growth suggestions based on natal chart.

        Args:
            chart_data: Complete birth chart data
            focus_areas: Optional focus areas (e.g., ['career', 'relationships'])

        Returns:
            Dictionary with growth_points, challenges, opportunities, and purpose
        """
        patterns = self.analyze_chart_patterns(chart_data)
        chart_summary = self._build_chart_summary(chart_data, patterns)
        focus_instruction = self._get_focus_areas_instruction(focus_areas)

        suggestions: dict[str, Any] = {}

        try:
            # Generate all sections in parallel using asyncio.gather
            results = await asyncio.gather(
                self._generate_growth_points(chart_summary, patterns, focus_instruction),
                self._generate_challenges(chart_summary, patterns, focus_instruction),
                self._generate_opportunities(chart_summary, patterns, focus_instruction),
                self._generate_purpose(chart_summary, patterns, focus_instruction),
            )

            suggestions["growth_points"] = results[0]
            suggestions["challenges"] = results[1]
            suggestions["opportunities"] = results[2]
            suggestions["purpose"] = results[3]

            # Add metadata
            suggestions["metadata"] = {
                "language": self.language,
                "model": self.model,
                "patterns_analyzed": {
                    "difficult_aspects": len(patterns.get("difficult_aspects", [])),
                    "harmonious_aspects": len(patterns.get("harmonious_aspects", [])),
                    "retrogrades": len(patterns.get("retrogrades", [])),
                    "stelliums": len(patterns.get("stelliums", [])),
                },
                "focus_areas": focus_areas,
                "cached": False,  # Will be updated if any item was cached
            }

        except Exception as e:
            logger.error("Error generating growth suggestions: {}", str(e))
            raise

        return suggestions

    async def _generate_growth_points(
        self,
        chart_summary: str,
        patterns: dict[str, Any],
        focus_instruction: str = "",
    ) -> list[dict[str, Any]]:
        """Generate growth point suggestions with caching support."""
        # Build cache parameters
        cache_params = {
            "chart_summary": chart_summary,
            "retrogrades": patterns.get("retrogrades", []),
            "weak_dignities": patterns.get("weak_dignities", []),
            "difficult_aspects": patterns.get("difficult_aspects", [])[:5],
            "focus_instruction": focus_instruction,
        }

        # Try to get from cache
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="growth_points",
                parameters=cache_params,
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )
            if cached:
                cached_result: list[dict[str, Any]] = json.loads(cached)
                return cached_result

        prompt = f"""You are an expert astrologer and personal development coach.
{self._get_language_instruction()}

Analyze this natal chart and provide 3-5 SPECIFIC, ACTIONABLE growth points.

Chart Summary:
{chart_summary}

Retrograde Planets: {json.dumps(patterns.get('retrogrades', []), indent=2)}
Challenging Placements: {json.dumps(patterns.get('weak_dignities', []), indent=2)}
Difficult Aspects: {json.dumps(patterns.get('difficult_aspects', [])[:5], indent=2)}
{focus_instruction}

For each growth point, provide:
1. area: What needs development (e.g., "Communication", "Self-worth")
2. indicator: The astrological indicator (e.g., "Mercury retrograde in Pisces")
3. explanation: Brief explanation of the astrological pattern (2-3 sentences)
4. practical_actions: 3-4 specific, actionable steps
5. mindset_shift: One reframe or affirmation

Return a JSON object with this structure:
{{
  "growth_points": [
    {{
      "area": "string",
      "indicator": "string",
      "explanation": "string",
      "practical_actions": ["string", "string", "string"],
      "mindset_shift": "string"
    }}
  ]
}}

IMPORTANT:
- Be specific to THIS chart, not generic
- Focus on ACTIONS, not just descriptions
- Use empowering, non-fatalistic language
- Base suggestions on actual chart data provided"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert astrologer specializing in practical personal development. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        result = json.loads(content)
        growth_points: list[dict[str, Any]] = result.get("growth_points", [])

        # Cache the result
        if self.cache_service and growth_points:
            await self.cache_service.set(
                interpretation_type="growth_points",
                subject="growth_analysis",
                parameters=cache_params,
                content=json.dumps(growth_points, ensure_ascii=False),
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )

        return growth_points

    async def _generate_challenges(
        self,
        chart_summary: str,
        patterns: dict[str, Any],
        focus_instruction: str = "",
    ) -> list[dict[str, Any]]:
        """Generate challenge insights with solutions and caching support."""
        # Build cache parameters
        cache_params = {
            "chart_summary": chart_summary,
            "difficult_aspects": patterns.get("difficult_aspects", [])[:5],
            "weak_dignities": patterns.get("weak_dignities", []),
            "focus_instruction": focus_instruction,
        }

        # Try to get from cache
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="growth_challenges",
                parameters=cache_params,
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )
            if cached:
                cached_result: list[dict[str, Any]] = json.loads(cached)
                return cached_result

        prompt = f"""You are an expert astrologer and personal development coach.
{self._get_language_instruction()}

Analyze this natal chart and identify 3-4 key challenges with solutions.

Chart Summary:
{chart_summary}

Difficult Aspects: {json.dumps(patterns.get('difficult_aspects', [])[:5], indent=2)}
Challenging Placements: {json.dumps(patterns.get('weak_dignities', []), indent=2)}
{focus_instruction}

For each challenge, provide:
1. name: Challenge title (e.g., "Self-Criticism Pattern")
2. pattern: The astrological pattern causing it
3. manifestation: How this might manifest in daily life
4. strategy: Main strategy to overcome
5. practices: 2-3 specific practices or exercises

Return a JSON object:
{{
  "challenges": [
    {{
      "name": "string",
      "pattern": "string",
      "manifestation": "string",
      "strategy": "string",
      "practices": ["string", "string"]
    }}
  ]
}}

IMPORTANT:
- Be specific to THIS chart
- Use empowering language - challenges are growth opportunities
- Focus on practical solutions"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert astrologer specializing in practical personal development. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        result = json.loads(content)
        challenges: list[dict[str, Any]] = result.get("challenges", [])

        # Cache the result
        if self.cache_service and challenges:
            await self.cache_service.set(
                interpretation_type="growth_challenges",
                subject="challenges_analysis",
                parameters=cache_params,
                content=json.dumps(challenges, ensure_ascii=False),
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )

        return challenges

    async def _generate_opportunities(
        self,
        chart_summary: str,
        patterns: dict[str, Any],
        focus_instruction: str = "",
    ) -> list[dict[str, Any]]:
        """Generate opportunity and talent insights with caching support."""
        # Build cache parameters
        cache_params = {
            "chart_summary": chart_summary,
            "harmonious_aspects": patterns.get("harmonious_aspects", [])[:5],
            "strong_dignities": patterns.get("strong_dignities", []),
            "stelliums": patterns.get("stelliums", []),
            "focus_instruction": focus_instruction,
        }

        # Try to get from cache
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="growth_opportunities",
                parameters=cache_params,
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )
            if cached:
                cached_result: list[dict[str, Any]] = json.loads(cached)
                return cached_result

        prompt = f"""You are an expert astrologer and personal development coach.
{self._get_language_instruction()}

Analyze this natal chart and identify 3-4 natural talents and opportunities.

Chart Summary:
{chart_summary}

Harmonious Aspects: {json.dumps(patterns.get('harmonious_aspects', [])[:5], indent=2)}
Strong Placements: {json.dumps(patterns.get('strong_dignities', []), indent=2)}
Stelliums: {json.dumps(patterns.get('stelliums', []), indent=2)}
{focus_instruction}

For each opportunity/talent, provide:
1. talent: The natural talent or gift
2. indicator: The astrological indicator
3. description: How this talent manifests
4. leverage_tips: 3-4 ways to leverage this talent

Return a JSON object:
{{
  "opportunities": [
    {{
      "talent": "string",
      "indicator": "string",
      "description": "string",
      "leverage_tips": ["string", "string", "string"]
    }}
  ]
}}

IMPORTANT:
- Be specific to THIS chart
- Focus on actionable ways to use these gifts
- Highlight unique combinations in the chart"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert astrologer specializing in practical personal development. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if not content:
            return []

        result = json.loads(content)
        opportunities: list[dict[str, Any]] = result.get("opportunities", [])

        # Cache the result
        if self.cache_service and opportunities:
            await self.cache_service.set(
                interpretation_type="growth_opportunities",
                subject="opportunities_analysis",
                parameters=cache_params,
                content=json.dumps(opportunities, ensure_ascii=False),
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )

        return opportunities

    async def _generate_purpose(
        self,
        chart_summary: str,
        patterns: dict[str, Any],
        focus_instruction: str = "",
    ) -> dict[str, Any]:
        """Generate life purpose insights with caching support."""
        big_three = patterns.get("big_three", {})

        # Build cache parameters
        cache_params = {
            "chart_summary": chart_summary,
            "big_three": big_three,
            "focus_instruction": focus_instruction,
        }

        # Try to get from cache
        if self.cache_service:
            cached = await self.cache_service.get(
                interpretation_type="growth_purpose",
                parameters=cache_params,
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )
            if cached:
                cached_result: dict[str, Any] = json.loads(cached)
                return cached_result

        prompt = f"""You are an expert astrologer and personal development coach.
{self._get_language_instruction()}

Analyze this natal chart and provide insights about life purpose and direction.

Chart Summary:
{chart_summary}

Big Three:
- Sun: {big_three.get('sun', {}).get('sign', 'Unknown')} in House {big_three.get('sun', {}).get('house', '?')}
- Moon: {big_three.get('moon', {}).get('sign', 'Unknown')} in House {big_three.get('moon', {}).get('house', '?')}
- Ascendant: {big_three.get('ascendant', {}).get('sign', 'Unknown')}
{focus_instruction}

Provide insights about:
1. soul_direction: The overall direction of soul evolution (2-3 sentences)
2. vocation: Career and vocation guidance (2-3 sentences)
3. contribution: How this person can contribute to the world (2-3 sentences)
4. integration: How to integrate all parts of themselves (2-3 sentences)
5. next_steps: 3-4 concrete next steps for growth

Return a JSON object:
{{
  "purpose": {{
    "soul_direction": "string",
    "vocation": "string",
    "contribution": "string",
    "integration": "string",
    "next_steps": ["string", "string", "string"]
  }}
}}

IMPORTANT:
- Be specific to THIS chart
- Use empowering, non-fatalistic language
- Focus on agency and choice"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert astrologer specializing in practical personal development. Always respond with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        if not content:
            return {}

        result = json.loads(content)
        purpose: dict[str, Any] = result.get("purpose", {})

        # Cache the result
        if self.cache_service and purpose:
            await self.cache_service.set(
                interpretation_type="growth_purpose",
                subject="purpose_analysis",
                parameters=cache_params,
                content=json.dumps(purpose, ensure_ascii=False),
                model=self.model,
                prompt_version=GROWTH_PROMPT_VERSION,
                language=self.language,
            )

        return purpose
