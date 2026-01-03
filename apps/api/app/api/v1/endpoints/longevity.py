"""
Longevity analysis endpoints for Hyleg and Alcochoden calculations.

These endpoints provide traditional astrology longevity analysis,
including Hyleg (Giver of Life) and Alcochoden (Giver of Years) calculations.

PREMIUM FEATURE: These endpoints require premium or admin access.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.astro.alcochoden import calculate_alcochoden
from app.astro.hyleg import calculate_hyleg
from app.astro.longevity import calculate_longevity_analysis
from app.core.context import get_locale
from app.core.credit_config import get_feature_cost
from app.core.dependencies import get_current_user, get_db
from app.core.rate_limit import RateLimits, limiter
from app.models.enums import FeatureType
from app.models.user import User
from app.schemas.longevity import AlcochodenResponse, HylegResponse, LongevityResponse
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


def _get_chart_data_for_locale(chart_data: dict | None, locale: str) -> dict | None:
    """Extract language-specific chart data."""
    if not chart_data:
        return None
    return extract_language_data(chart_data, locale)


@router.get(
    "/charts/{chart_id}/hyleg",
    response_model=HylegResponse,
    summary="Calculate Hyleg (Giver of Life)",
    description="""
Calculate the Hyleg (Giver of Life) for a birth chart.

The Hyleg represents the vital force and physical constitution in traditional astrology.
It is determined according to the Ptolemaic method:
- For day charts: Sun is checked first, then Moon
- For night charts: Moon is checked first, then Sun
- Candidate must be in a hylegical place (houses 1, 7, 9, 10, 11)
- Candidate must be aspected by its domicile lord or a prorogatory planet

**Note**: This endpoint is part of the Longevity feature. Use /longevity for the full analysis.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_hyleg(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    method: str = Query(
        "ptolemaic",
        pattern="^(ptolemaic)$",
        description="Calculation method (currently only ptolemaic supported)",
    ),
) -> HylegResponse:
    """Get Hyleg calculation for a chart."""
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
    chart_data = _get_chart_data_for_locale(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Check if longevity data is already calculated
    if "longevity" in chart_data and chart_data["longevity"]:
        hyleg = chart_data["longevity"].get("hyleg")
        if hyleg:
            return HylegResponse(**hyleg)

    # Calculate Hyleg on-the-fly
    planets = chart_data.get("planets", [])
    houses = chart_data.get("houses", [])
    aspects = chart_data.get("aspects", [])
    ascendant = chart_data.get("ascendant", 0)
    arabic_parts = chart_data.get("arabic_parts", [])
    sect = chart_data.get("sect", "diurnal")

    # We need the birth Julian Day - calculate from chart birth data
    from app.services.astro_service import convert_to_julian_day

    birth_jd = convert_to_julian_day(
        chart.birth_datetime,
        chart.birth_timezone,
        chart.latitude,
        chart.longitude,
    )

    hyleg = calculate_hyleg(
        planets=planets,
        houses=houses,
        aspects=aspects,
        ascendant=ascendant,
        arabic_parts=arabic_parts,
        sect=sect,
        birth_jd=birth_jd,
        method=method,
        language=locale,
    )

    if hyleg is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate Hyleg",
        )

    return HylegResponse(**hyleg)


