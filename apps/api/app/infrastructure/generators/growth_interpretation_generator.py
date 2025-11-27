"""
Growth interpretation generator adapter.

This module implements the IInterpretationGenerator interface using
the PersonalGrowthService for AI-powered personal development suggestions.
"""

from datetime import UTC, datetime
from typing import Any

from loguru import logger

from app.domain.interfaces.interpretation_generator import IInterpretationGenerator
from app.domain.interpretation import InterpretationResult
from app.services.personal_growth_service import GROWTH_PROMPT_VERSION, PersonalGrowthService


class GrowthInterpretationGenerator(IInterpretationGenerator):
    """
    Growth suggestions adapter implementing IInterpretationGenerator.

    This adapter wraps the PersonalGrowthService to provide
    domain-layer access to growth suggestions generation.
    """

    def __init__(self, growth_service: PersonalGrowthService):
        """
        Initialize growth generator adapter.

        Args:
            growth_service: Configured PersonalGrowthService instance
        """
        self.growth_service = growth_service

    async def generate(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str = "pt-BR",
    ) -> InterpretationResult:
        """
        Generate growth suggestions.

        Args:
            chart_data: Complete birth chart data
            interpretation_type: Should be 'growth'
            subject: Should be 'summary'
            language: Language code for generation

        Returns:
            InterpretationResult with structured growth data

        Raises:
            ValueError: If interpretation_type is not 'growth'
        """
        if interpretation_type != "growth":
            raise ValueError(
                f"GrowthInterpretationGenerator only supports 'growth' type, got: {interpretation_type}"
            )

        try:
            # Generate growth suggestions (without DB caching at this layer)
            suggestions_data = await self.growth_service.generate_growth_suggestions(
                chart_data=chart_data,
                focus_areas=None,
                chart_id=None,  # No DB caching at infrastructure layer
            )

            # Format structured data as summary text
            summary = self._format_summary(suggestions_data)

            # Wrap structured data in list for rag_sources type compatibility
            rag_sources_list = [suggestions_data] if suggestions_data else None

            return InterpretationResult(
                content=summary,
                subject="summary",
                interpretation_type="growth",
                source="rag",
                rag_sources=rag_sources_list,  # Wrap dict in list
                prompt_version=self.get_prompt_version(),
                is_outdated=False,
                cached=False,
                generated_at=datetime.now(UTC),
                openai_model=self.get_model_id(),
            )

        except Exception as e:
            logger.error(f"Error generating growth suggestions: {e}")
            raise

    def _format_summary(self, suggestions_data: dict[str, Any]) -> str:
        """
        Format growth suggestions data as human-readable summary.

        Args:
            suggestions_data: Structured growth suggestions

        Returns:
            Summary text
        """
        parts = []

        # Growth Points
        growth_points = suggestions_data.get("growth_points", [])
        if growth_points:
            parts.append(f"Growth Points: {len(growth_points)}")
            for point in growth_points[:2]:  # Show first 2
                parts.append(
                    f"- {point.get('area', 'Unknown')}: {point.get('explanation', '')[:100]}..."
                )

        # Challenges
        challenges = suggestions_data.get("challenges", [])
        if challenges:
            parts.append(f"\nChallenges: {len(challenges)}")
            for challenge in challenges[:2]:  # Show first 2
                parts.append(
                    f"- {challenge.get('name', 'Unknown')}: {challenge.get('manifestation', '')[:100]}..."
                )

        # Opportunities
        opportunities = suggestions_data.get("opportunities", [])
        if opportunities:
            parts.append(f"\nOpportunities: {len(opportunities)}")
            for opp in opportunities[:2]:  # Show first 2
                parts.append(
                    f"- {opp.get('talent', 'Unknown')}: {opp.get('description', '')[:100]}..."
                )

        # Purpose
        purpose = suggestions_data.get("purpose")
        if purpose:
            parts.append(f"\nPurpose: {purpose.get('soul_direction', '')[:150]}...")

        return "\n".join(parts)

    def get_prompt_version(self) -> str:
        """
        Get current prompt version.

        Returns:
            Prompt version string
        """
        return GROWTH_PROMPT_VERSION

    def get_model_id(self) -> str:
        """
        Get OpenAI model identifier.

        Returns:
            Model ID string
        """
        return "gpt-4o-mini"  # Growth service uses standard gpt-4o-mini
