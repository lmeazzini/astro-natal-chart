"""
Geocoding service for location search and coordinate lookup.
Uses Nominatim (OpenStreetMap) as primary provider (free, no API key needed).
Falls back to OpenCage if API key is configured.
"""

from typing import List, Optional
import httpx
from app.core.config import settings


class LocationResult:
    """Location search result with coordinates."""

    def __init__(
        self,
        display_name: str,
        latitude: float,
        longitude: float,
        city: str = "",
        country: str = "",
        country_code: str = "",
    ):
        self.display_name = display_name
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.country = country
        self.country_code = country_code


class GeocodingService:
    """Service for geocoding operations."""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opencage_url = "https://api.opencagedata.com/geocode/v1/json"
        self.timeout = 10.0

    async def search_location(self, query: str, limit: int = 5) -> List[LocationResult]:
        """
        Search for locations by city name or address.

        Args:
            query: City name or address to search
            limit: Maximum number of results to return

        Returns:
            List of LocationResult objects
        """
        # Try Nominatim first (free, no API key needed)
        results = await self._search_nominatim(query, limit)

        if not results and settings.OPENCAGE_API_KEY:
            # Fallback to OpenCage if configured
            results = await self._search_opencage(query, limit)

        return results

    async def _search_nominatim(self, query: str, limit: int) -> List[LocationResult]:
        """
        Search using Nominatim (OpenStreetMap).
        Free service, no API key required.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.nominatim_url,
                    params={
                        "q": query,
                        "format": "json",
                        "limit": limit,
                        "addressdetails": 1,
                    },
                    headers={
                        "User-Agent": settings.NOMINATIM_USER_AGENT,
                    },
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    return []

                data = response.json()

                results = []
                for item in data:
                    address = item.get("address", {})

                    # Extract city name (try different fields)
                    city = (
                        address.get("city")
                        or address.get("town")
                        or address.get("village")
                        or address.get("municipality")
                        or ""
                    )

                    result = LocationResult(
                        display_name=item.get("display_name", ""),
                        latitude=float(item.get("lat", 0)),
                        longitude=float(item.get("lon", 0)),
                        city=city,
                        country=address.get("country", ""),
                        country_code=address.get("country_code", "").upper(),
                    )
                    results.append(result)

                return results

        except Exception as e:
            print(f"Nominatim search error: {e}")
            return []

    async def _search_opencage(self, query: str, limit: int) -> List[LocationResult]:
        """
        Search using OpenCage Geocoding API.
        Requires API key in settings.
        """
        if not settings.OPENCAGE_API_KEY:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.opencage_url,
                    params={
                        "q": query,
                        "key": settings.OPENCAGE_API_KEY,
                        "limit": limit,
                        "no_annotations": 1,
                    },
                    timeout=self.timeout,
                )

                if response.status_code != 200:
                    return []

                data = response.json()

                results = []
                for item in data.get("results", []):
                    components = item.get("components", {})
                    geometry = item.get("geometry", {})

                    result = LocationResult(
                        display_name=item.get("formatted", ""),
                        latitude=float(geometry.get("lat", 0)),
                        longitude=float(geometry.get("lng", 0)),
                        city=components.get("city", ""),
                        country=components.get("country", ""),
                        country_code=components.get("country_code", "").upper(),
                    )
                    results.append(result)

                return results

        except Exception as e:
            print(f"OpenCage search error: {e}")
            return []

    async def get_coordinates(self, city: str, country: str = "") -> Optional[LocationResult]:
        """
        Get coordinates for a specific city.

        Args:
            city: City name
            country: Country name (optional, helps accuracy)

        Returns:
            LocationResult with coordinates, or None if not found
        """
        query = f"{city}, {country}" if country else city
        results = await self.search_location(query, limit=1)

        return results[0] if results else None
