"""
Interpretation Cache model for storing AI-generated interpretation responses.

This cache stores interpretation results based on a unique hash key derived from:
- interpretation type (planet, house, aspect)
- subject parameters (planet name, sign, house, etc.)
- model and prompt version

This helps reduce OpenAI API costs by reusing interpretations for identical inputs.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InterpretationCache(Base):
    """Cache for AI-generated astrological interpretations."""

    __tablename__ = "interpretation_cache"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )

    # Unique hash key for cache lookup
    # Generated from: type + subject params + model + prompt_version
    cache_key: Mapped[str] = mapped_column(
        String(64),  # SHA-256 hash
        unique=True,
        nullable=False,
        index=True,
    )

    # Interpretation type: 'planet', 'house', 'aspect'
    interpretation_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        comment="Type: 'planet', 'house', or 'aspect'",
    )

    # Subject identifier (e.g., "Sun", "1", "Sun-Trine-Moon")
    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g., 'Sun', '1', 'Sun-Trine-Moon'",
    )

    # The cached interpretation content
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="AI-generated interpretation text",
    )

    # Parameters used to generate (for debugging/audit)
    # JSON with all params: sign, house, dignities, sect, retrograde, etc.
    parameters_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="JSON of parameters used to generate this interpretation",
    )

    # Model and version tracking
    openai_model: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="OpenAI model used (e.g., 'gpt-4o-mini')",
    )
    prompt_version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Prompt version for tracking changes",
    )

    # Usage tracking
    hit_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Number of times this cache entry was used",
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Last time this cache entry was accessed",
    )

    def __repr__(self) -> str:
        return f"<InterpretationCache {self.interpretation_type}:{self.subject} (hits: {self.hit_count})>"
