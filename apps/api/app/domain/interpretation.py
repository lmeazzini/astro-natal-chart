"""
Domain models for chart interpretations.

This module defines the core domain entities for astrological interpretations,
independent of storage mechanisms or external services.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class InterpretationResult:
    """
    Domain model for a single interpretation with metadata.

    This represents the core interpretation entity with all necessary
    metadata for tracking source, versioning, and caching status.

    Attributes:
        content: The AI-generated interpretation text
        subject: Subject identifier (e.g., 'Sun', '1', 'Sun-trine-Moon', 'fortune')
        interpretation_type: Type of interpretation ('planet', 'house', 'aspect', 'arabic_part', 'growth')
        source: Where this came from ('database', 'cache', or 'rag')
        rag_sources: Optional list of RAG source documents used
        prompt_version: Version of prompt used for generation
        is_outdated: True if prompt_version is older than current
        cached: True if retrieved from DB or cache tier (vs. fresh generation)
        generated_at: Timestamp when interpretation was created
        openai_model: OpenAI model used for generation (e.g., 'gpt-4o-mini-rag')
    """

    content: str
    subject: str
    interpretation_type: str
    source: str
    prompt_version: str
    rag_sources: list[dict[str, Any]] | None = None
    is_outdated: bool = False
    cached: bool = False
    generated_at: datetime | None = None
    openai_model: str = "gpt-4o-mini-rag"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for API serialization.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "content": self.content,
            "subject": self.subject,
            "interpretation_type": self.interpretation_type,
            "source": self.source,
            "rag_sources": self.rag_sources or [],
            "prompt_version": self.prompt_version,
            "is_outdated": self.is_outdated,
            "cached": self.cached,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "openai_model": self.openai_model,
        }


@dataclass
class InterpretationMetadata:
    """
    Metadata about interpretation generation and caching.

    Provides statistics and diagnostic information about how interpretations
    were retrieved or generated.

    Attributes:
        total_items: Total number of interpretations returned
        cache_hits_db: Number fetched from database
        cache_hits_cache: Number fetched from InterpretationCache
        rag_generations: Number freshly generated with RAG
        outdated_count: Number with old prompt_version
        documents_used: Total RAG documents retrieved
        prompt_version_current: Latest prompt version identifier
        response_time_ms: Total response time in milliseconds
    """

    total_items: int = 0
    cache_hits_db: int = 0
    cache_hits_cache: int = 0
    rag_generations: int = 0
    outdated_count: int = 0
    documents_used: int = 0
    prompt_version_current: str = ""
    response_time_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for API serialization.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "total_items": self.total_items,
            "cache_hits_db": self.cache_hits_db,
            "cache_hits_cache": self.cache_hits_cache,
            "rag_generations": self.rag_generations,
            "outdated_count": self.outdated_count,
            "documents_used": self.documents_used,
            "current_prompt_version": self.prompt_version_current,
            "response_time_ms": self.response_time_ms,
        }
