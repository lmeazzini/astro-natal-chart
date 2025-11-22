"""
Chart interpretation endpoints for AI-generated astrological interpretations.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db, require_admin
from app.core.rate_limit import RateLimits, limiter
from app.models.chart import BirthChart
from app.models.user import User
from app.schemas.interpretation import (
    ChartInterpretationsResponse,
    InterpretationItem,
    RAGInterpretationsResponse,
    RAGSourceInfo,
)
from app.services import chart_service
from app.services.interpretation_service import InterpretationService
from app.services.interpretation_service_rag import InterpretationServiceRAG

router = APIRouter()


@router.get(
    "/charts/{chart_id}/interpretations",
    response_model=ChartInterpretationsResponse,
    summary="Get chart interpretations",
    description="Get all AI-generated interpretations for a birth chart (classical 7 planets only).",
)
async def get_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartInterpretationsResponse:
    """
    Get all interpretations for a birth chart.

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chart interpretations grouped by type (planets, houses, aspects)

    Raises:
        HTTPException: If chart not found or user unauthorized
    """
    try:
        # Verify user owns the chart
        await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Get interpretations
        interpretation_service = InterpretationService(db)
        interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

        return ChartInterpretationsResponse(**interpretations)

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
    except Exception as e:
        logger.error(f"Error retrieving interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving interpretations",
        ) from e


@router.post(
    "/charts/{chart_id}/interpretations/regenerate",
    response_model=ChartInterpretationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate chart interpretations",
    description="Delete existing interpretations and generate new ones using OpenAI.",
)
async def regenerate_chart_interpretations(
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartInterpretationsResponse:
    """
    Regenerate all interpretations for a birth chart.

    This endpoint:
    1. Verifies user owns the chart
    2. Deletes existing interpretations
    3. Generates new interpretations using OpenAI
    4. Returns the new interpretations

    Args:
        chart_id: Chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Newly generated chart interpretations

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

        interpretation_service = InterpretationService(db)

        # Check if chart data is available (not still processing)
        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Delete existing interpretations
        deleted_count = await interpretation_service.repository.delete_by_chart_id(chart_id)
        logger.info(f"Deleted {deleted_count} existing interpretations for chart {chart_id}")

        # Generate new interpretations
        await interpretation_service.generate_all_interpretations(
            chart_id=chart_id,
            chart_data=chart.chart_data,
        )

        # Get and return new interpretations
        interpretations = await interpretation_service.get_interpretations_by_chart(chart_id)

        return ChartInterpretationsResponse(**interpretations)

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
    except Exception as e:
        logger.error(f"Error regenerating interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error regenerating interpretations",
        ) from e


# ============================================================================
# RAG Interpretation Endpoints (Admin Only - A/B Testing)
# ============================================================================


async def _generate_rag_interpretations(
    chart: BirthChart,
    rag_service: InterpretationServiceRAG,
) -> RAGInterpretationsResponse:
    """
    Generate RAG-enhanced interpretations for a birth chart.

    This helper function contains the common logic for generating RAG interpretations,
    used by both get and regenerate endpoints.

    Args:
        chart: The birth chart with chart_data
        rag_service: Configured RAG interpretation service

    Returns:
        RAGInterpretationsResponse with planets, houses, and aspects interpretations
    """
    planets_data: dict[str, InterpretationItem] = {}
    houses_data: dict[str, InterpretationItem] = {}
    aspects_data: dict[str, InterpretationItem] = {}
    total_documents_used = 0

    # chart_data is guaranteed to be non-None by the calling endpoints
    chart_data = chart.chart_data
    assert chart_data is not None, "chart_data must not be None"

    planets = chart_data.get("planets", [])
    houses = chart_data.get("houses", [])

    # Process planets
    for planet in planets:
        planet_name = planet.get("name", "")
        if not planet_name:
            continue

        sign = planet.get("sign", "")
        house = planet.get("house", 1)
        retrograde = planet.get("retrograde", False)

        # Build search query for RAG context retrieval
        search_query = f"{planet_name} in {sign} house {house}"
        if retrograde:
            search_query += " retrograde"

        # Retrieve context documents
        documents = await rag_service._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Generate interpretation
        interpretation = await rag_service.generate_planet_interpretation(
            planet=planet_name,
            sign=sign,
            house=house,
            retrograde=retrograde,
        )

        planets_data[planet_name] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
        )

    # Process houses
    for house in houses:
        house_number = house.get("number", 0)
        house_sign = house.get("sign", "")

        if not house_number or not house_sign:
            continue

        house_key = f"House {house_number}"

        # Build search query for house interpretation
        search_query = f"house {house_number} in {house_sign}"

        # Retrieve context documents
        documents = await rag_service._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Generate house interpretation using the context
        # Note: Houses use a simpler interpretation since there's no dedicated method
        context = await rag_service._format_rag_context(documents)
        house_interpretation = (
            f"House {house_number} ({house_sign}): "
            f"This house governs specific life areas as indicated by its position in {house_sign}."
        )
        if context:
            house_interpretation = context[:500] if len(context) > 500 else context

        houses_data[house_key] = InterpretationItem(
            content=house_interpretation,
            source="rag",
            rag_sources=rag_sources,
        )

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
        documents = await rag_service._retrieve_context(
            query=search_query,
            filters={"document_type": ["text", "pdf", "interpretation"]},
        )

        rag_sources = _format_rag_sources(documents)
        total_documents_used += len(documents)

        # Get signs for additional context
        planet1_sign = next(
            (p.get("sign") for p in planets if p.get("name") == planet1), None
        )
        planet2_sign = next(
            (p.get("sign") for p in planets if p.get("name") == planet2), None
        )

        interpretation = await rag_service.generate_aspect_interpretation(
            planet1=planet1,
            planet2=planet2,
            aspect=aspect_name,
            orb=orb,
            planet1_sign=planet1_sign,
            planet2_sign=planet2_sign,
        )

        aspects_data[aspect_key] = InterpretationItem(
            content=interpretation,
            source="rag",
            rag_sources=rag_sources,
        )

    return RAGInterpretationsResponse(
        planets=planets_data,
        houses=houses_data,
        aspects=aspects_data,
        source="rag",
        documents_used=total_documents_used,
    )


