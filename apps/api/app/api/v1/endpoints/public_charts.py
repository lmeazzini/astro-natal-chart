"""
Public Charts API endpoints.

Provides public access to famous people's natal charts for evaluating RAG interpretations.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.core.i18n import SUPPORTED_LOCALES, normalize_locale
from app.core.rate_limit import RateLimits, limiter
from app.models.public_chart import PublicChart
from app.models.public_chart_interpretation import PublicChartInterpretation
from app.models.user import User
from app.schemas.interpretation import ChartInterpretationsResponse
from app.schemas.public_chart import (
    PUBLIC_CHART_CATEGORIES,
    PublicChartCreate,
    PublicChartDetail,
    PublicChartList,
    PublicChartPreview,
    PublicChartUpdate,
)
from app.services.interpretation_service_rag import ARABIC_PARTS, InterpretationServiceRAG
from app.services.public_chart_service import PublicChartService

router = APIRouter(prefix="/public-charts", tags=["public-charts"])


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================


@router.get(
    "",
    response_model=PublicChartList,
    summary="List public charts",
    description="Get a paginated list of public charts with optional filters. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def list_public_charts(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Annotated[str | None, Query(description="Filter by category")] = None,
    search: Annotated[str | None, Query(description="Search by name")] = None,
    sort: Annotated[
        str,
        Query(description="Sort order: name, date, views"),
    ] = "name",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=50, description="Items per page")] = 20,
) -> PublicChartList:
    """
    List all published public charts.

    - **category**: Filter by category (scientist, artist, leader, etc.)
    - **search**: Search term for name
    - **sort**: Sort order (name, date, views)
    - **page**: Page number (1-based)
    - **page_size**: Number of items per page (max 50)
    """
    service = PublicChartService(db)
    return await service.list_charts(
        category=category,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/featured",
    response_model=list[PublicChartPreview],
    summary="Get featured charts",
    description="Get a list of featured public charts. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_featured_charts(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=20, description="Maximum number of charts")] = 10,
) -> list[PublicChartPreview]:
    """Get featured public charts for homepage display."""
    service = PublicChartService(db)
    return await service.get_featured_charts(limit=limit)


@router.get(
    "/categories",
    response_model=list[dict],
    summary="Get categories with counts",
    description="Get all categories with chart counts. No authentication required.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def get_categories(
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[dict]:
    """Get all available categories with chart counts."""
    service = PublicChartService(db)
    categories = await service.get_categories_with_counts()

    # Add all possible categories even if empty
    existing = {c["category"] for c in categories}
    for cat in PUBLIC_CHART_CATEGORIES:
        if cat not in existing:
            categories.append({"category": cat, "count": 0})

    return sorted(categories, key=lambda x: x["count"], reverse=True)


@router.get(
    "/{slug}",
    response_model=PublicChartDetail,
    summary="Get public chart by slug",
    description="Get full details of a public chart including chart data. No authentication required.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_public_chart(
    request: Request,
    response: Response,
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PublicChartDetail:
    """
    Get a public chart by its slug.

    - **slug**: URL-friendly identifier (e.g., 'albert-einstein')

    Returns full chart details including calculated chart data and interpretations.
    Increments view count on each access.
    """
    service = PublicChartService(db)
    chart = await service.get_chart_detail(slug)

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Public chart '{slug}' not found",
        )

    return chart


@router.get(
    "/{slug}/interpretations",
    response_model=ChartInterpretationsResponse,
    summary="Get public chart interpretations",
    description="Get all AI-generated interpretations for a public chart. No authentication required.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_public_chart_interpretations(
    request: Request,
    response: Response,
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    lang: Annotated[str | None, Query(description="Language: 'pt-BR' or 'en-US'")] = None,
) -> ChartInterpretationsResponse:
    """
    Get all interpretations for a public chart by its slug.

    - **slug**: URL-friendly identifier (e.g., 'albert-einstein')
    - **lang**: Language for interpretations (default: 'pt-BR')

    Returns interpretations for planets, houses, aspects, and Arabic parts.
    If interpretations don't exist in the requested language, they will be generated using RAG-enhanced AI.
    """
    # Normalize language parameter
    language = normalize_locale(lang) if lang else "pt-BR"

    # Get the public chart
    service = PublicChartService(db)
    chart = await service.get_chart_by_slug(slug)

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Public chart '{slug}' not found",
        )

    if not chart.chart_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chart data is not available yet.",
        )

    # Check for existing interpretations in the requested language
    stmt = select(PublicChartInterpretation).where(
        PublicChartInterpretation.chart_id == chart.id,
        PublicChartInterpretation.language == language,
    )
    result = await db.execute(stmt)
    existing = result.scalars().all()

    if existing:
        # Return existing interpretations
        planets: dict[str, str] = {}
        houses: dict[str, str] = {}
        aspects: dict[str, str] = {}
        arabic_parts: dict[str, str] = {}

        for interp in existing:
            if interp.interpretation_type == "planet":
                planets[interp.subject] = interp.content
            elif interp.interpretation_type == "house":
                houses[interp.subject] = interp.content
            elif interp.interpretation_type == "aspect":
                aspects[interp.subject] = interp.content
            elif interp.interpretation_type == "arabic_part":
                arabic_parts[interp.subject] = interp.content

        logger.info(
            f"Returning {len(existing)} existing interpretations for public chart {slug} ({language})"
        )

        return ChartInterpretationsResponse(
            planets=planets,
            houses=houses,
            aspects=aspects,
            arabic_parts=arabic_parts,
            source="rag",
            language=language,
        )

    # Generate new interpretations
    try:
        interpretations = await _generate_public_chart_interpretations(
            chart=chart,
            db=db,
            language=language,
        )
        logger.info(f"Generated new interpretations for public chart {slug} ({language})")
        return interpretations
    except Exception as e:
        logger.error(f"Error generating interpretations for public chart {slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating interpretations",
        ) from e


async def _generate_public_chart_interpretations(
    chart: PublicChart,
    db: AsyncSession,
    language: str = "pt-BR",
    generate_all_languages: bool = True,
) -> ChartInterpretationsResponse:
    """
    Generate RAG-enhanced interpretations for a public chart.

    This helper function generates interpretations and saves them to the database.
    When generate_all_languages is True (default), it generates interpretations in
    all supported languages (pt-BR and en-US).

    Args:
        chart: The public chart with chart_data
        db: Database session
        language: Primary language for the returned response
        generate_all_languages: If True, also generates in other supported languages
    """
    planets: dict[str, str] = {}
    houses: dict[str, str] = {}
    aspects: dict[str, str] = {}
    arabic_parts: dict[str, str] = {}

    # Initialize RAG service with language
    rag_service = InterpretationServiceRAG(db, use_cache=True, use_rag=True, language=language)

    chart_data = chart.chart_data
    assert chart_data is not None, "chart_data must not be None"

    planets_data = chart_data.get("planets", [])
    houses_data = chart_data.get("houses", [])
    arabic_parts_data = chart_data.get("arabic_parts", {})
    sect = chart_data.get("sect", "diurnal")

    # Process planets
    for planet in planets_data:
        planet_name = planet.get("name", "")
        if not planet_name:
            continue

        sign = planet.get("sign", "")
        house = planet.get("house", 1)
        retrograde = planet.get("retrograde", False)
        dignities = planet.get("dignities", {})

        interpretation = await rag_service.generate_planet_interpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            dignities=dignities,
            sect=sect,
            retrograde=retrograde,
        )

        planets[planet_name] = interpretation

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="planet",
            subject=planet_name,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)

    # Process houses
    for house in houses_data:
        house_number = house.get("house", 0) or house.get("number", 0)
        house_sign = house.get("sign", "")

        if not house_number or not house_sign:
            continue

        house_key = str(house_number)

        from app.astro.dignities import get_sign_ruler

        ruler = get_sign_ruler(house_sign) or "Unknown"

        ruler_dignities: dict[str, Any] = {}
        for planet_data in planets_data:
            if planet_data.get("name") == ruler:
                ruler_dignities = planet_data.get("dignities", {})
                break

        interpretation = await rag_service.generate_house_interpretation(
            house=house_number,
            sign=house_sign,
            ruler=ruler,
            ruler_dignities=ruler_dignities,
            sect=sect,
        )

        houses[house_key] = interpretation

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="house",
            subject=house_key,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)

    # Process aspects (limited by settings)
    aspects_list = chart_data.get("aspects", [])
    max_aspects = settings.RAG_MAX_ASPECTS

    for aspect in aspects_list[:max_aspects]:
        planet1 = aspect.get("planet1", "")
        planet2 = aspect.get("planet2", "")
        aspect_name = aspect.get("aspect", "")
        orb = aspect.get("orb", 0.0)

        if not all([planet1, planet2, aspect_name]):
            continue

        aspect_key = f"{planet1}-{aspect_name}-{planet2}"

        planet1_data: dict[str, Any] = next(
            (p for p in planets_data if p.get("name") == planet1), {}
        )
        planet2_data: dict[str, Any] = next(
            (p for p in planets_data if p.get("name") == planet2), {}
        )

        sign1 = planet1_data.get("sign", "")
        sign2 = planet2_data.get("sign", "")
        dignities1 = planet1_data.get("dignities", {})
        dignities2 = planet2_data.get("dignities", {})
        applying = aspect.get("applying", False)

        interpretation = await rag_service.generate_aspect_interpretation(
            planet1=planet1,
            planet2=planet2,
            aspect=aspect_name,
            sign1=sign1,
            sign2=sign2,
            orb=orb,
            applying=applying,
            sect=sect,
            dignities1=dignities1,
            dignities2=dignities2,
        )

        aspects[aspect_key] = interpretation

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="aspect",
            subject=aspect_key,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)

    # Process Arabic Parts
    for part_key, part_data in arabic_parts_data.items():
        if part_key not in ARABIC_PARTS:
            continue

        part_sign = part_data.get("sign", "")
        part_house = part_data.get("house", 1)
        part_degree = part_data.get("degree", 0.0)

        interpretation = await rag_service.generate_arabic_part_interpretation(
            part_key=part_key,
            sign=part_sign,
            house=part_house,
            degree=part_degree,
            sect=sect,
        )

        arabic_parts[part_key] = interpretation

        # Save to database
        interp_record = PublicChartInterpretation(
            chart_id=chart.id,
            interpretation_type="arabic_part",
            subject=part_key,
            content=interpretation,
            openai_model="gpt-4o-mini-rag",
            prompt_version="rag-v1",
            language=language,
        )
        db.add(interp_record)

    # Commit all interpretations
    await db.commit()

    logger.info(
        f"Saved {len(planets)} planet, {len(houses)} house, "
        f"{len(aspects)} aspect, and {len(arabic_parts)} Arabic Part "
        f"interpretations for public chart {chart.id} ({language})"
    )

    # Generate interpretations in other languages if requested.
    # This runs after primary language is saved, so failures don't affect the main response.
    #
    # PERFORMANCE NOTE: This doubles the OpenAI API calls and response time for first-time
    # generation. The tradeoff is that users can instantly switch languages without waiting.
    # For high-traffic scenarios, consider moving secondary language generation to a Celery
    # background task. Current approach prioritizes UX over response time.
    if generate_all_languages:
        other_languages = [lang for lang in SUPPORTED_LOCALES if lang != language]
        for other_lang in other_languages:
            try:
                # Check if interpretations already exist for this language
                existing_query = select(PublicChartInterpretation).where(
                    PublicChartInterpretation.chart_id == chart.id,
                    PublicChartInterpretation.language == other_lang,
                )
                result = await db.execute(existing_query)
                existing_in_lang = result.scalars().all()

                if not existing_in_lang:
                    logger.info(
                        f"Generating additional interpretations in {other_lang} "
                        f"for public chart {chart.id}"
                    )
                    # Generate in other language (don't recurse)
                    await _generate_public_chart_interpretations(
                        chart=chart,
                        db=db,
                        language=other_lang,
                        generate_all_languages=False,  # Prevent infinite recursion
                    )
            except Exception as e:
                # Log error but don't fail the main request - secondary language can be generated later
                logger.warning(
                    f"Failed to generate interpretations in {other_lang} for public chart {chart.id}: {e}. "
                    "Will be generated on next request in that language."
                )

    return ChartInterpretationsResponse(
        planets=planets,
        houses=houses,
        aspects=aspects,
        arabic_parts=arabic_parts,
        source="rag",
        language=language,
    )


# ============================================================================
# ADMIN ENDPOINTS (Require admin role)
# ============================================================================

admin_router = APIRouter(prefix="/admin/public-charts", tags=["admin-public-charts"])


@admin_router.get(
    "",
    response_model=PublicChartList,
    summary="List all public charts (admin)",
    description="Admin view of all public charts including unpublished ones.",
)
async def list_public_charts_admin(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    include_unpublished: Annotated[bool, Query(description="Include unpublished")] = True,
) -> PublicChartList:
    """Admin endpoint to list all public charts."""
    service = PublicChartService(db)
    return await service.list_charts_admin(
        page=page,
        page_size=page_size,
        include_unpublished=include_unpublished,
    )


@admin_router.post(
    "",
    response_model=PublicChartDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create public chart (admin)",
    description="Create a new public chart. Calculates chart data automatically.",
)
async def create_public_chart(
    data: PublicChartCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """
    Create a new public chart.

    Chart data will be calculated automatically based on birth information.
    """
    service = PublicChartService(db)

    try:
        chart = await service.create_chart(data)
        return PublicChartDetail.model_validate(chart)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@admin_router.get(
    "/{chart_id}",
    response_model=PublicChartDetail,
    summary="Get public chart by ID (admin)",
    description="Get any public chart by ID, including unpublished ones.",
)
async def get_public_chart_admin(
    chart_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """Admin endpoint to get any chart by ID."""
    service = PublicChartService(db)
    chart = await service.get_chart_by_id(chart_id)

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )

    return PublicChartDetail.model_validate(chart)


@admin_router.put(
    "/{chart_id}",
    response_model=PublicChartDetail,
    summary="Update public chart (admin)",
    description="Update a public chart. Recalculates chart data if birth info changes.",
)
async def update_public_chart(
    chart_id: UUID,
    data: PublicChartUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> PublicChartDetail:
    """
    Update a public chart.

    If birth data changes, chart will be recalculated automatically.
    """
    service = PublicChartService(db)

    try:
        chart = await service.update_chart(chart_id, data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    if not chart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )

    return PublicChartDetail.model_validate(chart)


@admin_router.delete(
    "/{chart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete public chart (admin)",
    description="Permanently delete a public chart.",
)
async def delete_public_chart(
    chart_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    admin_user: Annotated[User, Depends(require_admin)],
) -> None:
    """Delete a public chart permanently."""
    service = PublicChartService(db)
    deleted = await service.delete_chart(chart_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public chart not found",
        )
