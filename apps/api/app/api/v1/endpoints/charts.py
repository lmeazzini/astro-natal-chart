"""
Birth chart endpoints for creating and managing natal charts.
"""

import re
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from loguru import logger
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.context import get_locale
from app.core.dependencies import get_current_user, get_db
from app.core.i18n import translate as _
from app.core.i18n.messages import ChartMessages
from app.core.rate_limit import RateLimits, limiter
from app.models.chart import BirthChart
from app.models.user import User
from app.repositories.chart_repository import ChartRepository
from app.schemas.chart import (
    BirthChartCreate,
    BirthChartList,
    BirthChartRead,
    BirthChartUpdate,
    ChartStatusResponse,
    PDFDownloadResponse,
    PDFDownloadURLResponse,
)
from app.services import chart_service
from app.services.s3_service import s3_service
from app.tasks.astro_tasks import generate_birth_chart_task
from app.tasks.pdf_tasks import generate_chart_pdf_task
from app.translations import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES, get_translation
from app.utils.chart_data_accessor import extract_language_data

router = APIRouter()


def _extract_chart_data_for_response(chart_data: dict[str, Any] | None) -> dict[str, Any] | None:
    """
    Extract language-specific chart data for API response.

    Converts language-first format {"en-US": {...}, "pt-BR": {...}}
    to flat format {...} based on request locale.

    Args:
        chart_data: Chart data in language-first or legacy flat format

    Returns:
        Language-specific chart data, or None if chart_data is None
    """
    if not chart_data:
        return None

    # Get current request locale (from LocaleMiddleware)
    locale = get_locale() or DEFAULT_LANGUAGE

    # Extract language-specific data using backward-compatible accessor
    return extract_language_data(chart_data, locale)


def _translate_phases_for_language(data: dict[str, Any], lang: str) -> dict[str, Any]:
    """
    Re-translate lunar_phase and solar_phase for the specified language.

    For legacy charts stored with single-language phase data, this function
    uses the phase_key to fetch the correct translations for the requested language.

    Args:
        data: Chart data dict containing lunar_phase and/or solar_phase
        lang: Target language code (e.g., "en-US", "pt-BR")

    Returns:
        Chart data with translated phases
    """
    if not data:
        return data

    # Translate lunar_phase if present
    if "lunar_phase" in data and isinstance(data["lunar_phase"], dict):
        lunar = data["lunar_phase"]
        phase_key = lunar.get("phase_key")
        if phase_key:
            lunar["phase_name"] = get_translation(f"lunar_phases.{phase_key}.name", lang)
            lunar["keywords"] = get_translation(f"lunar_phases.{phase_key}.keywords", lang)
            lunar["interpretation"] = get_translation(
                f"lunar_phases.{phase_key}.interpretation", lang
            )

    # Translate solar_phase if present
    if "solar_phase" in data and isinstance(data["solar_phase"], dict):
        solar = data["solar_phase"]
        phase_key = solar.get("phase_key")
        if phase_key and phase_key != "unknown":
            solar["phase_name"] = get_translation(f"solar_phases.{phase_key}.name", lang)
            solar["temperament"] = get_translation(f"solar_phases.{phase_key}.temperament", lang)
            solar["qualities"] = get_translation(f"solar_phases.{phase_key}.qualities", lang)
            solar["description"] = get_translation(f"solar_phases.{phase_key}.description", lang)
            signs_data = get_translation(f"solar_phases.{phase_key}.signs", lang)
            if isinstance(signs_data, list):
                solar["signs"] = signs_data

    return data


