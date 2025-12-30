"""
Solar Return schemas for API responses.

These schemas define the API response models for Solar Return
calculation and interpretation endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Location information for the Solar Return chart."""

    latitude: float = Field(..., description="Geographic latitude")
    longitude: float = Field(..., description="Geographic longitude")
    city: str = Field(default="", description="City name")
    country: str = Field(default="", description="Country name")
    timezone: str = Field(..., description="Timezone identifier")


class SolarReturnPlanetSchema(BaseModel):
    """Planet position in the Solar Return chart."""

    name: str = Field(..., description="Planet name")
    longitude: float = Field(..., description="Ecliptic longitude")
    sign: str = Field(..., description="Zodiac sign")
    degree: float = Field(..., description="Degree within the sign (0-30)")
    house: int = Field(..., ge=1, le=12, description="House placement")
    retrograde: bool = Field(default=False, description="Whether the planet is retrograde")


class SolarReturnHouseSchema(BaseModel):
    """House information in the Solar Return chart."""

    number: int = Field(..., ge=1, le=12, description="House number")
    cusp: float = Field(..., description="House cusp longitude")
    sign: str = Field(..., description="Sign on the cusp")


class SolarReturnAspectSchema(BaseModel):
    """Aspect in the Solar Return chart."""

    planet1: str = Field(..., description="First planet")
    planet2: str = Field(..., description="Second planet")
    aspect: str = Field(..., description="Aspect name")
    angle: float = Field(..., description="Exact angle")
    orb: float = Field(..., description="Orb (deviation from exact)")


class SRToNatalAspectSchema(BaseModel):
    """Aspect between Solar Return and natal planets."""

    sr_planet: str = Field(..., description="Solar Return planet")
    natal_planet: str = Field(..., description="Natal planet")
    aspect: str = Field(..., description="Aspect name")
    angle: float = Field(..., description="Aspect angle")
    orb: float = Field(..., description="Orb")
    is_major: bool = Field(..., description="Whether this is a major aspect")


class SolarReturnChartSchema(BaseModel):
    """Complete Solar Return chart data."""

    return_datetime: datetime = Field(..., description="Exact moment of the Sun return (UTC)")
    return_year: int = Field(..., description="Year of the Solar Return")
    location: LocationSchema = Field(..., description="Location where the chart is calculated")
    natal_sun_longitude: float = Field(..., description="Natal Sun's ecliptic longitude")
    return_sun_longitude: float = Field(
        ..., description="Sun's longitude at return (same as natal)"
    )
    planets: list[dict[str, Any]] = Field(..., description="Planet positions")
    houses: list[dict[str, Any]] = Field(..., description="House cusps")
    aspects: list[dict[str, Any]] = Field(..., description="Aspects in the SR chart")
    ascendant: float = Field(..., description="Ascendant longitude")
    ascendant_sign: str = Field(..., description="Ascendant sign")
    ascendant_degree: float = Field(..., description="Ascendant degree within sign")
    midheaven: float = Field(..., description="Midheaven longitude")
    midheaven_sign: str = Field(..., description="Midheaven sign")
    midheaven_degree: float = Field(..., description="Midheaven degree within sign")
    sun_house: int = Field(..., ge=1, le=12, description="House where SR Sun is placed")


class SolarReturnComparisonSchema(BaseModel):
    """Comparison between Solar Return and natal chart."""

    sr_asc_in_natal_house: int = Field(
        ..., ge=1, le=12, description="Which natal house the SR Ascendant falls in"
    )
    sr_mc_in_natal_house: int = Field(
        ..., ge=1, le=12, description="Which natal house the SR MC falls in"
    )
    sr_planets_in_natal_houses: dict[str, int] = Field(
        ..., description="Mapping of SR planets to natal houses"
    )
    natal_planets_in_sr_houses: dict[str, int] = Field(
        ..., description="Mapping of natal planets to SR houses"
    )
    key_aspects: list[SRToNatalAspectSchema] = Field(
        ..., description="Key aspects between SR and natal planets"
    )


class SolarReturnResponseSchema(BaseModel):
    """Complete Solar Return response including chart and comparison."""

    chart: SolarReturnChartSchema = Field(..., description="The Solar Return chart data")
    comparison: SolarReturnComparisonSchema | None = Field(
        None, description="Comparison to natal chart (if natal data provided)"
    )


class SolarReturnInterpretationSchema(BaseModel):
    """Solar Return interpretation response."""

    title: str = Field(..., description="Localized title")
    sr_ascendant_sign: str = Field(..., description="Solar Return ascendant sign")
    sr_sun_house: int = Field(..., ge=1, le=12, description="House where SR Sun is placed")
    general_introduction: str = Field(..., description="General introduction to Solar Return")
    general_interpretation: str = Field(..., description="General yearly themes interpretation")
    ascendant_interpretation: str = Field(
        ..., description="Interpretation based on SR ascendant sign"
    )
    sun_house_interpretation: str = Field(..., description="Interpretation based on SR Sun's house")


class SolarReturnListResponseSchema(BaseModel):
    """Response for multiple Solar Returns."""

    returns: list[SolarReturnResponseSchema] = Field(..., description="List of Solar Return charts")
    start_year: int = Field(..., description="First year in the range")
    end_year: int = Field(..., description="Last year in the range")
