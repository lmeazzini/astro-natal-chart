"""
Timezone schemas for request/response validation.
"""

from pydantic import BaseModel, Field


class TimezoneInfo(BaseModel):
    """Schema for timezone information."""

    id: str = Field(..., description="IANA timezone identifier (e.g., America/Sao_Paulo)")
    name: str = Field(..., description="Human-readable name (e.g., Sao Paulo)")
    region: str = Field(..., description="Region name (e.g., Americas)")
    offset: str = Field(..., description="UTC offset string (e.g., UTC-03:00)")
    offset_hours: float = Field(..., description="UTC offset in hours (e.g., -3.0)")
    is_dst: bool = Field(..., description="Whether currently in daylight saving time")
    abbreviation: str = Field(..., description="Timezone abbreviation (e.g., BRT)")


class TimezoneDetectRequest(BaseModel):
    """Schema for timezone detection from coordinates."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class TimezoneDetectResponse(BaseModel):
    """Schema for timezone detection response."""

    timezone_id: str | None = Field(
        None, description="Detected IANA timezone identifier"
    )
    timezone_info: TimezoneInfo | None = Field(
        None, description="Full timezone information if detected"
    )
    detected: bool = Field(..., description="Whether timezone was successfully detected")


class TimezoneSearchResponse(BaseModel):
    """Schema for timezone search results."""

    results: list[TimezoneInfo] = Field(..., description="List of matching timezones")
    query: str = Field(..., description="Original search query")
    count: int = Field(..., description="Number of results")


class TimezoneListResponse(BaseModel):
    """Schema for listing all timezones."""

    timezones: list[TimezoneInfo] = Field(..., description="List of all timezones")
    popular: list[TimezoneInfo] = Field(..., description="List of popular timezones")
    total: int = Field(..., description="Total number of timezones")


class TimezoneGroupedResponse(BaseModel):
    """Schema for timezones grouped by region."""

    regions: dict[str, list[TimezoneInfo]] = Field(
        ..., description="Timezones grouped by region"
    )
    total: int = Field(..., description="Total number of timezones")


class TimezoneValidateResponse(BaseModel):
    """Schema for timezone validation response."""

    timezone_id: str = Field(..., description="Timezone identifier that was validated")
    valid: bool = Field(..., description="Whether the timezone is valid")
    info: TimezoneInfo | None = Field(
        None, description="Timezone info if valid"
    )
