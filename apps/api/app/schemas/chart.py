"""
Birth Chart schemas for request/response validation.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class BirthChartCreate(BaseModel):
    """Schema for creating a new birth chart."""

    person_name: str = Field(..., min_length=1, max_length=100)
    gender: str | None = Field(None, max_length=50)
    birth_datetime: datetime = Field(..., description="Birth date and time in ISO format")
    birth_timezone: str = Field(
        ..., max_length=50, description="Timezone (e.g., America/Sao_Paulo)"
    )
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude")
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    notes: str | None = None
    tags: list[str] | None = None
    house_system: str = Field(default="placidus", max_length=20)
    zodiac_type: str = Field(default="tropical", max_length=20)
    node_type: str = Field(default="true", max_length=20)


class BirthChartUpdate(BaseModel):
    """Schema for updating a birth chart.

    All fields are optional. Only provided fields will be updated.
    If birth data (datetime, timezone, lat/lon) changes, chart will be recalculated.
    """

    # Personal info (no recalculation needed)
    person_name: str | None = Field(None, min_length=1, max_length=100)
    gender: str | None = Field(None, max_length=50)
    notes: str | None = None
    tags: list[str] | None = None
    visibility: str | None = Field(None, max_length=20)

    # Birth data (triggers recalculation if changed)
    birth_datetime: datetime | None = Field(
        None, description="Birth date and time in ISO format"
    )
    birth_timezone: str | None = Field(
        None, max_length=50, description="Timezone (e.g., America/Sao_Paulo)"
    )
    latitude: float | None = Field(
        None, ge=-90, le=90, description="Birth location latitude"
    )
    longitude: float | None = Field(
        None, ge=-180, le=180, description="Birth location longitude"
    )
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)

    # Technical settings (triggers recalculation if changed)
    house_system: str | None = Field(None, max_length=20)
    zodiac_type: str | None = Field(None, max_length=20)
    node_type: str | None = Field(None, max_length=20)


class PlanetPosition(BaseModel):
    """Schema for planet position data."""

    name: str
    longitude: float
    latitude: float
    speed: float
    sign: str
    degree: int
    minute: int
    second: int
    house: int
    retrograde: bool


class HousePosition(BaseModel):
    """Schema for house cusp position."""

    house: int
    longitude: float
    sign: str
    degree: int
    minute: int
    second: int


class AspectData(BaseModel):
    """Schema for aspect between two planets."""

    planet1: str
    planet2: str
    aspect: str
    angle: float
    orb: float
    applying: bool


class ChartData(BaseModel):
    """Schema for complete chart calculation data."""

    planets: list[PlanetPosition]
    houses: list[HousePosition]
    aspects: list[AspectData]
    ascendant: float
    midheaven: float
    calculation_timestamp: datetime


class BirthChartRead(BaseModel):
    """Schema for birth chart response."""

    id: UUID
    user_id: UUID
    person_name: str
    gender: str | None
    birth_datetime: datetime
    birth_timezone: str
    latitude: float
    longitude: float
    city: str | None
    country: str | None
    notes: str | None
    tags: list[str] | None
    house_system: str
    zodiac_type: str
    node_type: str
    status: str = Field(
        default="processing",
        description="Processing status: processing, completed, failed",
    )
    progress: int = Field(default=0, ge=0, le=100, description="Processing progress (0-100)")
    error_message: str | None = Field(None, description="Error message if status is failed")
    chart_data: dict[str, Any] | None
    pdf_url: str | None = Field(None, description="URL to generated PDF (S3 or local)")
    pdf_generated_at: datetime | None = Field(None, description="When PDF was generated")
    pdf_generating: bool = Field(default=False, description="Is PDF currently being generated")
    pdf_task_id: str | None = Field(None, description="Celery task ID for PDF generation")
    visibility: str
    share_uuid: UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class BirthChartList(BaseModel):
    """Schema for list of birth charts."""

    charts: list[BirthChartRead]
    total: int
    page: int
    page_size: int


class ChartStatusResponse(BaseModel):
    """Schema for chart processing status response."""

    id: UUID
    status: str = Field(description="Processing status: processing, completed, failed")
    progress: int = Field(ge=0, le=100, description="Processing progress (0-100)")
    error_message: str | None = Field(None, description="Error message if status is failed")
    task_id: str | None = Field(None, description="Celery task ID for tracking")


class PDFDownloadResponse(BaseModel):
    """Schema for PDF download/status response."""

    status: str = Field(
        description="PDF status: ready, generating, failed, not_found"
    )
    download_url: str | None = Field(
        None,
        description="Presigned S3 URL for download (expires in 1 hour) or local URL",
    )
    task_id: str | None = Field(None, description="Celery task ID if generating")
    expires_in: int | None = Field(
        None,
        description="Seconds until download URL expires (for S3 presigned URLs)",
    )
    generated_at: datetime | None = Field(
        None, description="Timestamp when PDF was generated"
    )
    message: str | None = Field(None, description="Human-readable status message")


class PDFDownloadURLResponse(BaseModel):
    """Schema for PDF download URL endpoint response."""

    download_url: str = Field(
        description="Direct S3 presigned URL or local file URL for download"
    )
    filename: str = Field(
        description="Suggested filename for the PDF download"
    )
    expires_in: int | None = Field(
        None,
        description="Seconds until download URL expires (only for S3 presigned URLs)",
    )
    content_type: str = Field(
        default="application/pdf",
        description="MIME type of the file"
    )
