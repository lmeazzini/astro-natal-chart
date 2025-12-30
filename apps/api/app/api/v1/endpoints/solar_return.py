"""
Solar Return chart endpoints.

These endpoints provide Solar Return chart calculations and interpretations,
including the full chart for a specific year and comparison to the natal chart.

PREMIUM FEATURE: These endpoints require premium or admin access.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.astro.solar_return import (
    calculate_multiple_solar_returns,
    calculate_solar_return,
    get_solar_return_interpretation,
)
from app.core.context import get_locale
from app.core.dependencies import require_premium
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.solar_return import (
    SolarReturnInterpretationSchema,
    SolarReturnListResponseSchema,
    SolarReturnResponseSchema,
)
from app.services.chart_service import (
    ChartNotFoundError,
    ChartService,
    UnauthorizedAccessError,
    get_chart_service,
)
from app.translations import DEFAULT_LANGUAGE
from app.utils.chart_data_accessor import extract_language_data

router = APIRouter()


def _get_sun_longitude_from_chart_data(chart_data: dict) -> float | None:
    """
    Extract Sun's longitude from chart data.

    Returns:
        Sun's ecliptic longitude or None if not found
    """
    planets = chart_data.get("planets", [])
    for planet in planets:
        if planet.get("name") == "Sun":
            return planet.get("longitude")
    return None


@router.get(
    "/charts/{chart_id}/solar-return",
    response_model=SolarReturnResponseSchema,
    summary="Calculate Solar Return Chart",
    description="""
Calculate Solar Return chart for a birth chart.

Solar Return (Revolução Solar) is a predictive technique that calculates a chart
for the exact moment the Sun returns to its natal position each year. This chart
is used to forecast themes and events for the coming year.

The chart can be calculated for:
- The birth location (default)
- A custom location (relocated Solar Return) using the lat/lon parameters

**Premium Feature**: This endpoint requires premium or admin access.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_return(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_premium)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    year: int = Query(
        default=None,
        description="Year for the Solar Return (defaults to current year)",
    ),
    lat: float | None = Query(
        default=None,
        description="Custom latitude for relocated Solar Return",
    ),
    lon: float | None = Query(
        default=None,
        description="Custom longitude for relocated Solar Return",
    ),
    city: str = Query(
        default="",
        description="City name for relocated Solar Return",
    ),
    country: str = Query(
        default="",
        description="Country name for relocated Solar Return",
    ),
) -> SolarReturnResponseSchema:
    """Get Solar Return chart for a specific year."""
    try:
        chart = await chart_service.get_chart_by_id(chart_id, current_user.id)
    except ChartNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        ) from err
    except UnauthorizedAccessError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chart",
        ) from err

    if not chart.chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart has not been calculated yet",
        )

    # Get language-specific chart data
    locale = get_locale() or DEFAULT_LANGUAGE
    chart_data = extract_language_data(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Extract Sun's longitude from chart
    natal_sun_longitude = _get_sun_longitude_from_chart_data(chart_data)
    if natal_sun_longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sun data not found in chart",
        )

    # Default to current year if not specified
    if year is None:
        year = datetime.now().year

    # Use custom location or birth location
    sr_latitude = lat if lat is not None else chart.latitude
    sr_longitude = lon if lon is not None else chart.longitude
    sr_city = city if city else (chart.city or "")
    sr_country = country if country else (chart.country or "")

    # Calculate Solar Return
    sr_data = calculate_solar_return(
        natal_sun_longitude=natal_sun_longitude,
        birth_datetime=chart.birth_datetime,
        target_year=year,
        latitude=sr_latitude,
        longitude=sr_longitude,
        timezone=chart.birth_timezone or "UTC",
        city=sr_city,
        country=sr_country,
        house_system=chart.house_system or "placidus",
        natal_chart_data=chart_data,
    )

    return SolarReturnResponseSchema(**sr_data)


