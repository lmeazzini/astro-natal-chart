"""
Abstract generator interface for interpretations.

This module defines the contract for interpretation generation implementations,
allowing the domain layer to remain independent of specific AI services or
generation strategies.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.domain.interpretation import InterpretationResult


class IInterpretationGenerator(ABC):
    """
    Abstract interface for interpretation generation.

    This interface defines the contract that all interpretation generators
    must follow, whether they use RAG, traditional prompts, or other methods.
    """

    @abstractmethod
    async def generate(
        self,
        chart_data: dict[str, Any],
        interpretation_type: str,
        subject: str,
        language: str = "pt-BR",
    ) -> InterpretationResult:
        """
        Generate interpretation for a chart element.

        Args:
            chart_data: Complete birth chart data from BirthChart.chart_data
            interpretation_type: Type to generate ('planet', 'house', 'aspect', etc.)
            subject: Subject identifier (e.g., 'Sun', '1', 'Sun-trine-Moon')
            language: Language code for generation ('pt-BR' or 'en-US')

        Returns:
            InterpretationResult with generated content and metadata

        Raises:
            GenerationError: If generation fails
        """
        pass

    @abstractmethod
    def get_prompt_version(self) -> str:
        """
        Get the current prompt version used by this generator.

        Returns:
            Prompt version string (e.g., 'rag-v1', '1.0.0')
        """
        pass

    @abstractmethod
    def get_model_id(self) -> str:
        """
        Get the OpenAI model identifier used by this generator.

        Returns:
            Model ID string (e.g., 'gpt-4o-mini-rag', 'gpt-4o-mini')
        """
        pass
