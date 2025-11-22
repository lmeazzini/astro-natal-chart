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


class InterpretationBase(BaseModel):
    """Base schema for interpretation."""

    interpretation_type: str = Field(..., description="Type: 'planet', 'house', or 'aspect'")
    subject: str = Field(
        ..., description="Subject of interpretation (e.g., 'Sun', '1', 'Sun-Trine-Moon')"
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
    source: str = Field(
        default="standard",
        description="Interpretation source: 'standard' or 'rag'",
    )


class RAGInterpretationsResponse(BaseModel):
    """Response schema for RAG-enhanced interpretations (admin only)."""

    planets: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="Planet interpretations with metadata"
    )
    houses: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="House interpretations with metadata"
    )
    aspects: dict[str, InterpretationItem] = Field(
        default_factory=dict, description="Aspect interpretations with metadata"
    )
    source: str = Field(default="rag", description="Always 'rag' for this response")
    documents_used: int = Field(
        default=0, description="Total number of RAG documents used"
    )