@router.get(
    "/charts/{chart_id}/interpretations/rag",
    response_model=RAGInterpretationsResponse,
    summary="Get RAG-enhanced interpretations (Admin Only)",
    description=(
        "Get AI-generated interpretations enhanced with RAG (Retrieval-Augmented "
        "Generation) for A/B testing. Only available to admin users."
    ),
    tags=["RAG", "Admin"],
)
@limiter.limit(RateLimits.RAG_SEARCH)
async def get_chart_interpretations_rag(
    chart_id: UUID,
    request: Request,
    admin_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RAGInterpretationsResponse:
    """
    Get RAG-enhanced interpretations for a birth chart.

    This endpoint is only available to admin users for A/B testing purposes.
    It returns interpretations generated using RAG (Retrieval-Augmented Generation),
    which retrieves relevant astrological knowledge from the vector database
    before generating interpretations.

    Args:
        chart_id: Chart UUID
        request: FastAPI request object (for rate limiting)
        admin_user: Current admin user (enforced by require_admin dependency)
        db: Database session

    Returns:
        RAG-enhanced chart interpretations with source information

    Raises:
        HTTPException: If chart not found, user unauthorized, or not admin
    """
    try:
        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(admin_user.id)),
        )

        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Use RAG-enhanced interpretation service with caching
        rag_service = InterpretationServiceRAG(db, use_cache=True, use_rag=True)

        # Generate interpretations using common helper
        response = await _generate_rag_interpretations(chart, rag_service)

        logger.info(
            f"Generated RAG interpretations for chart {chart_id} "
            f"(admin: {admin_user.email}, documents used: {response.documents_used})"
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
        logger.error(f"Error generating RAG interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating RAG interpretations",
        ) from e


@router.post(
    "/charts/{chart_id}/interpretations/rag/regenerate",
    response_model=RAGInterpretationsResponse,
    status_code=status.HTTP_200_OK,
    summary="Regenerate RAG interpretations (Admin Only)",
    description="Force regenerate RAG-enhanced interpretations. Only available to admin users.",
    tags=["RAG", "Admin"],
)
@limiter.limit(RateLimits.RAG_SEARCH)
async def regenerate_chart_interpretations_rag(
    chart_id: UUID,
    request: Request,
    admin_user: Annotated[User, Depends(require_admin)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RAGInterpretationsResponse:
    """
    Regenerate RAG-enhanced interpretations for a birth chart.

    This endpoint forces regeneration of RAG interpretations by bypassing cache.
    Only available to admin users for A/B testing purposes.

    Args:
        chart_id: Chart UUID
        request: FastAPI request object (for rate limiting)
        admin_user: Current admin user (enforced by require_admin dependency)
        db: Database session

    Returns:
        Newly generated RAG-enhanced chart interpretations

    Raises:
        HTTPException: If chart not found, user unauthorized, or not admin
    """
    try:
        # Verify user owns the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(admin_user.id)),
        )

        if not chart.chart_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart is still processing. Please wait until calculations are complete.",
            )

        # Use RAG service with cache disabled for regeneration
        rag_service = InterpretationServiceRAG(db, use_cache=False, use_rag=True)

        # Generate interpretations using common helper
        response = await _generate_rag_interpretations(chart, rag_service)

        logger.info(
            f"Regenerated RAG interpretations for chart {chart_id} "
            f"(admin: {admin_user.email}, documents used: {response.documents_used})"
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
        logger.error(f"Error regenerating RAG interpretations for chart {chart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error regenerating RAG interpretations",
        ) from e


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