def _translate_temperament_for_language(data: dict[str, Any], lang: str) -> dict[str, Any]:
    """
    Re-translate temperament data for the specified language.

    For legacy charts stored with single-language temperament data, this function
    uses the dominant_key to fetch the correct translations for the requested language.

    Args:
        data: Chart data dict containing temperament
        lang: Target language code (e.g., "en-US", "pt-BR")

    Returns:
        Chart data with translated temperament
    """
    if not data or "temperament" not in data:
        return data

    temp = data.get("temperament")
    if not isinstance(temp, dict):
        return data

    # Get the temperament key (e.g., "melancholic", "choleric")
    temp_key = temp.get("dominant_key") or temp.get("temperament_key")
    if temp_key:
        temp_key_lower = temp_key.lower()
        # Translate dominant temperament name
        temp["dominant"] = get_translation(f"temperaments.{temp_key_lower}.name", lang)
        # Translate description
        temp["description"] = get_translation(f"temperaments.{temp_key_lower}.description", lang)

    # Translate factors if present
    factors = temp.get("factors")
    if isinstance(factors, list):
        for factor in factors:
            if isinstance(factor, dict):
                # Translate factor name
                factor_key = factor.get("factor_key")
                if factor_key:
                    factor["factor"] = get_translation(f"factors.{factor_key}", lang)

                # Translate qualities
                qualities = factor.get("qualities")
                if isinstance(qualities, list):
                    translated_qualities = []
                    for q in qualities:
                        q_lower = q.lower() if isinstance(q, str) else q
                        translated = get_translation(f"qualities.{q_lower}", lang)
                        translated_qualities.append(
                            translated if translated != f"qualities.{q_lower}" else q
                        )
                    factor["qualities"] = translated_qualities

                # Translate value (planet in sign format)
                value = factor.get("value", "")
                if isinstance(value, str) and " em " in value.lower():
                    # Portuguese "em" -> translate to English "in" pattern
                    # e.g., "Saturno em Escorpião" -> "Saturn in Scorpio"
                    parts = value.split(" em ", 1)
                    if len(parts) == 2:
                        planet_pt = parts[0].strip()
                        sign_pt = parts[1].strip()
                        # Try to translate planet and sign
                        planet_translated = get_translation(f"planets.{planet_pt}", lang)
                        sign_translated = get_translation(f"signs.{sign_pt}", lang)
                        if planet_translated != f"planets.{planet_pt}":
                            planet_pt = planet_translated
                        if sign_translated != f"signs.{sign_pt}":
                            sign_pt = sign_translated
                        factor["value"] = (
                            f"{planet_pt} in {sign_pt}"
                            if lang.startswith("en")
                            else f"{planet_pt} em {sign_pt}"
                        )
                elif isinstance(value, str):
                    # Try to translate standalone signs
                    sign_translated = get_translation(f"signs.{value}", lang)
                    if sign_translated != f"signs.{value}":
                        factor["value"] = sign_translated
                    # Try to translate solar phase value
                    # e.g., "3ª Fase (Melancólico)" -> "3rd Phase (Melancholic)"
                    if "Fase" in value or "Phase" in value:
                        # Extract phase number
                        match = re.search(r"(\d+)", value)
                        if match:
                            phase_num = match.group(1)
                            factor["value"] = get_translation(
                                f"temperament_solar_phases.{phase_num}", lang
                            )

    return data


def _translate_lord_of_nativity_for_language(data: dict[str, Any], lang: str) -> dict[str, Any]:
    """
    Re-translate lord of nativity data for the specified language.

    For legacy charts stored with single-language lord of nativity data, this function
    uses the planet_key and sign_key to fetch the correct translations.

    Args:
        data: Chart data dict containing lord_of_nativity
        lang: Target language code (e.g., "en-US", "pt-BR")

    Returns:
        Chart data with translated lord of nativity
    """
    if not data or "lord_of_nativity" not in data:
        return data

    lon = data.get("lord_of_nativity")
    if not isinstance(lon, dict):
        return data

    # Translate planet name
    planet_key = lon.get("planet_key")
    if planet_key:
        lon["planet"] = get_translation(f"planets.{planet_key}", lang)

    # Translate sign name
    sign_key = lon.get("sign_key")
    if sign_key:
        lon["sign"] = get_translation(f"signs.{sign_key}", lang)

    # Translate dignity details labels
    dignity_details = lon.get("dignity_details")
    if isinstance(dignity_details, list):
        for detail in dignity_details:
            if isinstance(detail, dict):
                # Get the dignity type (e.g., "domicile", "exaltation")
                dignity_type = detail.get("type", "").lower()
                if dignity_type:
                    detail["label"] = get_translation(f"dignities.{dignity_type}", lang)
                    # Also set label_en for backward compatibility
                    if lang.startswith("en"):
                        detail["label_en"] = detail["label"]

    return data


