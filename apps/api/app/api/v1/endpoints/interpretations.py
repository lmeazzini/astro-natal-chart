"""
Chart interpretation endpoints for AI-generated astrological interpretations.
"""

import json
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.astro.dignities import get_sign_ruler
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.dependencies import get_db, require_verified_email
from app.core.i18n import SUPPORTED_LOCALES, normalize_locale
from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation
from app.models.user import User
from app.repositories.interpretation_repository import InterpretationRepository
from app.schemas.interpretation import (
    InterpretationItem,
    InterpretationMetadata,
    RAGInterpretationsResponse,
    RAGSourceInfo,
)
from app.services import chart_service
from app.services.interpretation_service_rag import (
    ARABIC_PARTS,
    RAG_MODEL_ID,
    RAG_PROMPT_VERSION,
    InterpretationServiceRAG,
    PlanetData,
)
from app.services.personal_growth_service import GROWTH_PROMPT_VERSION, PersonalGrowthService

router = APIRouter()


@router.get(
    "/charts/{chart_id}/interpretations",
    response_model=RAGInterpretationsResponse,
    summary="Get chart interpretations",
    description="Get all AI-generated interpretations for a birth chart with RAG enhancement. Requires verified email.",
    responses={
        403: {
            "description": "Email not verified or unauthorized access",
            "content": {
                "application/json": {
                    "examples": {
                        "email_not_verified": {
                            "summary": "Email not verified",
                            "value": {
                                "detail": {
                                    "error": "email_not_verified",
                                    "message": "Email verification required to access this feature.",
                                    "user_email": "user@example.com",
                                }
                            },
                        },
                        "unauthorized": {
                            "summary": "Unauthorized access",
                            "value": {"detail": "Not authorized to access this chart"},
                        },
                    }
                }
            },
        },
        404: {
            "description": "Chart not found",
            "content": {"application/json": {"example": {"detail": "Chart not found"}}},
        },
    },
)
async def get_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_verified_email)],
    db: Annotated[AsyncSession, Depends(get_db)],
    regenerate: str | None = None,
    lang: str | None = None,
) -> RAGInterpretationsResponse:
    """
    Get all interpretations for a birth chart using RAG-enhanced AI.

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session
        lang: Optional language code (e.g., 'pt-BR', 'en-US'). If not provided, uses user's profile language.

    Returns:
        RAG-enhanced chart interpretations grouped by type (planets, houses, aspects, arabic_parts)

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
        # Get user's preferred language (use query param if provided, otherwise use profile language)
        user_language = (
            normalize_locale(lang) if lang else (normalize_locale(current_user.locale) or "pt-BR")
        )

        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Parse regenerate parameter for selective regeneration
        regenerate_types = set()
        if regenerate:
            regenerate_types = {t.strip() for t in regenerate.split(",") if t.strip()}
            logger.info(f"Regeneration requested for types: {regenerate_types}")

        # Use RAG-enhanced interpretation service with caching
        rag_service = InterpretationServiceRAG(
            db, use_cache=True, use_rag=True, language=user_language
        )

        # Check if RAG interpretations already exist for this chart in user's language
        repo = InterpretationRepository(db)
        existing = await repo.get_by_chart_id(chart_id)
        rag_existing = [
            i
            for i in existing
            if i.prompt_version == RAG_PROMPT_VERSION
            and getattr(i, "language", "pt-BR") == user_language
        ]

        # Determine which types should use existing data vs regenerate
        # Note: Growth is handled separately below after transaction commit
        use_existing_planets = "planets" not in regenerate_types
        use_existing_houses = "houses" not in regenerate_types
        use_existing_aspects = "aspects" not in regenerate_types
        use_existing_arabic_parts = "arabic_parts" not in regenerate_types

        # Check if we have existing data for each type
        existing_by_type: dict[str, list[ChartInterpretation]] = {
            "planet": [],
            "house": [],
            "aspect": [],
            "arabic_part": [],
        }
        for interp in rag_existing:
            if interp.interpretation_type in existing_by_type:
                existing_by_type[interp.interpretation_type].append(interp)

        planets_data: dict[str, InterpretationItem] = {}
        houses_data: dict[str, InterpretationItem] = {}
        aspects_data: dict[str, InterpretationItem] = {}
        arabic_parts_data: dict[str, InterpretationItem] = {}

        total_documents = 0
        cache_hits_db = 0
        rag_generations = 0

        # Handle planets
        if use_existing_planets and existing_by_type["planet"]:
            logger.info(f"Using existing {len(existing_by_type['planet'])} planet interpretations")
            for interp in existing_by_type["planet"]:
                rag_sources_data = interp.rag_sources or []
                rag_sources_list = [RAGSourceInfo(**src) for src in rag_sources_data]
                total_documents += len(rag_sources_list)
                planets_data[interp.subject] = InterpretationItem(
                    content=interp.content,
                    source="database",
                    rag_sources=rag_sources_list,
                    is_outdated=(interp.prompt_version != RAG_PROMPT_VERSION),
                    cached=False,
                    prompt_version=interp.prompt_version,
                    generated_at=interp.created_at.isoformat() if interp.created_at else None,
                    interpretation_type=interp.interpretation_type,
                    subject=interp.subject,
                    openai_model=interp.openai_model,
                )
            cache_hits_db += len(existing_by_type["planet"])
        else:
            logger.info("Regenerating planet interpretations")
            # Generate planets - will be handled by _generate_rag_interpretations

        # Handle houses
        if use_existing_houses and existing_by_type["house"]:
            logger.info(f"Using existing {len(existing_by_type['house'])} house interpretations")
            for interp in existing_by_type["house"]:
                rag_sources_data = interp.rag_sources or []
                rag_sources_list = [RAGSourceInfo(**src) for src in rag_sources_data]
                total_documents += len(rag_sources_list)
                # Convert legacy "House X" format to just "X" for frontend compatibility
                house_key = interp.subject
                if house_key.startswith("House "):
                    house_key = house_key.replace("House ", "")
                houses_data[house_key] = InterpretationItem(
                    content=interp.content,
                    source="database",
                    rag_sources=rag_sources_list,
                    is_outdated=(interp.prompt_version != RAG_PROMPT_VERSION),
                    cached=False,
                    prompt_version=interp.prompt_version,
                    generated_at=interp.created_at.isoformat() if interp.created_at else None,
                    interpretation_type=interp.interpretation_type,
                    subject=interp.subject,
                    openai_model=interp.openai_model,
                )
            cache_hits_db += len(existing_by_type["house"])
        else:
            logger.info("Regenerating house interpretations")
            # Generate houses - will be handled by _generate_rag_interpretations

        # Handle aspects
        if use_existing_aspects and existing_by_type["aspect"]:
            logger.info(f"Using existing {len(existing_by_type['aspect'])} aspect interpretations")
            for interp in existing_by_type["aspect"]:
                rag_sources_data = interp.rag_sources or []
                rag_sources_list = [RAGSourceInfo(**src) for src in rag_sources_data]
                total_documents += len(rag_sources_list)
                aspects_data[interp.subject] = InterpretationItem(
                    content=interp.content,
                    source="database",
                    rag_sources=rag_sources_list,
                    is_outdated=(interp.prompt_version != RAG_PROMPT_VERSION),
                    cached=False,
                    prompt_version=interp.prompt_version,
                    generated_at=interp.created_at.isoformat() if interp.created_at else None,
                    interpretation_type=interp.interpretation_type,
                    subject=interp.subject,
                    openai_model=interp.openai_model,
                )
            cache_hits_db += len(existing_by_type["aspect"])
        else:
            logger.info("Regenerating aspect interpretations")
            # Generate aspects - will be handled by _generate_rag_interpretations

        # Handle Arabic parts
        if use_existing_arabic_parts and existing_by_type["arabic_part"]:
            logger.info(
                f"Using existing {len(existing_by_type['arabic_part'])} Arabic part interpretations"
            )
            for interp in existing_by_type["arabic_part"]:
                rag_sources_data = interp.rag_sources or []
                rag_sources_list = [RAGSourceInfo(**src) for src in rag_sources_data]
                total_documents += len(rag_sources_list)
                arabic_parts_data[interp.subject] = InterpretationItem(
                    content=interp.content,
                    source="database",
                    rag_sources=rag_sources_list,
                    is_outdated=(interp.prompt_version != RAG_PROMPT_VERSION),
                    cached=False,
                    prompt_version=interp.prompt_version,
                    generated_at=interp.created_at.isoformat() if interp.created_at else None,
                    interpretation_type=interp.interpretation_type,
                    subject=interp.subject,
                    openai_model=interp.openai_model,
                )
            cache_hits_db += len(existing_by_type["arabic_part"])
        else:
            logger.info("Regenerating Arabic part interpretations")
            # Generate Arabic parts - will be handled by _generate_rag_interpretations

        # Check if we need to generate any types
        need_generation = (
            (not use_existing_planets or not existing_by_type["planet"])
            or (not use_existing_houses or not existing_by_type["house"])
            or (not use_existing_aspects or not existing_by_type["aspect"])
            or (not use_existing_arabic_parts or not existing_by_type["arabic_part"])
        )

        if need_generation:
            # Generate missing interpretations
            logger.info("Generating missing interpretation types")
            generated_response = await _generate_rag_interpretations(
                chart, rag_service, db, save_to_db=True, language=user_language
            )

            # Merge generated data with existing data
            if not planets_data:
                planets_data = generated_response.planets
                rag_generations += len(planets_data)
            if not houses_data:
                houses_data = generated_response.houses
                rag_generations += len(houses_data)
            if not aspects_data:
                aspects_data = generated_response.aspects
                rag_generations += len(aspects_data)
            if not arabic_parts_data:
                arabic_parts_data = generated_response.arabic_parts
                rag_generations += len(arabic_parts_data)

            total_documents += generated_response.metadata.documents_used

            logger.info(
                f"Generated {rag_generations} new interpretations for chart {chart_id} "
                f"(user: {current_user.email})"
            )

        # Build metadata
        total_items = (
            len(planets_data) + len(houses_data) + len(aspects_data) + len(arabic_parts_data)
        )
        metadata = InterpretationMetadata(
            total_items=total_items,
            cache_hits_db=cache_hits_db,
            cache_hits_cache=0,
            rag_generations=rag_generations,
            outdated_count=0,
            documents_used=total_documents,
            current_prompt_version=RAG_PROMPT_VERSION,
            response_time_ms=0,
        )

        # Build response (growth will be added later)
        response = RAGInterpretationsResponse(
            planets=planets_data,
            houses=houses_data,
            aspects=aspects_data,
            arabic_parts=arabic_parts_data,
            growth={},  # Will be populated below
            metadata=metadata,
            language=user_language,
        )

        # Commit the main transaction before handling growth suggestions
        # This ensures no session conflicts when creating a new session for growth
        await db.commit()

        # Handle growth suggestions AFTER main transaction is committed
        # This runs for both existing and new interpretations

        # Use a single session for both checking and generating growth
        # This prevents "session is provisioning" errors from concurrent session creation
        async with AsyncSessionLocal() as growth_db:
            if "growth" in regenerate_types:
                # Growth regeneration explicitly requested
                logger.info("Growth regeneration explicitly requested via regenerate parameter")
                needs_generation = True
            else:
                # Check if growth exists in database
                logger.info("Checking for existing growth interpretations in database")
                growth_repo = InterpretationRepository(growth_db)
                existing_growth_dict = await growth_repo.get_growth_interpretations(
                    chart_id=chart_id, language=user_language
                )

                if existing_growth_dict:
                    # All 4 components exist, use them
                    logger.info("Found complete growth interpretations in database")
                    response.growth = _get_existing_growth(existing_growth_dict)
                    response.metadata.cache_hits_db += 4  # 4 components loaded from DB
                    needs_generation = False
                else:
                    # Missing or incomplete, need to generate
                    logger.info("Growth interpretations not found or incomplete, will generate")
                    needs_generation = True

            # Generate if needed (using same session)
            if needs_generation:
                logger.info("Generating growth suggestions via PersonalGrowthService")

                try:
                    growth_service = PersonalGrowthService(language=user_language, db=growth_db)
                    growth_dict = await growth_service.generate_growth_suggestions(
                        chart_data=chart.chart_data,
                        chart_id=chart_id,  # Enable persistence to ChartInterpretation table
                    )
                    # Commit the growth session
                    await growth_db.commit()

                    # Convert growth dict to InterpretationItems and add to response
                    # Map the keys from growth_dict to subject names
                    growth_items = {
                        "points": InterpretationItem(
                            content=json.dumps(growth_dict["growth_points"], ensure_ascii=False),
                            source="rag",
                            rag_sources=[],
                            is_outdated=False,
                            cached=False,
                            prompt_version=GROWTH_PROMPT_VERSION,
                            generated_at=datetime.now(UTC).isoformat(),
                        ),
                        "challenges": InterpretationItem(
                            content=json.dumps(growth_dict["challenges"], ensure_ascii=False),
                            source="rag",
                            rag_sources=[],
                            is_outdated=False,
                            cached=False,
                            prompt_version=GROWTH_PROMPT_VERSION,
                            generated_at=datetime.now(UTC).isoformat(),
                        ),
                        "opportunities": InterpretationItem(
                            content=json.dumps(growth_dict["opportunities"], ensure_ascii=False),
                            source="rag",
                            rag_sources=[],
                            is_outdated=False,
                            cached=False,
                            prompt_version=GROWTH_PROMPT_VERSION,
                            generated_at=datetime.now(UTC).isoformat(),
                        ),
                        "purpose": InterpretationItem(
                            content=json.dumps(growth_dict["purpose"], ensure_ascii=False),
                            source="rag",
                            rag_sources=[],
                            is_outdated=False,
                            cached=False,
                            prompt_version=GROWTH_PROMPT_VERSION,
                            generated_at=datetime.now(UTC).isoformat(),
                        ),
                    }
                    response.growth = growth_items
                    # Update metadata to reflect growth generation (4 components)
                    response.metadata.rag_generations += 4
                    logger.info(f"Growth suggestions generated and saved for chart {chart_id}")
                except Exception as e:
                    logger.error(f"Failed to generate growth suggestions for chart {chart_id}: {e}")
                    # Set growth to empty dict on error - don't let it bubble up to fail the whole request
                    response.growth = {}

        return response

    except chart_service.ChartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except chart_service.UnauthorizedAccessError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., 400 for processing chart)
        raise
    except Exception as e:
        logger.error(f"Error retrieving interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving interpretations",
        ) from e


@router.post(
    "/charts/{chart_id}/interpretations/regenerate",
    response_model=RAGInterpretationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate chart interpretations",
    description="Delete existing interpretations and generate new ones using RAG-enhanced AI. Requires verified email.",
    responses={
        403: {
            "description": "Email not verified or unauthorized access",
            "content": {
                "application/json": {
                    "examples": {
                        "email_not_verified": {
                            "summary": "Email not verified",
                            "value": {
                                "detail": {
                                    "error": "email_not_verified",
                                    "message": "Email verification required to access this feature.",
                                    "user_email": "user@example.com",
                                }
                            },
                        },
                        "unauthorized": {
                            "summary": "Unauthorized access",
                            "value": {"detail": "Not authorized to access this chart"},
                        },
                    }
                }
            },
        },
        404: {
            "description": "Chart not found",
            "content": {"application/json": {"example": {"detail": "Chart not found"}}},
        },
    },
)
async def regenerate_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_verified_email)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RAGInterpretationsResponse:
    """
    Regenerate all RAG-enhanced interpretations for a birth chart.

    This endpoint:
    1. Verifies user owns the chart
    2. Deletes existing interpretations
    3. Generates new RAG-enhanced interpretations using OpenAI
    4. Returns the new interpretations

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Newly generated RAG-enhanced chart interpretations

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
        # Get user's preferred language
        user_language = normalize_locale(current_user.locale) or "pt-BR"

        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Check if chart data is available (not still processing)
        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Use RAG service with cache disabled for regeneration
        rag_service = InterpretationServiceRAG(
            db, use_cache=False, use_rag=True, language=user_language
        )

        # Delete existing interpretations for this chart in user's language
        repo = InterpretationRepository(db)
        existing = await repo.get_by_chart_id(chart_id)
        existing_in_language = [
            i for i in existing if getattr(i, "language", "pt-BR") == user_language
        ]
        for interp in existing_in_language:
            await repo.delete(interp)
        if existing_in_language:
            await db.commit()
            logger.info(
                f"Deleted {len(existing_in_language)} existing interpretations "
                f"for chart {chart_id} in {user_language}"
            )

        # Generate new interpretations and save to DB
        response = await _generate_rag_interpretations(
            chart, rag_service, db, save_to_db=True, language=user_language
        )

        logger.info(
            f"Regenerated RAG interpretations for chart {chart_id} "
            f"(user: {current_user.email}, documents used: {response.metadata.documents_used})"
        )

        return response

    except chart_service.ChartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except chart_service.UnauthorizedAccessError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        ) from e
    except HTTPException:
        # Re-raise HTTP exceptions (e.g., 400 for processing chart)
        raise
    except Exception as e:
        logger.error(f"Error regenerating interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error regenerating interpretations",
        ) from e


