"""
Solar Return chart endpoints.

These endpoints provide Solar Return chart calculations and interpretations,
including the full chart for a specific year and comparison to the natal chart.

CREDIT FEATURE: These endpoints consume credits (2 per analysis).
Results are cached per year in chart_data to avoid re-consumption.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.astro.solar_return import (
    calculate_multiple_solar_returns,
    calculate_solar_return,
    get_solar_return_interpretation,
)
from app.core.context import get_locale
from app.core.credit_config import get_feature_cost
from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.models.enums import FeatureType
from app.models.user import User
from app.schemas.solar_return import (
    SolarReturnInterpretationSchema,
    SolarReturnListResponseSchema,
    SolarReturnResponseSchema,
)
from app.services import credit_service
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


def _get_solar_return_cache_key(year: int, lat: float, lon: float) -> str:
    """Generate cache key for Solar Return including location."""
    return f"{year}_{lat:.4f}_{lon:.4f}"


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

**Credit Cost**: 2 credits per year (first calculation only).
If you have already paid for this year on this chart, no credits will be charged.
""",
    responses={
        402: {"description": "Insufficient credits"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_return(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
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

    # Default to current year if not specified
    if year is None:
        year = datetime.now().year

    # Use custom location or birth location
    sr_latitude = lat if lat is not None else chart.latitude
    sr_longitude = lon if lon is not None else chart.longitude
    sr_city = city if city else (chart.city or "")
    sr_country = country if country else (chart.country or "")

    # Check cache for this year/location combination
    cache_key = _get_solar_return_cache_key(year, sr_latitude, sr_longitude)
    solar_returns_cache = chart_data.get("solar_returns", {})
    cached_sr = solar_returns_cache.get(cache_key)

    if cached_sr:
        # Return cached data without consuming credits
        return SolarReturnResponseSchema(**cached_sr)

    # Check if this specific year is already unlocked (previously paid)
    year_unlocked = await credit_service.has_solar_return_year_unlocked(
        db=db,
        user_id=current_user.id,
        chart_id=chart_id,
        year=year,
    )

    # If not unlocked and not admin, check for sufficient credits
    if not year_unlocked and not current_user.is_admin:
        has_credits, required, available = await credit_service.has_sufficient_credits(
            db=db,
            user_id=current_user.id,
            feature_type=FeatureType.SOLAR_RETURN.value,
        )
        # Unlimited plans have available == -1
        if available != -1 and not has_credits:
            cost = get_feature_cost(FeatureType.SOLAR_RETURN.value)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "insufficient_credits",
                    "message": f"This feature requires {required} credits. You have {available} credits available.",
                    "feature_type": FeatureType.SOLAR_RETURN.value,
                    "required_credits": required,
                    "available_credits": available,
                    "feature_cost": cost,
                },
            )

    # Extract Sun's longitude from chart
    natal_sun_longitude = _get_sun_longitude_from_chart_data(chart_data)
    if natal_sun_longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sun data not found in chart",
        )

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

    # Cache the result in chart_data (flat format for consistency)
    if "solar_returns" not in chart.chart_data:
        chart.chart_data["solar_returns"] = {}
    chart.chart_data["solar_returns"][cache_key] = sr_data
    await db.commit()

    # Consume credits only if this year was not previously unlocked
    if not year_unlocked:
        await credit_service.consume_credits(
            db=db,
            user_id=current_user.id,
            feature_type=FeatureType.SOLAR_RETURN.value,
            resource_id=chart_id,
            description=f"Solar Return {year} for chart {chart.person_name}",
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

**Credit Cost**: 2 credits per year in the range.
Note: Use /solar-return for individual years with unlock tracking.
""",
    responses={
        402: {"description": "Insufficient credits"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_returns(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
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

    # Consume credits for each year in the batch (unless admin)
    if not current_user.is_admin:
        for year in range(start_year, end_year + 1):
            year_unlocked = await credit_service.has_solar_return_year_unlocked(
                db=db,
                user_id=current_user.id,
                chart_id=chart_id,
                year=year,
            )
            if not year_unlocked:
                await credit_service.consume_credits(
                    db=db,
                    user_id=current_user.id,
                    feature_type=FeatureType.SOLAR_RETURN.value,
                    resource_id=chart_id,
                    description=f"Solar Return {year} for chart {chart.person_name}",
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

**Note**: Interpretation is included with Solar Return calculation (no extra credits).
""",
    responses={
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_solar_return_interp(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
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
