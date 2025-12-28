"""
Longevity analysis service combining Hyleg and Alcochoden calculations.

This module provides the unified longevity analysis for traditional astrology,
combining:
- Hyleg (Giver of Life) - the vital force significator
- Alcochoden (Giver of Years) - the planet determining lifespan

IMPORTANT DISCLAIMER:
Longevity calculations are presented purely for historical and educational purposes.
Traditional astrology's approach to predicting lifespan is not scientifically validated
and should never be used for medical decisions, health predictions, or causing anxiety
about life expectancy.
"""

from typing import Any

from app.astro.alcochoden import calculate_alcochoden
from app.astro.hyleg import calculate_hyleg
from app.translations import get_translation


def calculate_longevity_analysis(
    planets: list[dict[str, Any]],
    houses: list[dict[str, Any]],
    aspects: list[dict[str, Any]],
    ascendant: float,
    arabic_parts: list[dict[str, Any]],
    sect: str,
    birth_jd: float,
    sun_longitude: float,
    method: str = "ptolemaic",
    language: str = "en-US",
) -> dict[str, Any]:
    """
    Complete longevity analysis: Hyleg + Alcochoden.

    This function performs the traditional astrological longevity analysis
    by first determining the Hyleg (vital force point) and then calculating
    the Alcochoden (planet determining years of life).

    Args:
        planets: List of planet data with positions and dignities
        houses: List of house cusp data
        aspects: List of aspect data between planets
        ascendant: Longitude of the Ascendant
        arabic_parts: List of Arabic Parts (Part of Fortune is first)
        sect: Chart sect - "diurnal" or "nocturnal"
        birth_jd: Julian Day of birth
        sun_longitude: Sun's longitude
        method: Calculation method (currently only "ptolemaic" supported)
        language: Language code for translations

    Returns:
        Dictionary containing:
        - hyleg: Hyleg calculation result or None
        - alcochoden: Alcochoden calculation result or None
        - summary: Summary of the longevity analysis
        - educational_disclaimer: Important disclaimer text
    """
    # Calculate Hyleg
    hyleg = calculate_hyleg(
        planets=planets,
        houses=houses,
        aspects=aspects,
        ascendant=ascendant,
        arabic_parts=arabic_parts,
        sect=sect,
        birth_jd=birth_jd,
        method=method,
        language=language,
    )

    # Calculate Alcochoden (requires Hyleg)
    alcochoden = calculate_alcochoden(
        hyleg_data=hyleg,
        planets=planets,
        houses=houses,
        aspects=aspects,
        sun_longitude=sun_longitude,
        sect=sect,
        language=language,
    )

    # Build summary
    summary = build_longevity_summary(hyleg, alcochoden, language)

    # Get educational disclaimer
    disclaimer = get_translation("longevity.educational_disclaimer", language)

    return {
        "hyleg": hyleg,
        "alcochoden": alcochoden,
        "summary": summary,
        "educational_disclaimer": disclaimer,
    }


def build_longevity_summary(
    hyleg: dict[str, Any] | None,
    alcochoden: dict[str, Any] | None,
    language: str,
) -> dict[str, Any]:
    """
    Build a summary of the longevity analysis.

    Args:
        hyleg: Hyleg calculation result
        alcochoden: Alcochoden calculation result
        language: Language code for translations

    Returns:
        Summary dictionary
    """
    # Determine vital force strength based on Hyleg condition
    if hyleg is None or hyleg.get("hyleg") is None:
        vital_force = "undetermined"
        vital_force_description = get_translation("longevity.summary.no_hyleg", language)
    else:
        hyleg_dignity = hyleg.get("hyleg_dignity")
        if hyleg_dignity:
            score = hyleg_dignity.get("score", 0)
            if score >= 4:
                vital_force = "strong"
            elif score >= 0:
                vital_force = "moderate"
            else:
                vital_force = "weak"
        else:
            # Hyleg is a point (ASC, Fortune, Syzygy), consider moderate
            vital_force = "moderate"

        vital_force_description = get_translation(
            f"longevity.summary.vital_force.{vital_force}", language
        )

    # Determine potential years
    if alcochoden is None or alcochoden.get("alcochoden") is None:
        potential_years = None
        years_confidence = "undetermined"
    else:
        potential_years = alcochoden.get("final_years")
        # Confidence based on Alcochoden condition
        alco_condition = alcochoden.get("alcochoden_condition", {})
        if alco_condition.get("is_combust") or alco_condition.get("is_debilitated"):
            years_confidence = "low"
        elif alco_condition.get("essential_dignity") in ["domicile", "exaltation"]:
            years_confidence = "high"
        else:
            years_confidence = "moderate"

    return {
        "vital_force": vital_force,
        "vital_force_description": vital_force_description,
        "potential_years": potential_years,
        "years_confidence": years_confidence,
        "hyleg_found": hyleg is not None and hyleg.get("hyleg") is not None,
        "alcochoden_found": alcochoden is not None and alcochoden.get("alcochoden") is not None,
        "method": "ptolemaic",
    }
