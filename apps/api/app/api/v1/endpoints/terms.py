"""
Planetary Terms (Bounds) API endpoints.

Terms divide each zodiac sign into 5 unequal segments, each ruled by one of
the five non-luminary planets (Saturn, Jupiter, Mars, Venus, Mercury).

This module provides endpoints for:
- Getting term rulers for all planets in a chart
- Looking up term ruler for any degree
- Getting the complete terms reference table

IMPORTANT: These endpoints are NOT premium-gated. Terms are a reference feature
available to all authenticated users.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from app.astro.terms import (
    TermSystem,
    get_all_term_rulers,
    get_term_ruler,
    get_terms_table,
)
from app.core.dependencies import get_current_user
from app.core.rate_limit import RateLimits, limiter
from app.models.user import User
from app.schemas.terms import (
    ChartTermsResponse,
    PlanetTermInfo,
    TermEntry,
    TermRulerResponse,
    TermsSummary,
    TermsTableResponse,
    TermSystemEnum,
)
from app.services.chart_service import (
    ChartNotFoundError,
    ChartService,
    UnauthorizedAccessError,
    get_chart_service,
)

router = APIRouter(tags=["terms"])


@router.get(
    "/charts/{chart_id}/terms",
    response_model=ChartTermsResponse,
    summary="Get term rulers for all planets in a chart",
    description="""
Get the term (bound) rulers for all planets in a birth chart.

Terms are one of the 5 essential dignities in traditional astrology.
Each zodiac sign is divided into 5 unequal segments, each ruled by
one of the classical planets (Saturn, Jupiter, Mars, Venus, Mercury).

A planet in its own term receives +2 dignity points.

**Available Term Systems:**
- `egyptian` - Most widely used in Hellenistic astrology (default)
- `ptolemaic` - Ptolemy's refined system from Tetrabiblos
- `chaldean` - Regular 8-7-6-5-4 degree pattern
- `dorothean` - From Dorotheus of Sidon
""",
    responses={
        401: {"description": "Authentication required"},
        404: {"description": "Chart not found or not owned by user"},
    },
)
@limiter.limit(RateLimits.CHART_READ)
async def get_chart_terms(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    chart_service: Annotated[ChartService, Depends(get_chart_service)],
    system: TermSystemEnum = Query(
        TermSystemEnum.EGYPTIAN,
        description="Term system to use",
    ),
) -> ChartTermsResponse:
    """Get term rulers for all planets in a chart."""
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

    # Get planets from chart data
    planets = chart.chart_data.get("planets", [])
    if not planets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart has no planet data",
        )

    # Convert schema enum to astro module enum
    term_system = TermSystem(system.value)

    # Calculate terms for all planets
    result = get_all_term_rulers(planets, term_system)

    # Convert to response model
    return ChartTermsResponse(
        system=system,
        planets=[PlanetTermInfo(**p) for p in result["planets"]],
        summary=TermsSummary(**result["summary"]),
    )


@router.get(
    "/dignities/term",
    response_model=TermRulerResponse,
    summary="Look up term ruler for any degree",
    description="""
Look up which planet rules the term (bound) for any ecliptic longitude.

This is a reference endpoint for looking up term rulers without needing a chart.

**Parameters:**
- `longitude` - Ecliptic longitude in degrees (0-359.999...)
- `system` - Term system to use (egyptian, ptolemaic, chaldean, dorothean)

**Example:**
- 0° Aries (longitude=0): Jupiter (Egyptian)
- 15° Taurus (longitude=45): Jupiter (Egyptian)
- 0° Cancer (longitude=90): Mars (Egyptian)
""",
    responses={
        400: {"description": "Invalid longitude value"},
    },
)
@limiter.limit(RateLimits.CHART_LIST)
async def lookup_term_ruler(
    request: Request,
    response: Response,
    longitude: float = Query(
        ...,
        ge=0,
        lt=360,
        description="Ecliptic longitude in degrees (0-359.999...)",
    ),
    system: TermSystemEnum = Query(
        TermSystemEnum.EGYPTIAN,
        description="Term system to use",
    ),
) -> TermRulerResponse:
    """Look up term ruler for any degree."""
    # Convert schema enum to astro module enum
    term_system = TermSystem(system.value)

    try:
        result = get_term_ruler(longitude, term_system)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err

    return TermRulerResponse(
        longitude=result["longitude"],
        sign=result["sign"],
        degree_in_sign=result["degree_in_sign"],
        term_ruler=result["term_ruler"],
        term_start=result["term_start"],
        term_end=result["term_end"],
        term_system=system,
    )


@router.get(
    "/dignities/terms/table",
    response_model=TermsTableResponse,
    summary="Get complete terms reference table",
    description="""
Get the complete terms (bounds) table for a specific system.

Returns the full reference table showing which planet rules each term
in all 12 zodiac signs.

**Available Term Systems:**
- `egyptian` - Most widely used in Hellenistic astrology
- `ptolemaic` - Ptolemy's refined system from Tetrabiblos
- `chaldean` - Regular 8-7-6-5-4 degree pattern
- `dorothean` - From Dorotheus of Sidon
""",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_terms_reference_table(
    request: Request,
    response: Response,
    system: TermSystemEnum = Query(
        TermSystemEnum.EGYPTIAN,
        description="Term system to use",
    ),
) -> TermsTableResponse:
    """Get complete terms reference table."""
    # Convert schema enum to astro module enum
    term_system = TermSystem(system.value)

    result = get_terms_table(term_system)

    # Convert to response model
    signs_output = {}
    for sign, terms in result["signs"].items():
        signs_output[sign] = [TermEntry(**t) for t in terms]

    return TermsTableResponse(
        system=system,
        signs=signs_output,
    )