def _normalize_temperament_fields(data: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize temperament field names from old format to new format.

    Old format: temperament_name, temperament_key
    New format: dominant, dominant_key

    This ensures backward compatibility with existing chart data.
    """
    if "temperament" not in data or not isinstance(data["temperament"], dict):
        return data

    temp = data["temperament"]

    # Map old field names to new ones
    if "temperament_name" in temp and "dominant" not in temp:
        temp["dominant"] = temp["temperament_name"]
    if "temperament_key" in temp and "dominant_key" not in temp:
        temp["dominant_key"] = temp["temperament_key"]

    return data


def extract_chart_data_for_language(chart: BirthChart, lang: str) -> dict[str, Any] | None:
    """
    Extract chart_data for the specified language.

    Handles both new format (language-keyed: {"en-US": {...}, "pt-BR": {...}})
    and legacy format (single language dict with direct keys like "planets", "houses").

    Args:
        chart: BirthChart model instance
        lang: Language code (e.g., "en-US", "pt-BR")

    Returns:
        Chart data dict for the specified language, or None if not available
    """
    if not chart.chart_data:
        return None

    chart_data: dict[str, Any] = chart.chart_data
    result: dict[str, Any] | None = None

    # Check if this is the new language-keyed format
    if lang in chart_data:
        result = chart_data[lang]
    else:
        # Check if any supported language key exists (indicates new format)
        has_language_keys = any(
            supported_lang in chart_data for supported_lang in SUPPORTED_LANGUAGES
        )

        if has_language_keys:
            # New format but requested language not found - fallback to default
            result = chart_data.get(DEFAULT_LANGUAGE, None)
        else:
            # Legacy format - return as-is (no language separation)
            result = chart_data

    # Normalize field names for backward compatibility
    if result:
        result = _normalize_temperament_fields(result)
        # Re-translate phases for the requested language
        # This ensures legacy charts display phases in the correct language
        result = _translate_phases_for_language(result, lang)
        # Translate temperament data
        result = _translate_temperament_for_language(result, lang)
        # Translate lord of nativity data
        result = _translate_lord_of_nativity_for_language(result, lang)

    return result


@router.post(
    "/",
    response_model=BirthChartRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create birth chart (async)",
    description="Create a new birth chart. Calculations run in background. Poll /charts/{id}/status to check progress.",
)
@limiter.limit(RateLimits.CHART_CREATE)
async def create_chart(
    request: Request,
    response: Response,
    chart_data: BirthChartCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Create a new birth chart with async processing.

    **Async Flow:**
    1. Creates initial chart record with status='processing'
    2. Dispatches Celery task to calculate data in background
    3. Returns HTTP 202 Accepted immediately
    4. Client polls GET /charts/{id}/status to track progress

    **Benefits:**
    - Immediate response (no 20-30s wait)
    - Non-blocking user experience
    - Automatic retries on OpenAI failures
    - Scalable via Celery workers

    Args:
        chart_data: Birth chart data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created birth chart with status='processing' (no chart_data yet)
    """
    try:
        # Check chart limit for unverified users
        if not current_user.email_verified:
            chart_repo = ChartRepository(db)
            chart_count = await chart_repo.count_by_user(UUID(str(current_user.id)))
            if chart_count >= settings.UNVERIFIED_USER_CHART_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=_(
                        ChartMessages.UNVERIFIED_CHART_LIMIT,
                        limit=settings.UNVERIFIED_USER_CHART_LIMIT,
                    ),
                )

        # Create initial chart record (no calculations yet)
        chart = await chart_service.create_birth_chart_async(
            db=db,
            user_id=UUID(str(current_user.id)),
            chart_data=chart_data,
        )

        # Dispatch Celery task to process in background
        task = generate_birth_chart_task.delay(str(chart.id))

        # Verify task was accepted and store task_id for tracking
        chart_uuid = UUID(str(chart.id))
        if not task or not task.id:
            logger.error(f"Failed to queue task for chart {chart.id}")
            # Update chart status to failed
            chart_repo = ChartRepository(db)
            chart_obj = await chart_repo.get_by_id(chart_uuid)
            if chart_obj:
                chart_obj.status = "failed"
                chart_obj.error_message = "Task queue unavailable. Please try again."
                await db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chart processing unavailable. Please try again later.",
            )

        # Store task_id on chart for tracking
        chart_repo = ChartRepository(db)
        chart_obj = await chart_repo.get_by_id(chart_uuid)
        if chart_obj:
            chart_obj.task_id = task.id
            await db.commit()
            await db.refresh(chart_obj)

        logger.info(f"Dispatched task {task.id} for chart {chart.id}")
        return chart  # type: ignore[return-value]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating birth chart: {str(e)}",
        ) from e


