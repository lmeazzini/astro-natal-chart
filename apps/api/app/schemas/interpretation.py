"""
Pydantic schemas for chart interpretations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InterpretationBase(BaseModel):
    """Base schema for interpretation."""

    interpretation_type: str = Field(..., description="Type: 'planet', 'house', or 'aspect'")
    subject: str = Field(
        ..., description="Subject of interpretation (e.g., 'Sun', '1', 'Sun-Trine-Moon')"
    )
    content: str = Field(..., description="AI-generated interpretation text")


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
