"""
Geocoding endpoints for location search.
"""

from typing import List
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.services.geocoding_service import GeocodingService, LocationResult


router = APIRouter()


class LocationResponse(BaseModel):
    """Location search result response."""

    display_name: str
    latitude: float
    longitude: float
    city: str
    country: str
    country_code: str


@router.get("/search", response_model=List[LocationResponse])
async def search_location(
    q: str = Query(..., min_length=2, description="City name or address to search"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of results"),
):
    """
    Search for locations by city name or address.

    Returns coordinates, city name, and country for matching locations.

    Example:
    - `/api/v1/geocoding/search?q=São Paulo`
    - `/api/v1/geocoding/search?q=New York&limit=3`
    """
    geocoding_service = GeocodingService()

    try:
        results = await geocoding_service.search_location(q, limit)

        if not results:
            return []

        return [
            LocationResponse(
                display_name=result.display_name,
                latitude=result.latitude,
                longitude=result.longitude,
                city=result.city,
                country=result.country,
                country_code=result.country_code,
            )
            for result in results
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search location: {str(e)}",
        )


@router.get("/coordinates")
async def get_coordinates(
    city: str = Query(..., min_length=2, description="City name"),
    country: str = Query("", description="Country name (optional, improves accuracy)"),
):
    """
    Get coordinates for a specific city.

    Returns latitude and longitude for the given city.

    Example:
    - `/api/v1/geocoding/coordinates?city=São Paulo&country=Brazil`
    """
    geocoding_service = GeocodingService()

    try:
        result = await geocoding_service.get_coordinates(city, country)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Location not found: {city}",
            )

        return LocationResponse(
            display_name=result.display_name,
            latitude=result.latitude,
            longitude=result.longitude,
            city=result.city,
            country=result.country,
            country_code=result.country_code,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get coordinates: {str(e)}",
        )
