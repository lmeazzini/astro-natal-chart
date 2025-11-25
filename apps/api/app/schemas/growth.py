"""
Pydantic schemas for personal growth suggestions.
"""

from pydantic import BaseModel, Field


class GrowthPoint(BaseModel):
    """A single growth point with actionable suggestions."""

    area: str = Field(..., description="Area that needs development")
    indicator: str = Field(..., description="Astrological indicator")
    explanation: str = Field(..., description="Explanation of the pattern")
    practical_actions: list[str] = Field(
        ..., description="Specific actionable steps"
    )
    mindset_shift: str = Field(..., description="Reframe or affirmation")


class Challenge(BaseModel):
    """A challenge with strategies to overcome it."""

    name: str = Field(..., description="Challenge title")
    pattern: str = Field(..., description="Astrological pattern")
    manifestation: str = Field(..., description="How it manifests in daily life")
    strategy: str = Field(..., description="Main strategy to overcome")
    practices: list[str] = Field(..., description="Specific practices")


class Opportunity(BaseModel):
    """A natural talent or opportunity to leverage."""

    talent: str = Field(..., description="Natural talent or gift")
    indicator: str = Field(..., description="Astrological indicator")
    description: str = Field(..., description="How the talent manifests")
    leverage_tips: list[str] = Field(..., description="Ways to leverage the talent")


class Purpose(BaseModel):
    """Life purpose and direction insights."""

    soul_direction: str = Field(..., description="Direction of soul evolution")
    vocation: str = Field(..., description="Career and vocation guidance")
    contribution: str = Field(..., description="Contribution to the world")
    integration: str = Field(..., description="How to integrate all parts")
    next_steps: list[str] = Field(..., description="Concrete next steps")


class PatternsAnalyzed(BaseModel):
    """Metadata about patterns analyzed in the chart."""

    difficult_aspects: int = Field(default=0)
    harmonious_aspects: int = Field(default=0)
    retrogrades: int = Field(default=0)
    stelliums: int = Field(default=0)


class GrowthMetadata(BaseModel):
    """Metadata for the growth suggestions response."""

    language: str = Field(..., description="Language of the suggestions")
    model: str = Field(..., description="AI model used")
    patterns_analyzed: PatternsAnalyzed = Field(
        default_factory=PatternsAnalyzed,
        description="Patterns analyzed in the chart",
    )


class GrowthSuggestionsResponse(BaseModel):
    """Complete response with all growth suggestions."""

    growth_points: list[GrowthPoint] = Field(
        default_factory=list,
        description="Areas for personal growth",
    )
    challenges: list[Challenge] = Field(
        default_factory=list,
        description="Challenges to overcome",
    )
    opportunities: list[Opportunity] = Field(
        default_factory=list,
        description="Natural talents and opportunities",
    )
    purpose: Purpose | None = Field(
        default=None,
        description="Life purpose insights",
    )
    metadata: GrowthMetadata | None = Field(
        default=None,
        description="Response metadata",
    )


class GrowthSuggestionsRequest(BaseModel):
    """Request body for generating growth suggestions."""

    focus_areas: list[str] | None = Field(
        default=None,
        description="Optional focus areas (e.g., ['career', 'relationships'])",
    )
