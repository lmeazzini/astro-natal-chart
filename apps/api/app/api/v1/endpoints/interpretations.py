"""
Chart interpretation endpoints for AI-generated astrological interpretations.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.astro.dignities import get_sign_ruler
from app.core.config import settings
from app.core.dependencies import get_db, require_verified_email
from app.models.chart import BirthChart
from app.models.interpretation import ChartInterpretation
from app.models.user import User
from app.repositories.interpretation_repository import InterpretationRepository
from app.schemas.interpretation import (
    InterpretationItem,
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
            "content": {
                "application/json": {
                    "example": {"detail": "Chart not found"}
                }
            },
        },
    },
)
async def get_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(require_verified_email)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RAGInterpretationsResponse:
    """
    Get all interpretations for a birth chart using RAG-enhanced AI.

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        RAG-enhanced chart interpretations grouped by type (planets, houses, aspects, arabic_parts)

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
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

        # Use RAG-enhanced interpretation service with caching
        rag_service = InterpretationServiceRAG(db, use_cache=True, use_rag=True)

        # Check if RAG interpretations already exist for this chart
        repo = InterpretationRepository(db)
        existing = await repo.get_by_chart_id(chart_id)
        rag_existing = [i for i in existing if i.prompt_version == RAG_PROMPT_VERSION]

        if rag_existing:
            # Return existing interpretations from database
            logger.info(
                f"Returning {len(rag_existing)} existing RAG interpretations for chart {chart_id}"
            )
            planets_data: dict[str, InterpretationItem] = {}
            houses_data: dict[str, InterpretationItem] = {}
            aspects_data: dict[str, InterpretationItem] = {}
            arabic_parts_data: dict[str, InterpretationItem] = {}

            total_documents = 0
            for interp in rag_existing:
                # Load rag_sources from database
                rag_sources_data = interp.rag_sources or []
                rag_sources_list = [
                    RAGSourceInfo(**src) for src in rag_sources_data
                ]
                total_documents += len(rag_sources_list)

                item = InterpretationItem(
                    content=interp.content,
                    source="rag",
                    rag_sources=rag_sources_list,
                )
                if interp.interpretation_type == "planet":
                    planets_data[interp.subject] = item
                elif interp.interpretation_type == "house":
                    # Convert legacy "House X" format to just "X" for frontend compatibility
                    house_key = interp.subject
                    if house_key.startswith("House "):
                        house_key = house_key.replace("House ", "")
                    houses_data[house_key] = item
                elif interp.interpretation_type == "aspect":
                    aspects_data[interp.subject] = item
                elif interp.interpretation_type == "arabic_part":
                    arabic_parts_data[interp.subject] = item

            return RAGInterpretationsResponse(
                planets=planets_data,
                houses=houses_data,
                aspects=aspects_data,
                arabic_parts=arabic_parts_data,
                source="rag",
                documents_used=total_documents,
            )

        # Generate new interpretations and save to DB
        response = await _generate_rag_interpretations(chart, rag_service, db, save_to_db=True)

        logger.info(
            f"Generated RAG interpretations for chart {chart_id} "
            f"(user: {current_user.email}, documents used: {response.documents_used})"
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
            "content": {
                "application/json": {
                    "example": {"detail": "Chart not found"}
                }
            },
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
        rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)

        # Delete existing interpretations for this chart
        repo = InterpretationRepository(db)
        existing = await repo.get_by_chart_id(chart_id)
        for interp in existing:
            await repo.delete(interp)
        if existing:
            await db.commit()
            logger.info(f"Deleted {len(existing)} existing interpretations for chart {chart_id}")

        # Generate new interpretations and save to DB
        response = await _generate_rag_interpretations(chart, rag_service, db, save_to_db=True)

        logger.info(
            f"Regenerated RAG interpretations for chart {chart_id} "
            f"(user: {current_user.email}, documents used: {response.documents_used})"
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
# RAG Interpretation Helper Function
# ============================================================================


async def _generate_rag_interpretations(
    chart: BirthChart,
    rag_service: InterpretationServiceRAG,
    db: AsyncSession,
    save_to_db: bool = True,
) -> RAGInterpretationsResponse:
    """
    Generate RAG-enhanced interpretations for a birth chart.

    This helper function contains the common logic for generating RAG interpretations,
    used by both get and regenerate endpoints.

    Args:
        chart: The birth chart with chart_data
        rag_service: Configured RAG interpretation service
        db: Database session for saving interpretations
        save_to_db: Whether to save interpretations to the database

    Returns:
        RAGInterpretationsResponse with planets, houses, and aspects interpretations
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
        for planet_data in planets:  # type: PlanetData
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
        planet1_data: PlanetData = next(
            (p for p in planets if p.get("name") == planet1), {}
        )
        planet2_data: PlanetData = next(
            (p for p in planets if p.get("name") == planet2), {}
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

        aspects_data[aspect_key] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
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
                rag_sources=[s.model_dump() for s in rag_sources] if rag_sources else None,
            )
            await repo.create(arabic_part_interpretation)

    # Commit all interpretations to database
    if repo:
        await db.commit()
        logger.info(
            f"Saved {len(planets_data)} planet, {len(houses_data)} house, "
            f"{len(aspects_data)} aspect, and {len(arabic_parts_data)} Arabic Part "
            f"RAG interpretations to database for chart {chart.id}"
        )

    return RAGInterpretationsResponse(
        planets=planets_data,
        houses=houses_data,
        aspects=aspects_data,
        arabic_parts=arabic_parts_data,
        source="rag",
        documents_used=total_documents_used,
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
