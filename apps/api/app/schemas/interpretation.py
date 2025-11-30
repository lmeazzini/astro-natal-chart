"""
Pydantic schemas for chart interpretations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RAGSourceInfo(BaseModel):
    """Information about a RAG source used in interpretation."""

    source: str = Field(..., description="Source name or document title")
    page: str | None = Field(None, description="Page number if available")
    relevance_score: float = Field(..., description="Relevance score from 0 to 1")
    content_preview: str = Field(..., description="Preview of source content used")


# Growth Suggestions Schemas
class GrowthPoint(BaseModel):
    """A growth point with practical actions."""

    area: str
    indicator: str
    explanation: str
    practical_actions: list[str]
    mindset_shift: str


class Challenge(BaseModel):
    """A challenge to overcome."""

    name: str
    pattern: str
    manifestation: str
    strategy: str
    practices: list[str]


class Opportunity(BaseModel):
    """An opportunity to leverage."""

    talent: str
    indicator: str
    description: str
    leverage_tips: list[str]


class Purpose(BaseModel):
    """Life purpose insights."""

    soul_direction: str
    vocation: str
    contribution: str
    integration: str
    next_steps: list[str]


class GrowthSuggestionsData(BaseModel):
    """Complete growth suggestions response."""

    growth_points: list[GrowthPoint]
    challenges: list[Challenge]
    opportunities: list[Opportunity]
    purpose: Purpose | None
    summary: str | None = None


class InterpretationMetadata(BaseModel):
    """Metadata about interpretation generation."""

    total_items: int = Field(default=0, description="Total number of interpretations")
    cache_hits_db: int = Field(default=0, description="Items from database cache")
    cache_hits_cache: int = Field(default=0, description="Items from memory cache")
    rag_generations: int = Field(default=0, description="Items freshly generated with RAG")
    outdated_count: int = Field(default=0, description="Items with outdated prompt version")
    documents_used: int = Field(default=0, description="Total RAG documents used")
    current_prompt_version: str = Field(default="", description="Current prompt version")
    response_time_ms: int = Field(default=0, description="Total response time in milliseconds")


class InterpretationBase(BaseModel):
    """Base schema for interpretation."""

    interpretation_type: str = Field(
        ..., description="Type: 'planet', 'house', 'aspect', or 'arabic_part'"
    )
    subject: str = Field(
        ...,
        description="Subject of interpretation (e.g., 'Sun', '1', 'Sun-Trine-Moon', 'fortune')",
    )
    content: str = Field(..., description="AI-generated interpretation text")
    source: str = Field(
        default="standard",
        description="Interpretation source: 'standard' (no RAG) or 'rag' (RAG-enhanced)",
    )
    rag_sources: list[RAGSourceInfo] = Field(
        default_factory=list,
        description="List of RAG sources used in interpretation (empty for standard)",
    )


class InterpretationCreate(InterpretationBase):
    """Schema for creating interpretation."""

    chart_id: UUID
    openai_model: str = Field(default="gpt-4o-mini")
    prompt_version: str = Field(default="1.0")


class InterpretationRead(InterpretationBase):
    """Schema for reading interpretation."""

    id: UUID
    chart_id: UUID
    openai_model: str
    prompt_version: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterpretationItem(BaseModel):
    """Single interpretation with metadata."""

    content: str = Field(..., description="Interpretation text")
    source: str = Field(default="standard", description="'standard' or 'rag'")
    rag_sources: list[RAGSourceInfo] = Field(default_factory=list)


class ChartInterpretationsResponse(BaseModel):
    """Response schema for all interpretations of a chart."""

    planets: dict[str, str] = Field(
        default_factory=dict, description="Planet interpretations by name"
    )
    houses: dict[str, str] = Field(
        default_factory=dict, description="House interpretations by number"
    )
    aspects: dict[str, str] = Field(
        default_factory=dict, description="Aspect interpretations by key"
    )
    arabic_parts: dict[str, str] = Field(
        default_factory=dict,
        description="Arabic Parts interpretations by key (fortune, spirit, eros, necessity)",
    )
    source: str = Field(
        default="standard",
        description="Interpretation source: 'standard' or 'rag'",
    )
    language: str = Field(
        default="pt-BR",
        description="Language code for interpretations (pt-BR or en-US)",
    )


class RAGInterpretationsResponse(BaseModel):
    """Response schema for unified RAG-enhanced interpretations."""

    planets: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="Planet interpretations with metadata"
    )
    houses: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="House interpretations with metadata"
    )
    aspects: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="Aspect interpretations with metadata"
    )
    arabic_parts: dict[str, InterpretationItem] = Field(
        default_factory=dict,
        description="Arabic Parts interpretations with metadata (fortune, spirit, eros, necessity)",
    )
    growth: dict[str, InterpretationItem] = Field(
        default_factory=dict,
        description="Growth interpretations (points, challenges, opportunities, purpose)",
    )
    metadata: InterpretationMetadata = Field(
        default_factory=InterpretationMetadata, description="Generation metadata and statistics"
    )
    language: str = Field(
        default="pt-BR",
        description="Language code for interpretations (pt-BR or en-US)",
    )