# ============================================================================
# Growth Interpretation Helper Function
# ============================================================================


def _get_existing_growth(
    existing_growth: dict[str, ChartInterpretation],
) -> dict[str, InterpretationItem]:
    """
    Convert existing growth interpretations to response format.

    This helper function converts growth interpretations from the database
    (ChartInterpretation objects) into InterpretationItem objects for the API response.

    Returns empty dict if any component is missing (already validated by repo).

    Args:
        existing_growth: Dict of growth interpretations keyed by subject
                        (points, challenges, opportunities, purpose)

    Returns:
        Dict of InterpretationItem objects keyed by subject
        Empty dict if conversion fails or input is empty
    """
    if not existing_growth:
        return {}

    growth_items = {}
    try:
        for subject, interp in existing_growth.items():
            growth_items[subject] = InterpretationItem(
                content=interp.content,  # Already JSON string
                source="database",
                rag_sources=[],
                is_outdated=(interp.prompt_version != GROWTH_PROMPT_VERSION),
                cached=False,
                prompt_version=interp.prompt_version,
                generated_at=interp.created_at.isoformat() if interp.created_at else None,
            )

        logger.info(f"Loaded existing growth with {len(growth_items)} components from database")
        return growth_items

    except Exception as e:
        logger.error(f"Error converting existing growth: {e}")
        return {}  # Treat conversion errors as missing data