@router.get(
    "/charts/{chart_id}/alcochoden",
    response_model=AlcochodenResponse,
    summary="Calculate Alcochoden (Giver of Years)",
    description="""
Calculate the Alcochoden (Giver of Years) for a birth chart.

The Alcochoden is the planet that determines potential lifespan in traditional astrology.
It works in conjunction with the Hyleg:
- Find the planet with most dignity at the Hyleg's degree
- That planet must also aspect the Hyleg
- The Alcochoden's planetary years indicate potential lifespan
- Modifications are applied based on the Alcochoden's condition

**Note**: This endpoint is part of the Longevity feature. Use /longevity for the full analysis.
""",
    responses={
        403: {"description": "Premium access required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_alcochoden(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AlcochodenResponse:
    """Get Alcochoden calculation for a chart."""
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
    chart_data = _get_chart_data_for_locale(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Check if longevity data is already calculated
    if "longevity" in chart_data and chart_data["longevity"]:
        alcochoden = chart_data["longevity"].get("alcochoden")
        if alcochoden:
            return AlcochodenResponse(**alcochoden)

    # Need to calculate Hyleg first
    planets = chart_data.get("planets", [])
    houses = chart_data.get("houses", [])
    aspects = chart_data.get("aspects", [])
    ascendant = chart_data.get("ascendant", 0)
    arabic_parts = chart_data.get("arabic_parts", [])
    sect = chart_data.get("sect", "diurnal")

    # Get Sun's longitude for combustion check
    sun_longitude = 0
    for planet in planets:
        if planet.get("name") == "Sun":
            sun_longitude = planet.get("longitude", 0)
            break

    # Calculate birth Julian Day
    from app.services.astro_service import convert_to_julian_day

    birth_jd = convert_to_julian_day(
        chart.birth_datetime,
        chart.birth_timezone,
        chart.latitude,
        chart.longitude,
    )

    # Calculate Hyleg first
    hyleg = calculate_hyleg(
        planets=planets,
        houses=houses,
        aspects=aspects,
        ascendant=ascendant,
        arabic_parts=arabic_parts,
        sect=sect,
        birth_jd=birth_jd,
        method="ptolemaic",
        language=locale,
    )

    # Calculate Alcochoden
    alcochoden = calculate_alcochoden(
        hyleg_data=hyleg,
        planets=planets,
        houses=houses,
        aspects=aspects,
        sun_longitude=sun_longitude,
        sect=sect,
        language=locale,
    )

    if alcochoden is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate Alcochoden",
        )

    return AlcochodenResponse(**alcochoden)


@router.get(
    "/charts/{chart_id}/longevity",
    response_model=LongevityResponse,
    summary="Complete longevity analysis (Hyleg + Alcochoden)",
    description="""
Complete longevity analysis combining Hyleg and Alcochoden calculations.

This endpoint provides the full traditional astrology longevity analysis:
- **Hyleg (Giver of Life)**: The vital force significator
- **Alcochoden (Giver of Years)**: The planet determining lifespan
- **Summary**: Overall assessment of vital force and potential years

**Credits Required**: This endpoint requires 3 credits (first calculation only).
If you have already paid for this feature on this chart, no credits will be charged.

**Educational Disclaimer**: These calculations are presented for historical and educational
purposes only. They are not scientifically validated and should never be used for health
predictions or medical decisions.
""",
    responses={
        402: {"description": "Insufficient credits"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_longevity(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
    method: str = Query(
        "ptolemaic",
        pattern="^(ptolemaic)$",
        description="Calculation method (currently only ptolemaic supported)",
    ),
) -> LongevityResponse:
    """Get complete longevity analysis for a chart."""
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
    chart_data = _get_chart_data_for_locale(chart.chart_data, locale)

    if not chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data not available for this locale",
        )

    # Check if longevity data is already calculated (no credits consumed for cached)
    if "longevity" in chart_data and chart_data["longevity"]:
        return LongevityResponse(**chart_data["longevity"])

    # Check if feature is already unlocked (previously paid)
    feature_unlocked = await credit_service.has_feature_unlocked(
        db=db,
        user_id=current_user.id,
        chart_id=chart_id,
        feature_type=FeatureType.LONGEVITY.value,
    )

    # If not unlocked and not admin, check for sufficient credits
    if not feature_unlocked and not current_user.is_admin:
        has_credits, required, available = await credit_service.has_sufficient_credits(
            db=db,
            user_id=current_user.id,
            feature_type=FeatureType.LONGEVITY.value,
        )
        # Unlimited plans have available == -1
        if available != -1 and not has_credits:
            cost = get_feature_cost(FeatureType.LONGEVITY.value)
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "insufficient_credits",
                    "message": f"This feature requires {required} credits. You have {available} credits available.",
                    "feature_type": FeatureType.LONGEVITY.value,
                    "required_credits": required,
                    "available_credits": available,
                    "feature_cost": cost,
                },
            )

    # Calculate on-the-fly
    planets = chart_data.get("planets", [])
    houses = chart_data.get("houses", [])
    aspects = chart_data.get("aspects", [])
    ascendant = chart_data.get("ascendant", 0)
    arabic_parts = chart_data.get("arabic_parts", [])
    sect = chart_data.get("sect", "diurnal")

    # Get Sun's longitude
    sun_longitude = 0
    for planet in planets:
        if planet.get("name") == "Sun":
            sun_longitude = planet.get("longitude", 0)
            break

    # Calculate birth Julian Day
    from app.services.astro_service import convert_to_julian_day

    birth_jd = convert_to_julian_day(
        chart.birth_datetime,
        chart.birth_timezone,
        chart.latitude,
        chart.longitude,
    )

    longevity = calculate_longevity_analysis(
        planets=planets,
        houses=houses,
        aspects=aspects,
        ascendant=ascendant,
        arabic_parts=arabic_parts,
        sect=sect,
        birth_jd=birth_jd,
        sun_longitude=sun_longitude,
        method=method,
        language=locale,
    )

    if longevity is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate longevity analysis",
        )

    # Cache the result in chart_data (flat format for consistency)
    chart.chart_data["longevity"] = longevity
    await db.commit()

    # Consume credits only if not previously unlocked
    if not feature_unlocked:
        await credit_service.consume_credits(
            db=db,
            user_id=current_user.id,
            feature_type=FeatureType.LONGEVITY.value,
            resource_id=chart_id,
            description=f"Longevity analysis for chart {chart.person_name}",
        )

    return LongevityResponse(**longevity)
