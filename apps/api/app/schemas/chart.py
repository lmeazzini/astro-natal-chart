"""
Birth Chart schemas for request/response validation.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Dict, List, Any


class BirthChartCreate(BaseModel):
    """Schema for creating a new birth chart."""

    person_name: str = Field(..., min_length=1, max_length=100)
    gender: str | None = Field(None, max_length=50)
    birth_datetime: datetime = Field(..., description="Birth date and time in ISO format")
    birth_timezone: str = Field(..., max_length=50, description="Timezone (e.g., America/Sao_Paulo)")
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude")
    city: str | None = Field(None, max_length=100)
    country: str | None = Field(None, max_length=100)
    notes: str | None = None
    tags: List[str] | None = None
    house_system: str = Field(default="placidus", max_length=20)
    zodiac_type: str = Field(default="tropical", max_length=20)
    node_type: str = Field(default="true", max_length=20)


class BirthChartUpdate(BaseModel):
    """Schema for updating a birth chart."""

    person_name: str | None = Field(None, min_length=1, max_length=100)
    gender: str | None = Field(None, max_length=50)
    notes: str | None = None
    tags: List[str] | None = None
    visibility: str | None = Field(None, max_length=20)


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

    planets: List[PlanetPosition]
    houses: List[HousePosition]
    aspects: List[AspectData]
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
    tags: List[str] | None
    house_system: str
    zodiac_type: str
    node_type: str
    chart_data: Dict[str, Any]
    visibility: str
    share_uuid: UUID | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {"from_attributes": True}


class BirthChartList(BaseModel):
    """Schema for list of birth charts."""

    charts: List[BirthChartRead]
    total: int
    page: int
    page_size: int
