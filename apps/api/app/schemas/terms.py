"""
Pydantic schemas for planetary terms (bounds) API responses.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TermSystemEnum(str, Enum):
    """Available term systems."""

    EGYPTIAN = "egyptian"
    PTOLEMAIC = "ptolemaic"
    CHALDEAN = "chaldean"
    DOROTHEAN = "dorothean"


class TermEntry(BaseModel):
    """A single term entry in a sign."""

    ruler: str = Field(..., description="Planet ruling this term")
    start: int = Field(..., ge=0, lt=30, description="Start degree (inclusive)")
    end: int = Field(..., gt=0, le=30, description="End degree (exclusive)")


class TermRulerResponse(BaseModel):
    """Response for looking up term ruler at a specific degree."""

    longitude: float = Field(..., description="Original longitude in degrees")
    sign: str = Field(..., description="Zodiac sign name")
    degree_in_sign: float = Field(..., ge=0, lt=30, description="Degree within the sign")
    term_ruler: str = Field(..., description="Planet ruling this term")
    term_start: int = Field(..., ge=0, lt=30, description="Start degree of this term")
    term_end: int = Field(..., gt=0, le=30, description="End degree of this term")
    term_system: TermSystemEnum = Field(..., description="Term system used")


class PlanetTermInfo(BaseModel):
    """Term information for a single planet."""

    planet: str = Field(..., description="Planet name")
    term_ruler: str = Field(..., description="Planet ruling this term")
    in_own_term: bool = Field(
        ..., description="Whether the planet is in its own term (+2 dignity points)"
    )


class TermsSummary(BaseModel):
    """Summary of term analysis for a chart."""

    planets_in_own_term: list[str] = Field(
        default_factory=list, description="List of planets in their own terms"
    )
    term_ruler_frequency: dict[str, int] = Field(
        default_factory=dict, description="Count of how many planets each ruler governs"
    )


class ChartTermsResponse(BaseModel):
    """Response for chart-wide term analysis."""

    system: TermSystemEnum = Field(..., description="Term system used")
    planets: list[PlanetTermInfo] = Field(..., description="Term info for each planet")
    summary: TermsSummary = Field(..., description="Analysis summary")


class SignTerms(BaseModel):
    """Terms for a single zodiac sign."""

    terms: list[TermEntry] = Field(..., min_length=5, max_length=5)


class TermsTableResponse(BaseModel):
    """Response for the complete terms reference table."""

    system: TermSystemEnum = Field(..., description="Term system")
    signs: dict[str, list[TermEntry]] = Field(..., description="Terms for each zodiac sign")