@router.get(
    "/",
    response_model=BirthChartList,
    summary="List user's birth charts",
    description="Get all birth charts for the current user with pagination.",
)
@limiter.limit(RateLimits.CHART_LIST)
async def list_charts(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> BirthChartList:
    """
    List all birth charts for current user.

    Args:
        current_user: Current authenticated user
        db: Database session
        page: Page number (starts at 1)
        page_size: Number of items per page

    Returns:
        Paginated list of birth charts
    """
    skip = (page - 1) * page_size

    charts = await chart_service.get_user_charts(
        db=db,
        user_id=UUID(str(current_user.id)),
        skip=skip,
        limit=page_size,
    )

    total = await chart_service.count_user_charts(
        db=db,
        user_id=UUID(str(current_user.id)),
    )

    # Extract language-specific chart data for each chart
    for chart in charts:
        chart.chart_data = _extract_chart_data_for_response(chart.chart_data)

    return BirthChartList(
        charts=charts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{chart_id}/status",
    response_model=ChartStatusResponse,
    summary="Get chart processing status",
    description="Check processing status of a birth chart. Use for polling while chart is being generated.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_chart_status(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChartStatusResponse:
    """
    Get birth chart processing status.

    **Use for polling:**
    - After creating a chart (HTTP 202), poll this endpoint every 2-3 seconds
    - Check status: 'processing' → 'completed' or 'failed'
    - When completed, fetch full chart via GET /charts/{id}

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Chart status information (status, progress, error_message)
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )
        return ChartStatusResponse(
            id=chart.id,
            status=chart.status,
            progress=chart.progress,
            error_message=chart.error_message,
            task_id=chart.task_id,
        )
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}",
    response_model=BirthChartRead,
    summary="Get birth chart",
    description="Get a specific birth chart by ID. Admins can access any chart. Use `lang` query param to select language.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    lang: str = Query(
        DEFAULT_LANGUAGE,
        description="Language for chart data (en-US or pt-BR)",
        regex="^(en-US|pt-BR)$",
    ),
) -> BirthChartRead:
    """
    Get a birth chart by ID.

    Admins can access any chart in the system.
    Use the `lang` query parameter to select the language for translated content.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session
        lang: Language code for translated content (default: en-US)

    Returns:
        Birth chart data in the specified language
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            is_admin=current_user.is_admin,
        )

        # Extract chart_data for the requested language
        chart_data = extract_chart_data_for_language(chart, lang)

        # Build response with language-specific chart_data
        return BirthChartRead(
            id=chart.id,
            user_id=chart.user_id,
            person_name=chart.person_name,
            gender=chart.gender,
            birth_datetime=chart.birth_datetime,
            birth_timezone=chart.birth_timezone,
            latitude=float(chart.latitude),
            longitude=float(chart.longitude),
            city=chart.city,
            country=chart.country,
            notes=chart.notes,
            tags=chart.tags,
            house_system=chart.house_system,
            zodiac_type=chart.zodiac_type,
            node_type=chart.node_type,
            status=chart.status,
            progress=chart.progress,
            error_message=chart.error_message,
            chart_data=chart_data,
            pdf_url=chart.pdf_url,
            pdf_generated_at=chart.pdf_generated_at,
            pdf_generating=chart.pdf_generating,
            pdf_task_id=chart.pdf_task_id,
            visibility=chart.visibility,
            share_uuid=chart.share_uuid,
            created_at=chart.created_at,
            updated_at=chart.updated_at,
            deleted_at=chart.deleted_at,
        )
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.put(
    "/{chart_id}",
    response_model=BirthChartRead,
    summary="Update birth chart",
    description="Update birth chart metadata (name, notes, tags, etc).",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def update_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    update_data: BirthChartUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Update a birth chart.

    Args:
        chart_id: Birth chart UUID
        update_data: Updated chart data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated birth chart
    """
    try:
        chart = await chart_service.update_birth_chart(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            update_data=update_data,
        )
        return chart  # type: ignore[return-value]
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.delete(
    "/{chart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete birth chart",
    description="Delete a birth chart (soft delete by default).",
)
@limiter.limit(RateLimits.CHART_DELETE)
async def delete_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    hard_delete: bool = Query(False, description="Permanently delete if true"),
) -> None:
    """
    Delete a birth chart.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session
        hard_delete: If true, permanently delete; otherwise soft delete
    """
    try:
        await chart_service.delete_birth_chart(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            soft_delete=not hard_delete,
        )
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


# ============================================================
# PDF EXPORT ENDPOINTS
# ============================================================


@router.post(
    "/{chart_id}/generate-pdf",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate PDF report",
    description="Generate a PDF report for the birth chart. Processing happens in background.",
)
@limiter.limit(RateLimits.CHART_CREATE)
async def generate_chart_pdf(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """
    Generate PDF report for a birth chart (async).

    **Async Flow:**
    1. Verifies chart exists and user has access
    2. Dispatches Celery task to generate PDF in background
    3. Returns HTTP 202 Accepted immediately
    4. Client polls GET /charts/{id}/pdf-status to track progress

    **Auto-generates interpretations:**
    - If chart lacks AI interpretations, they will be generated automatically
    - This ensures complete PDF reports with all sections

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Message with task status
    """
    try:
        # Block PDF generation for unverified users
        if not current_user.email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=_(ChartMessages.UNVERIFIED_PDF_BLOCKED),
            )

        # Verify chart exists and user has access
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Verify chart has calculated data
        if not chart.chart_data or chart.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chart must be fully calculated before generating PDF. Wait for chart calculations to complete.",
            )

        # Atomically acquire PDF generation lock (prevents race conditions)
        # This UPDATE only succeeds if pdf_generating is currently False
        stmt = (
            update(BirthChart)
            .where(BirthChart.id == chart_id, BirthChart.pdf_generating == False)  # noqa: E712
            .values(pdf_generating=True)
        )
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:  # type: ignore[attr-defined]
            # Another request already started PDF generation
            # Refresh chart to get current task_id for debugging
            await db.refresh(chart)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"PDF is already being generated for this chart. Task ID: {chart.pdf_task_id}. Please wait for the current generation to complete.",
            )

        # Dispatch Celery task now that we have the lock
        try:
            task = generate_chart_pdf_task.delay(str(chart_id))
        except Exception as e:
            # Rollback the flag if task dispatch fails (e.g., Redis down)
            logger.error(f"Failed to dispatch PDF task for chart {chart_id}: {e}")
            rollback_stmt = (
                update(BirthChart)
                .where(BirthChart.id == chart_id)
                .values(pdf_generating=False, pdf_task_id=None)
            )
            await db.execute(rollback_stmt)
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="PDF generation service temporarily unavailable. Please try again later.",
            ) from e

        # Update with task ID for tracking
        chart.pdf_task_id = task.id
        await db.commit()

        return {
            "message": "PDF generation started",
            "chart_id": str(chart_id),
            "task_id": task.id,
        }

    except HTTPException:
        raise
    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}/pdf-status",
    response_model=PDFDownloadResponse,
    summary="Get PDF generation status and download URL",
    description="Check the status of PDF generation and get presigned download URL if ready.",
)
@limiter.limit(RateLimits.CHART_READ)
async def get_pdf_status(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PDFDownloadResponse:
    """
    Get PDF generation status and download URL for a birth chart.

    **Workflow:**
    1. After calling POST /charts/{id}/generate-pdf, poll this endpoint
    2. Check status field: 'ready', 'generating', 'failed', or 'not_found'
    3. If status is 'ready', use download_url to download (expires in 1 hour for S3)

    **S3 Integration:**
    - If PDF is stored in S3, returns a presigned URL (valid for 1 hour)
    - If PDF is stored locally, returns local file path
    - Presigned URLs are regenerated on each request

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        PDF status with download URL and metadata
    """
    from app.core.config import settings

    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Check if PDF exists
        if not chart.pdf_url:
            # No PDF generated yet
            if chart.error_message and "PDF generation failed" in chart.error_message:
                return PDFDownloadResponse(
                    status="failed",
                    message=chart.error_message,
                )
            else:
                return PDFDownloadResponse(
                    status="generating",
                    message="PDF generation is in progress. Please check back in a few moments.",
                )

        # PDF exists - determine download URL
        download_url = None
        expires_in = None

        if chart.pdf_url.startswith("s3://"):
            # S3 URL - generate presigned URL
            download_url = s3_service.generate_presigned_url(
                s3_url=chart.pdf_url,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
            )

            if download_url:
                expires_in = settings.S3_PRESIGNED_URL_EXPIRATION
            else:
                # Failed to generate presigned URL
                return PDFDownloadResponse(
                    status="failed",
                    message="Failed to generate download URL. Please try again.",
                    generated_at=chart.pdf_generated_at,
                )
        else:
            # Local file path - return as-is
            download_url = chart.pdf_url

        return PDFDownloadResponse(
            status="ready",
            download_url=download_url,
            expires_in=expires_in,
            generated_at=chart.pdf_generated_at,
            message="PDF is ready for download.",
        )

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


@router.get(
    "/{chart_id}/download-pdf",
    response_model=PDFDownloadURLResponse,
    summary="Get PDF download URL",
    description="Get the presigned download URL for a birth chart PDF.",
)
@limiter.limit(RateLimits.CHART_READ)
async def download_chart_pdf(
    request: Request,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    response: Response,
) -> PDFDownloadURLResponse:
    """
    Get presigned URL for PDF download.

    **Prerequisites:**
    1. Chart must be fully calculated (status='completed')
    2. PDF must have been generated (call POST /charts/{id}/generate-pdf first)
    3. PDF generation must be complete (poll /charts/{id}/pdf-status)

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session
        response: FastAPI response object for setting headers

    Returns:
        PDFDownloadURLResponse with presigned URL or local file URL
    """
    try:
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
        )

        # Check if PDF exists
        if not chart.pdf_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF not generated yet. Call POST /charts/{id}/generate-pdf first.",
            )

        # Generate filename
        filename = f"natal_chart_{chart.person_name}_{chart_id}.pdf".replace(" ", "_")

        # Set cache-control headers to prevent browser caching
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, private, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        # Handle S3 URLs - return presigned URL as JSON
        if chart.pdf_url.startswith("s3://"):
            # Generate presigned URL for S3 download
            download_url = s3_service.generate_presigned_url(
                s3_url=chart.pdf_url,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
            )

            if not download_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to generate download URL from S3. Please try again.",
                )

            # Return presigned URL in JSON response
            return PDFDownloadURLResponse(
                download_url=download_url,
                filename=filename,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRATION,
                content_type="application/pdf",
            )

        # Handle local files - for now, just return the path as-is
        # Frontend will need to construct full URL
        return PDFDownloadURLResponse(
            download_url=chart.pdf_url,
            filename=filename,
            expires_in=None,  # Local files don't expire
            content_type="application/pdf",
        )

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None


# ============================================================
# RECALCULATE ENDPOINT
# ============================================================


@router.post(
    "/{chart_id}/recalculate",
    response_model=BirthChartRead,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Recalculate birth chart",
    description="Force recalculation of all chart data and interpretations.",
)
@limiter.limit(RateLimits.CHART_UPDATE)
async def recalculate_chart(
    request: Request,
    response: Response,
    chart_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BirthChartRead:
    """
    Force recalculation of a birth chart.

    This endpoint triggers a full recalculation of the chart data,
    including all planetary positions, houses, aspects, dignities,
    sect analysis, and other traditional calculations.

    Use this when you want to regenerate the chart with potentially
    updated calculation logic or to refresh cached data.

    Args:
        chart_id: Birth chart UUID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated birth chart with recalculated data
    """
    try:
        # Verify access and get the chart
        chart = await chart_service.get_chart_by_id(
            db=db,
            chart_id=chart_id,
            user_id=UUID(str(current_user.id)),
            is_admin=current_user.is_admin,
        )

        # Update status to processing
        chart.status = "processing"
        chart.progress = 0
        await db.commit()
        await db.refresh(chart)

        # Dispatch Celery task to recalculate in background
        task = generate_birth_chart_task.delay(str(chart_id))

        # Verify task was accepted and store task_id
        if not task or not task.id:
            logger.error(f"Failed to queue recalculation task for chart {chart_id}")
            chart.status = "failed"
            chart.error_message = "Task queue unavailable. Please try again."
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Chart recalculation unavailable. Please try again later.",
            )

        chart.task_id = task.id
        await db.commit()
        await db.refresh(chart)

        logger.info(f"Dispatched recalculation task {task.id} for chart {chart_id}")
        return chart  # type: ignore[return-value]

    except chart_service.ChartNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Birth chart not found",
        ) from None
    except chart_service.UnauthorizedAccessError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this birth chart",
        ) from None
