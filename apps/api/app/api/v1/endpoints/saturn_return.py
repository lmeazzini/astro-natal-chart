"""
Saturn Return analysis endpoints.

These endpoints provide Saturn Return calculations and interpretations,
including timing of past and future returns, cycle progress, and
astrological interpretations by sign and house.

PREMIUM FEATURE: These endpoints require premium or admin access.
"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.astro.saturn_return import (
    calculate_saturn_return_analysis,
    get_saturn_return_interpretation,
    get_sign_from_longitude,
)
from app.core.context import get_locale
from app.core.dependencies import require_premium
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.saturn_return import (
    SaturnReturnAnalysisSchema,
    SaturnReturnInterpretationSchema,
)
from app.services.astro_service import convert_to_julian_day
from app.services.chart_service import (
    ChartNotFoundError,
    ChartService,
    UnauthorizedAccessError,
    get_chart_service,
)
from app.translations import DEFAULT_LANGUAGE
from app.utils.chart_data_accessor import extract_language_data

router = APIRouter()


def _get_saturn_from_chart_data(chart_data: dict) -> tuple[float, int] | None:
    """
    Extract Saturn's longitude and house from chart data.

    Returns:
        Tuple of (longitude, house) or None if Saturn not found
    """
    planets = chart_data.get("planets", [])
    for planet in planets:
        if planet.get("name") == "Saturn":
            longitude = planet.get("longitude")
            house = planet.get("house", 1)
            if longitude is not None:
                return longitude, house
    return None


@router.get(
    "/charts/{chart_id}/saturn-return",
    response_model=SaturnReturnAnalysisSchema,
    summary="Calculate Saturn Return",
    description="""
Calculate Saturn Return analysis for a birth chart.

Saturn Return occurs approximately every 29.5 years when transiting Saturn
returns to its natal position. This is a significant astrological event
marking major life transitions.

This endpoint calculates:
- Past Saturn Returns with exact dates for all passes
- Current Saturn Return (if one is in progress)
- Next upcoming Saturn Return
- Current cycle progress (percentage through ~29.5 year cycle)
- Days until next return

**Premium Feature**: This endpoint requires premium or admin access.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_saturn_return(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_premium)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
) -> SaturnReturnAnalysisSchema:
    """Get Saturn Return analysis for a chart."""
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

    # Extract Saturn data from chart
    saturn_data = _get_saturn_from_chart_data(chart_data)
    if not saturn_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saturn data not found in chart",
        )

    natal_saturn_longitude, natal_saturn_house = saturn_data

    # Calculate birth Julian Day
    birth_jd = convert_to_julian_day(
        chart.birth_datetime,
        chart.birth_timezone,
        chart.latitude,
        chart.longitude,
    )

    # Calculate Saturn Return analysis
    analysis = calculate_saturn_return_analysis(
        birth_jd=birth_jd,
        natal_saturn_longitude=natal_saturn_longitude,
        natal_saturn_house=natal_saturn_house,
        language=locale,
    )

    return SaturnReturnAnalysisSchema(**analysis)


@router.get(
    "/charts/{chart_id}/saturn-return/interpretation",
    response_model=SaturnReturnInterpretationSchema,
    summary="Get Saturn Return Interpretation",
    description="""
Get astrological interpretation for Saturn Return.

Provides detailed interpretations based on:
- General Saturn Return meaning
- Natal Saturn's zodiac sign (12 variations)
- Natal Saturn's house placement (12 variations)
- Current phase of the return (if applicable)

**Premium Feature**: This endpoint requires premium or admin access.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_saturn_return_interp(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_premium)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
) -> SaturnReturnInterpretationSchema:
    """Get Saturn Return interpretation for a chart."""
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

    # Extract Saturn data from chart
    saturn_data = _get_saturn_from_chart_data(chart_data)
    if not saturn_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Saturn data not found in chart",
        )

    natal_saturn_longitude, natal_saturn_house = saturn_data

    # Calculate birth Julian Day to determine which return we're in
    birth_jd = convert_to_julian_day(
        chart.birth_datetime,
        chart.birth_timezone,
        chart.latitude,
        chart.longitude,
    )

    # Get Saturn Return analysis to determine current phase
    analysis = calculate_saturn_return_analysis(
        birth_jd=birth_jd,
        natal_saturn_longitude=natal_saturn_longitude,
        natal_saturn_house=natal_saturn_house,
        language=locale,
    )

    # Determine return number and phase
    return_number = None
    current_phase = None

    if analysis.get("current_return"):
        current_return = analysis["current_return"]
        return_number = current_return.get("return_number")

        # Determine phase based on passes
        passes = current_return.get("passes", [])
        if passes:
            now = datetime.now(UTC)
            # Check which phase we're in
            for i, p in enumerate(passes):
                pass_date = datetime.fromisoformat(p["date"].replace("Z", "+00:00"))
                if now < pass_date:
                    if i == 0:
                        current_phase = "approaching"
                    break
                elif i == 0:
                    current_phase = "first_pass"
                elif i == 1 and p.get("is_retrograde"):
                    current_phase = "retrograde_pass"
                elif i == len(passes) - 1:
                    current_phase = "final_pass"
    elif analysis.get("next_return"):
        next_return = analysis["next_return"]
        return_number = next_return.get("return_number")
        current_phase = "approaching"

    # Get natal Saturn sign from longitude
    natal_saturn_sign = get_sign_from_longitude(natal_saturn_longitude)

    # Get interpretation
    interpretation = get_saturn_return_interpretation(
        natal_saturn_sign=natal_saturn_sign,
        natal_saturn_house=natal_saturn_house,
        return_number=return_number,
        current_phase=current_phase,
        language=locale,
    )

    return SaturnReturnInterpretationSchema(**interpretation)
