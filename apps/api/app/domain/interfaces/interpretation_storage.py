"""
Abstract storage interface for interpretations.

This module defines the contract for interpretation storage implementations,
allowing the domain layer to remain independent of specific storage mechanisms
(database, cache, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.domain.interpretation import InterpretationResult


class IInterpretationStorage(ABC):
    """
    Abstract interface for interpretation storage.

    This interface defines the contract that all interpretation storage
    implementations must follow, whether they're backed by a database,
    cache, or other persistence mechanism.
    """

    @abstractmethod
    async def get_by_chart(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str = "pt-BR",
    ) -> list[InterpretationResult]:
        """
        Get interpretations from storage for a specific chart.

        Args:
            chart_id: Chart UUID to retrieve interpretations for
            interpretation_type: Optional filter by type ('planet', 'house', etc.)
            language: Language code for interpretations ('pt-BR' or 'en-US')

        Returns:
            List of InterpretationResult domain objects

        Raises:
            StorageError: If retrieval fails
        """
        pass

    @abstractmethod
    async def save(
        self,
        chart_id: UUID,
        interpretation: InterpretationResult,
        language: str = "pt-BR",
    ) -> None:
        """
        Save interpretation to storage.

        Args:
            chart_id: Chart UUID the interpretation belongs to
            interpretation: InterpretationResult to save
            language: Language code for interpretation

        Raises:
            StorageError: If save operation fails
        """
        pass

    @abstractmethod
    async def delete(
        self,
        chart_id: UUID,
        interpretation_type: str | None = None,
        language: str | None = None,
    ) -> int:
        """
        Delete interpretations from storage.

        Args:
            chart_id: Chart UUID to delete interpretations for
            interpretation_type: Optional filter to delete only specific type
            language: Optional filter to delete only specific language

        Returns:
            Number of interpretations deleted

        Raises:
            StorageError: If delete operation fails
        """
        pass

    @abstractmethod
    async def get_single(
        self,
        interpretation_type: str,
        parameters: dict[str, Any],
        model: str,
        version: str,
        language: str,
    ) -> InterpretationResult | None:
        """
        Get a single interpretation by parameters (cache lookup).

        This method is primarily for cache-based storage that uses
        parameter hashing for lookups.

        Args:
            interpretation_type: Type of interpretation
            parameters: Parameters dict for cache key generation
            model: OpenAI model identifier
            version: Prompt version
            language: Language code

        Returns:
            InterpretationResult if found, None otherwise

        Raises:
            StorageError: If lookup fails
        """
        pass
