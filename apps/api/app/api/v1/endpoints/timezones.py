"""
Timezone API endpoints.

Provides endpoints for:
- Listing all available timezones
- Searching timezones
- Detecting timezone from coordinates
- Validating timezone identifiers
"""

from datetime import datetime

from fastapi import APIRouter, Query

from app.schemas.timezone import (
    TimezoneDetectRequest,
    TimezoneDetectResponse,
    TimezoneInfo,
    TimezoneListResponse,
    TimezoneSearchResponse,
    TimezoneValidateResponse,
)
from app.services.timezone_service import timezone_service

router = APIRouter()


@router.get("", response_model=TimezoneListResponse)
async def list_timezones(
    popular_only: bool = Query(
        False,
        description="If true, return only popular timezones",
    ),
) -> TimezoneListResponse:
    """
    List all available IANA timezones.

    Returns both a complete list and a separate list of popular timezones
    for easier selection in UI dropdowns.
    """
    # Get popular timezones with info
    popular_ids = timezone_service.get_popular_timezones()
    popular = []
    for tz_id in popular_ids:
        info = timezone_service.get_timezone_info(tz_id)
        if info:
            popular.append(TimezoneInfo(**info.to_dict()))

    if popular_only:
        return TimezoneListResponse(
            timezones=popular,
            popular=popular,
            total=len(popular),
        )

    # Get all timezones with info
    all_ids = timezone_service.get_all_timezones()
    timezones = []
    for tz_id in all_ids:
        info = timezone_service.get_timezone_info(tz_id)
        if info:
            timezones.append(TimezoneInfo(**info.to_dict()))

    return TimezoneListResponse(
        timezones=timezones,
        popular=popular,
        total=len(timezones),
    )


@router.get("/search", response_model=TimezoneSearchResponse)
async def search_timezones(
    q: str = Query(
        ...,
        min_length=1,
        max_length=100,
        description="Search query (city name, country, or timezone ID)",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Maximum number of results",
    ),
) -> TimezoneSearchResponse:
    """
    Search timezones by name, city, or region.

    Useful for autocomplete functionality in timezone selection UI.
    Popular timezones are boosted in search results.
    """
    results = timezone_service.search_timezones(q, limit)
    return TimezoneSearchResponse(
        results=[TimezoneInfo(**r) for r in results],
        query=q,
        count=len(results),
    )


@router.post("/detect", response_model=TimezoneDetectResponse)
async def detect_timezone(
    request: TimezoneDetectRequest,
) -> TimezoneDetectResponse:
    """
    Detect timezone from geographic coordinates.

    Uses the timezonefinder library to determine the timezone
    at a specific latitude/longitude. Useful for auto-selecting
    timezone when user enters a birth location.
    """
    timezone_id = timezone_service.detect_timezone_from_coordinates(
        request.latitude,
        request.longitude,
    )

    if timezone_id:
        info = timezone_service.get_timezone_info(timezone_id)
        return TimezoneDetectResponse(
            timezone_id=timezone_id,
            timezone_info=TimezoneInfo(**info.to_dict()) if info else None,
            detected=True,
        )

    return TimezoneDetectResponse(
        timezone_id=None,
        timezone_info=None,
        detected=False,
    )


@router.get("/validate/{timezone_id:path}", response_model=TimezoneValidateResponse)
async def validate_timezone(
    timezone_id: str,
    reference_date: datetime | None = Query(
        None,
        description="Optional date for offset calculation (defaults to now)",
    ),
) -> TimezoneValidateResponse:
    """
    Validate a timezone identifier and get its information.

    The timezone_id should be an IANA timezone identifier
    (e.g., "America/Sao_Paulo", "Europe/London").

    Optionally provide a reference date to get the offset
    for a specific historical date (important for birth charts).
    """
    is_valid = timezone_service.is_valid_timezone(timezone_id)

    if is_valid:
        info = timezone_service.get_timezone_info(timezone_id, reference_date)
        return TimezoneValidateResponse(
            timezone_id=timezone_id,
            valid=True,
            info=TimezoneInfo(**info.to_dict()) if info else None,
        )

    return TimezoneValidateResponse(
        timezone_id=timezone_id,
        valid=False,
        info=None,
    )


@router.get("/{timezone_id:path}", response_model=TimezoneInfo)
async def get_timezone_info(
    timezone_id: str,
    reference_date: datetime | None = Query(
        None,
        description="Optional date for offset calculation (defaults to now)",
    ),
) -> TimezoneInfo:
    """
    Get detailed information about a specific timezone.

    Returns current offset, DST status, and other details.
    Optionally provide a reference date to get historical offset.
    """
    from fastapi import HTTPException

    info = timezone_service.get_timezone_info(timezone_id, reference_date)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"Timezone '{timezone_id}' not found",
        )

    return TimezoneInfo(**info.to_dict())