@router.get(
    "/charts/{chart_id}/solar-returns",
    response_model=SolarReturnListResponseSchema,
    summary="Calculate Multiple Solar Returns",
    description="""
Calculate Solar Return charts for a range of years.

This endpoint calculates Solar Return charts for multiple years at once,
useful for comparing yearly themes over time.

**Premium Feature**: This endpoint requires premium or admin access.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_returns(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_premium)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    start_year: int = Query(..., description="First year in the range"),
    end_year: int = Query(..., description="Last year in the range"),
    lat: float | None = Query(
        default=None,
        description="Custom latitude for relocated Solar Returns",
    ),
    lon: float | None = Query(
        default=None,
        description="Custom longitude for relocated Solar Returns",
    ),
) -> SolarReturnListResponseSchema:
    """Get Solar Return charts for multiple years."""
    # Validate year range
    if end_year < start_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_year must be greater than or equal to start_year",
        )

    if end_year - start_year > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum range is 20 years",
        )

    try:
        chart = await chart_service.get_chart_by_id(chart_id, current_user.id)
    except ChartNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        ) from err
    except UnauthorizedAccessError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chart",
        ) from err

    if not chart.chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart has not been calculated yet",
        )

    # Get language-specific chart data
    locale = get_locale() or DEFAULT_LANGUAGE
    chart_data = extract_language_data(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Extract Sun's longitude from chart
    natal_sun_longitude = _get_sun_longitude_from_chart_data(chart_data)
    if natal_sun_longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sun data not found in chart",
        )

    # Use custom location or birth location
    sr_latitude = lat if lat is not None else chart.latitude
    sr_longitude = lon if lon is not None else chart.longitude

    # Calculate multiple Solar Returns
    returns = calculate_multiple_solar_returns(
        natal_sun_longitude=natal_sun_longitude,
        birth_datetime=chart.birth_datetime,
        start_year=start_year,
        end_year=end_year,
        latitude=sr_latitude,
        longitude=sr_longitude,
        timezone=chart.birth_timezone or "UTC",
        city=chart.city or "",
        country=chart.country or "",
        house_system=chart.house_system or "placidus",
    )

    return SolarReturnListResponseSchema(
        returns=returns,
        start_year=start_year,
        end_year=end_year,
    )


@router.get(
    "/charts/{chart_id}/solar-return/interpretation",
    response_model=SolarReturnInterpretationSchema,
    summary="Get Solar Return Interpretation",
    description="""
Get astrological interpretation for Solar Return.

Provides detailed interpretations based on:
- General Solar Return meaning
- Solar Return Ascendant sign (12 variations)
- Solar Return Sun's house placement (12 variations)

**Premium Feature**: This endpoint requires premium or admin access.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_return_interp(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_premium)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    year: int = Query(
        default=None,
        description="Year for the Solar Return (defaults to current year)",
    ),
    lat: float | None = Query(
        default=None,
        description="Custom latitude for relocated Solar Return",
    ),
    lon: float | None = Query(
        default=None,
        description="Custom longitude for relocated Solar Return",
    ),
) -> SolarReturnInterpretationSchema:
    """Get Solar Return interpretation for a chart."""
    try:
        chart = await chart_service.get_chart_by_id(chart_id, current_user.id)
    except ChartNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart not found",
        ) from err
    except UnauthorizedAccessError as err:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this chart",
        ) from err

    if not chart.chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart has not been calculated yet",
        )

    # Get language-specific chart data
    locale = get_locale() or DEFAULT_LANGUAGE
    chart_data = extract_language_data(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Extract Sun's longitude from chart
    natal_sun_longitude = _get_sun_longitude_from_chart_data(chart_data)
    if natal_sun_longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sun data not found in chart",
        )

    # Default to current year if not specified
    if year is None:
        year = datetime.now().year

    # Use custom location or birth location
    sr_latitude = lat if lat is not None else chart.latitude
    sr_longitude = lon if lon is not None else chart.longitude

    # Calculate Solar Return to get ascendant and sun house
    sr_data = calculate_solar_return(
        natal_sun_longitude=natal_sun_longitude,
        birth_datetime=chart.birth_datetime,
        target_year=year,
        latitude=sr_latitude,
        longitude=sr_longitude,
        timezone=chart.birth_timezone or "UTC",
        city=chart.city or "",
        country=chart.country or "",
        house_system=chart.house_system or "placidus",
    )

    sr_chart = sr_data.get("chart", {})
    sr_ascendant_sign = sr_chart.get("ascendant_sign", "Aries")
    sr_sun_house = sr_chart.get("sun_house", 1)

    # Get interpretation
    interpretation = get_solar_return_interpretation(
        sr_ascendant_sign=sr_ascendant_sign,
        sr_sun_house=sr_sun_house,
        language=locale,
    )

    return SolarReturnInterpretationSchema(**interpretation)