# ============================================================================
# RAG Interpretation Helper Function
# ============================================================================


async def _generate_rag_interpretations(
    chart: BirthChart,
    rag_service: InterpretationServiceRAG,
    db: AsyncSession,
    save_to_db: bool = True,
    language: str = "pt-BR",
    generate_all_languages: bool = True,
) -> RAGInterpretationsResponse:
    """
    Generate RAG-enhanced interpretations for a birth chart.

    This helper function contains the common logic for generating RAG interpretations,
    used by both get and regenerate endpoints.

    When generate_all_languages is True (default), it generates interpretations in
    all supported languages (pt-BR and en-US) so users can switch languages without
    waiting for regeneration.

    Args:
        chart: The birth chart with chart_data
        rag_service: Configured RAG interpretation service (used for primary language)
        db: Database session for saving interpretations
        save_to_db: Whether to save interpretations to the database
        language: Primary language for interpretations ('pt-BR' or 'en-US')
        generate_all_languages: If True, also generates in other supported languages

    Returns:
        RAGInterpretationsResponse with planets, houses, and aspects interpretations
        (in the primary language specified)
    """
    planets_data: dict[str, InterpretationItem] = {}
    houses_data: dict[str, InterpretationItem] = {}
    aspects_data: dict[str, InterpretationItem] = {}
    arabic_parts_data: dict[str, InterpretationItem] = {}
    total_documents_used = 0

    # Initialize repository for saving interpretations
    repo = InterpretationRepository(db) if save_to_db else None

    # chart_data is guaranteed to be non-None by the calling endpoints
    chart_data = chart.chart_data
    assert chart_data is not None, "chart_data must not be None"

    planets = chart_data.get("planets", [])
    houses = chart_data.get("houses", [])
    arabic_parts = chart_data.get("arabic_parts", {})

    # Get chart sect for interpretations
    sect = chart_data.get("sect", "diurnal")

    # Process planets
    for planet in planets:
        planet_name = planet.get("name", "")
        if not planet_name:
            continue

        sign = planet.get("sign", "")
        house = planet.get("house", 1)
        retrograde = planet.get("retrograde", False)
        dignities = planet.get("dignities", {})

        # Build search query for RAG context retrieval
        search_query = f"{planet_name} in {sign} house {house}"
        if retrograde:
            search_query += " retrograde"

        # Retrieve context documents
        documents = await rag_service.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Generate interpretation with full signature
        interpretation = await rag_service.generate_planet_interpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            dignities=dignities,
            sect=sect,
            retrograde=retrograde,
        )

        planets_data[planet_name] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
            is_outdated=False,
            cached=False,
            prompt_version=RAG_PROMPT_VERSION,
            generated_at=datetime.now(UTC).isoformat(),
        )

        # Save planet interpretation to database
        if repo:
            planet_interpretation = ChartInterpretation(
                chart_id=chart.id,
                interpretation_type="planet",
                subject=planet_name,
                content=interpretation,
                openai_model=RAG_MODEL_ID,
                prompt_version=RAG_PROMPT_VERSION,
                language=language,
                rag_sources=[s.model_dump() for s in rag_sources] if rag_sources else None,
            )
            await repo.create(planet_interpretation)

    # Process houses
    for house in houses:
        # The house data uses "house" key (not "number") for the house number
        house_number = house.get("house", 0) or house.get("number", 0)
        house_sign = house.get("sign", "")

        if not house_number or not house_sign:
            continue

        # Use just the number as key to match frontend expectations
        house_key = str(house_number)

        # Get ruler (imported at module level)
        ruler = get_sign_ruler(house_sign) or "Unknown"

        # Find ruler's dignities from planet data
        ruler_dignities: dict[str, Any] = {}
        planet_data: PlanetData
        for planet_data in planets:
            if planet_data.get("name") == ruler:
                ruler_dignities = planet_data.get("dignities", {})
                break

        # Build search query for house interpretation
        search_query = f"house {house_number} in {house_sign} ruled by {ruler}"

        # Retrieve context documents
        documents = await rag_service.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Generate house interpretation using the RAG-enhanced method
        house_interpretation = await rag_service.generate_house_interpretation(
            house=house_number,
            sign=house_sign,
            ruler=ruler,
            ruler_dignities=ruler_dignities,
            sect=sect,
        )

        houses_data[house_key] = InterpretationItem(
            content=house_interpretation,
            source="rag",
            rag_sources=rag_sources,
            is_outdated=False,
            cached=False,
            prompt_version=RAG_PROMPT_VERSION,
            generated_at=datetime.now(UTC).isoformat(),
        )

        # Save house interpretation to database
        if repo:
            house_interpretation_record = ChartInterpretation(
                chart_id=chart.id,
                interpretation_type="house",
                subject=house_key,
                content=house_interpretation,
                openai_model=RAG_MODEL_ID,
                prompt_version=RAG_PROMPT_VERSION,
                language=language,
                rag_sources=[s.model_dump() for s in rag_sources] if rag_sources else None,
            )
            await repo.create(house_interpretation_record)

    # Process aspects (limited by RAG_MAX_ASPECTS setting)
    aspects = chart_data.get("aspects", [])
    max_aspects = settings.RAG_MAX_ASPECTS

    for aspect in aspects[:max_aspects]:
        planet1 = aspect.get("planet1", "")
        planet2 = aspect.get("planet2", "")
        aspect_name = aspect.get("aspect", "")
        orb = aspect.get("orb", 0.0)

        if not all([planet1, planet2, aspect_name]):
            continue

        aspect_key = f"{planet1}-{aspect_name}-{planet2}"

        # Build search query
        search_query = f"{planet1} {aspect_name} {planet2}"

        # Retrieve context documents
        documents = await rag_service.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Get signs and dignities for additional context
        planet1_data: PlanetData = next((p for p in planets if p.get("name") == planet1), {})
        planet2_data: PlanetData = next((p for p in planets if p.get("name") == planet2), {})

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

        aspects_data[aspect_key] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
            is_outdated=False,
            cached=False,
            prompt_version=RAG_PROMPT_VERSION,
            generated_at=datetime.now(UTC).isoformat(),
        )

        # Save aspect interpretation to database
        if repo:
            aspect_interpretation = ChartInterpretation(
                chart_id=chart.id,
                interpretation_type="aspect",
                subject=aspect_key,
                content=interpretation,
                openai_model=RAG_MODEL_ID,
                prompt_version=RAG_PROMPT_VERSION,
                language=language,
                rag_sources=[s.model_dump() for s in rag_sources] if rag_sources else None,
            )
            await repo.create(aspect_interpretation)

    # Process Arabic Parts
    for part_key, part_data in arabic_parts.items():
        if part_key not in ARABIC_PARTS:
            continue

        # Build search query
        part_name = ARABIC_PARTS[part_key]["name"]
        part_sign = part_data.get("sign", "")
        part_house = part_data.get("house", 1)
        part_degree = part_data.get("degree", 0.0)

        search_query = f"{part_name} in {part_sign} house {part_house}"

        # Retrieve context documents
        documents = await rag_service.retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        interpretation = await rag_service.generate_arabic_part_interpretation(
            part_key=part_key,
            sign=part_sign,
            house=part_house,
            degree=part_degree,
            sect=sect,
        )

        arabic_parts_data[part_key] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
            is_outdated=False,
            cached=False,
            prompt_version=RAG_PROMPT_VERSION,
            generated_at=datetime.now(UTC).isoformat(),
        )

        # Save Arabic Part interpretation to database
        if repo:
            arabic_part_interpretation = ChartInterpretation(
                chart_id=chart.id,
                interpretation_type="arabic_part",
                subject=part_key,
                content=interpretation,
                openai_model=RAG_MODEL_ID,
                prompt_version=RAG_PROMPT_VERSION,
                language=language,
                rag_sources=[s.model_dump() for s in rag_sources] if rag_sources else None,
            )
            await repo.create(arabic_part_interpretation)

    # Commit all interpretations to database
    if repo:
        await db.commit()
        logger.info(
            f"Saved {len(planets_data)} planet, {len(houses_data)} house, "
            f"{len(aspects_data)} aspect, and {len(arabic_parts_data)} Arabic Part "
            f"RAG interpretations to database for chart {chart.id} ({language})"
        )

    # Generate interpretations in other languages if requested.
    # This runs after primary language is saved, so failures don't affect the main response.
    #
    # PERFORMANCE NOTE: This doubles the OpenAI API calls and response time for first-time
    # generation. The tradeoff is that users can instantly switch languages without waiting.
    # For high-traffic scenarios, consider moving secondary language generation to a Celery
    # background task. Current approach prioritizes UX over response time.
    if save_to_db and generate_all_languages and repo:
        other_languages = [lang for lang in SUPPORTED_LOCALES if lang != language]
        for other_lang in other_languages:
            try:
                # Check if interpretations already exist for this language
                chart_uuid = UUID(str(chart.id))
                existing = await repo.get_by_chart_id(chart_uuid)
                existing_in_lang = [
                    i
                    for i in existing
                    if i.prompt_version == RAG_PROMPT_VERSION
                    and getattr(i, "language", "pt-BR") == other_lang
                ]

                if not existing_in_lang:
                    logger.info(
                        f"Generating additional interpretations in {other_lang} for chart {chart.id}"
                    )
                    # Create a new service instance for the other language
                    other_lang_service = InterpretationServiceRAG(
                        db, use_cache=True, use_rag=True, language=other_lang
                    )
                    # Generate in other language (don't recurse - set generate_all_languages=False)
                    await _generate_rag_interpretations(
                        chart=chart,
                        rag_service=other_lang_service,
                        db=db,
                        save_to_db=True,
                        language=other_lang,
                        generate_all_languages=False,  # Prevent infinite recursion
                    )
            except Exception as e:
                # Log error but don't fail the main request - secondary language can be generated later
                logger.warning(
                    f"Failed to generate interpretations in {other_lang} for chart {chart.id}: {e}. "
                    "User can regenerate later by switching language."
                )

    return RAGInterpretationsResponse(
        planets=planets_data,
        houses=houses_data,
        aspects=aspects_data,
        arabic_parts=arabic_parts_data,
        growth={},  # Growth not generated in this path
        metadata=InterpretationMetadata(
            total_items=(
                len(planets_data) + len(houses_data) + len(aspects_data) + len(arabic_parts_data)
            ),
            cache_hits_db=0,
            cache_hits_cache=0,
            rag_generations=(
                len(planets_data) + len(houses_data) + len(aspects_data) + len(arabic_parts_data)
            ),
            outdated_count=0,
            documents_used=total_documents_used,
            current_prompt_version=RAG_PROMPT_VERSION,
            response_time_ms=0,
        ),
        language=language,
    )


def _format_rag_sources(documents: list[dict[str, Any]]) -> list[RAGSourceInfo]:
    """Format RAG documents into RAGSourceInfo objects."""
    sources = []
    for doc in documents:
        payload = doc.get("payload", {})
        metadata = payload.get("metadata", {})

        sources.append(
            RAGSourceInfo(
                source=metadata.get("source", payload.get("title", "Unknown")),
                page=str(metadata.get("page", "")) if metadata.get("page") else None,
                relevance_score=doc.get("score", doc.get("hybrid_score", 0.0)),
                content_preview=payload.get("content", "")[:200] + "..."
                if len(payload.get("content", "")) > 200
                else payload.get("content", ""),
            )
        )

    return sources
