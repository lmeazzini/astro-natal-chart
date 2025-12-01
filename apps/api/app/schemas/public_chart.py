"""
Public Chart schemas for request/response validation.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class PublicChartCreate(BaseModel):
    """Schema for creating a new public chart (admin only)."""

    slug: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    full_name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)
    birth_datetime: datetime = Field(..., description="Birth date and time in ISO format")
    birth_timezone: str = Field(
        ..., max_length=100, description="Timezone (e.g., America/Sao_Paulo)"
    )
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude")
    city: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    house_system: str = Field(default="placidus", max_length=50)
    photo_url: str | None = None
    # Legacy single-language fields (backward compat)
    short_bio: str | None = None
    highlights: list[str] | None = None
    meta_title: str | None = Field(None, max_length=255)
    meta_description: str | None = None
    meta_keywords: list[str] | None = None
    # i18n multilingual fields: {lang_code: content}
    short_bio_i18n: dict[str, str] | None = None
    highlights_i18n: dict[str, list[str]] | None = None
    meta_title_i18n: dict[str, str] | None = None
    meta_description_i18n: dict[str, str] | None = None
    meta_keywords_i18n: dict[str, list[str]] | None = None
    is_published: bool = Field(default=False)
    featured: bool = Field(default=False)


class PublicChartUpdate(BaseModel):
    """Schema for updating a public chart (admin only).

    All fields are optional. Only provided fields will be updated.
    If birth data changes, chart will be recalculated.
    """

    slug: str | None = Field(None, min_length=1, max_length=255, pattern=r"^[a-z0-9-]+$")
    full_name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)
    birth_datetime: datetime | None = Field(None, description="Birth date and time in ISO format")
    birth_timezone: str | None = Field(
        None, max_length=100, description="Timezone (e.g., America/Sao_Paulo)"
    )
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    city: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    house_system: str | None = Field(None, max_length=50)
    photo_url: str | None = None
    # Legacy single-language fields (backward compat)
    short_bio: str | None = None
    highlights: list[str] | None = None
    meta_title: str | None = Field(None, max_length=255)
    meta_description: str | None = None
    meta_keywords: list[str] | None = None
    # i18n multilingual fields: {lang_code: content}
    short_bio_i18n: dict[str, str] | None = None
    highlights_i18n: dict[str, list[str]] | None = None
    meta_title_i18n: dict[str, str] | None = None
    meta_description_i18n: dict[str, str] | None = None
    meta_keywords_i18n: dict[str, list[str]] | None = None
    is_published: bool | None = None
    featured: bool | None = None


class PublicChartPreview(BaseModel):
    """Schema for public chart preview in listings.

    The short_bio field returns the language-resolved value based on ?lang= param.
    """

    id: UUID
    slug: str
    full_name: str
    category: str | None
    birth_datetime: datetime
    birth_timezone: str
    city: str | None
    country: str | None
    photo_url: str | None
    short_bio: str | None  # Language-resolved value
    view_count: int
    featured: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PublicChartDetail(BaseModel):
    """Schema for full public chart response.

    Text fields (short_bio, highlights, meta_*) return language-resolved values
    based on the ?lang= query parameter.
    """

    id: UUID
    slug: str
    full_name: str
    category: str | None
    birth_datetime: datetime
    birth_timezone: str
    latitude: float
    longitude: float
    city: str | None
    country: str | None
    chart_data: dict[str, Any] | None
    house_system: str
    photo_url: str | None
    # Language-resolved text fields
    short_bio: str | None
    highlights: list[str] | None
    meta_title: str | None
    meta_description: str | None
    meta_keywords: list[str] | None
    view_count: int
    is_published: bool
    featured: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PublicChartList(BaseModel):
    """Schema for paginated list of public charts."""

    charts: list[PublicChartPreview]
    total: int
    page: int
    page_size: int


# Categories for filtering
PUBLIC_CHART_CATEGORIES = [
    "scientist",
    "artist",
    "leader",
    "writer",
    "athlete",
    "actor",
    "musician",
    "entrepreneur",
    "historical",
    "other",
]
