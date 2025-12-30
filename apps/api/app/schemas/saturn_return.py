"""
Saturn Return schemas for API responses.

These schemas define the API response models for Saturn Return
calculation and interpretation endpoints.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class SaturnReturnPassSchema(BaseModel):
    """A single pass of Saturn over the natal position."""

    date: datetime = Field(..., description="Date and time of the pass (UTC)")
    longitude: float = Field(..., description="Saturn's ecliptic longitude at this pass")
    is_retrograde: bool = Field(..., description="Whether Saturn is retrograde during this pass")
    pass_number: int = Field(..., ge=1, le=3, description="Pass number (1, 2, or 3)")


class SaturnReturnSchema(BaseModel):
    """A complete Saturn Return event (all passes)."""

    return_number: int = Field(
        ..., ge=1, le=3, description="Which Saturn Return (1st, 2nd, or 3rd)"
    )
    passes: list[SaturnReturnPassSchema] = Field(
        ..., description="All passes for this return (typically 3)"
    )
    start_date: datetime = Field(..., description="Date of the first pass")
    end_date: datetime = Field(..., description="Date of the last pass")
    age_at_return: float = Field(..., description="Age at the first pass of this return")


class SaturnReturnAnalysisSchema(BaseModel):
    """Complete Saturn Return analysis response."""

    natal_saturn_longitude: float = Field(..., description="Natal Saturn ecliptic longitude")
    natal_saturn_sign: str = Field(..., description="Zodiac sign of natal Saturn")
    natal_saturn_house: int = Field(
        ..., ge=1, le=12, description="House where natal Saturn is placed"
    )
    natal_saturn_degree: float = Field(..., description="Degree within the sign (0-30)")
    current_saturn_longitude: float = Field(..., description="Current Saturn ecliptic longitude")
    current_saturn_sign: str = Field(..., description="Current zodiac sign of Saturn")
    cycle_progress_percent: float = Field(
        ..., ge=0, le=100, description="Progress through current Saturn cycle (0-100%)"
    )
    days_until_next_return: int | None = Field(
        None, description="Days until the next Saturn Return (null if unknown)"
    )
    past_returns: list[SaturnReturnSchema] = Field(
        default_factory=list, description="Past Saturn Returns"
    )
    current_return: SaturnReturnSchema | None = Field(
        None, description="Currently active Saturn Return (if happening now)"
    )
    next_return: SaturnReturnSchema | None = Field(None, description="Next upcoming Saturn Return")


class SaturnReturnInterpretationSchema(BaseModel):
    """Saturn Return interpretation response."""

    title: str = Field(..., description="Localized title")
    natal_saturn_sign: str = Field(..., description="Zodiac sign of natal Saturn")
    natal_saturn_house: int = Field(
        ..., ge=1, le=12, description="House where natal Saturn is placed"
    )
    general_introduction: str = Field(..., description="General introduction to Saturn Return")
    general_interpretation: str = Field(
        ..., description="General interpretation based on return number"
    )
    sign_interpretation: str = Field(..., description="Interpretation based on natal Saturn's sign")
    house_interpretation: str = Field(
        ..., description="Interpretation based on natal Saturn's house"
    )
    current_phase_interpretation: str | None = Field(
        None, description="Interpretation of the current phase (if in a return)"
    )
