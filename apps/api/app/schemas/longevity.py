"""
Longevity analysis schemas for Hyleg and Alcochoden calculations.

These schemas define the API response models for traditional astrology
longevity analysis endpoints.
"""

from typing import Any

from pydantic import BaseModel, Field


class HylegCandidateEvaluation(BaseModel):
    """Evaluation details for a Hyleg candidate."""

    candidate: str = Field(..., description="Name of the candidate (Sun, Moon, Ascendant, etc.)")
    longitude: float = Field(..., description="Ecliptic longitude of the candidate")
    sign: str = Field(..., description="Zodiac sign of the candidate")
    house: int = Field(..., ge=1, le=12, description="House number where the candidate is located")
    in_hylegical_place: bool = Field(
        ..., description="Whether the candidate is in a hylegical place"
    )
    is_qualified: bool = Field(..., description="Whether the candidate qualifies as Hyleg")
    qualification_reason: str | None = Field(
        None, description="Reason for qualification or rejection"
    )
    aspecting_planets: list[str] = Field(
        default_factory=list, description="Planets aspecting this candidate"
    )


class HylegDignity(BaseModel):
    """Essential dignity data for the Hyleg."""

    score: int = Field(..., description="Total dignity score")
    dignities: list[str] = Field(default_factory=list, description="List of dignities held")
    is_ruler: bool = Field(False, description="Whether in domicile")
    is_exalted: bool = Field(False, description="Whether exalted")
    is_detriment: bool = Field(False, description="Whether in detriment")
    is_fall: bool = Field(False, description="Whether in fall")
    classification: str = Field("peregrine", description="dignified, peregrine, or debilitated")


class HylegResponse(BaseModel):
    """Complete Hyleg calculation response."""

    hyleg: str | None = Field(None, description="Name of the Hyleg, or null if not found")
    hyleg_longitude: float | None = Field(None, description="Ecliptic longitude of the Hyleg")
    hyleg_sign: str | None = Field(None, description="Zodiac sign of the Hyleg")
    hyleg_house: int | None = Field(None, ge=1, le=12, description="House number of the Hyleg")
    is_day_chart: bool = Field(..., description="Whether this is a day (diurnal) chart")
    method: str = Field("ptolemaic", description="Calculation method used")
    qualification_reason: str | None = Field(None, description="Reason the Hyleg qualified")
    hyleg_dignity: dict[str, Any] | None = Field(
        None, description="Essential dignity data for the Hyleg"
    )
    aspecting_planets: list[str] = Field(
        default_factory=list, description="Planets aspecting the Hyleg"
    )
    domicile_lord: str | None = Field(None, description="Domicile ruler of the Hyleg's sign")
    candidates_evaluated: list[HylegCandidateEvaluation] = Field(
        default_factory=list, description="All candidates that were evaluated"
    )


class AlcochodenCandidate(BaseModel):
    """Evaluation details for an Alcochoden candidate."""

    planet: str = Field(..., description="Name of the planet")
    dignity_type: str = Field(..., description="Highest dignity type at Hyleg's degree")
    dignity_points: int = Field(..., description="Total dignity points at Hyleg's degree")
    aspects_hyleg: bool = Field(..., description="Whether the planet aspects the Hyleg")
    aspect_type: str | None = Field(None, description="Type of aspect to Hyleg")
    selected: bool = Field(False, description="Whether this candidate was selected as Alcochoden")


class AlcochodenAspectToHyleg(BaseModel):
    """Aspect between Alcochoden and Hyleg."""

    type: str = Field(..., description="Aspect type (Conjunction, Trine, etc.)")
    orb: float = Field(..., description="Orb of the aspect in degrees")
    applying: bool | None = Field(None, description="Whether the aspect is applying")


class AlcochodenDignityAtHyleg(BaseModel):
    """Dignity that the Alcochoden has at the Hyleg's degree."""

    type: str = Field(
        ..., description="Dignity type (domicile, exaltation, triplicity, term, face)"
    )
    points: int = Field(..., description="Points for this dignity")


class AlcochodenCondition(BaseModel):
    """Condition of the Alcochoden planet."""

    essential_dignity: str | None = Field(
        None, description="Essential dignity state of the Alcochoden"
    )
    accidental_dignity: str = Field(..., description="House type (angular, succedent, cadent)")
    is_retrograde: bool = Field(False, description="Whether the Alcochoden is retrograde")
    is_combust: bool = Field(False, description="Whether the Alcochoden is combust")
    is_debilitated: bool = Field(False, description="Whether the Alcochoden is debilitated")
    benefic_aspects: list[str] = Field(
        default_factory=list, description="Benefic aspects to Alcochoden"
    )
    malefic_aspects: list[str] = Field(
        default_factory=list, description="Malefic aspects to Alcochoden"
    )


class PlanetaryYears(BaseModel):
    """Planetary years for the Alcochoden."""

    minor: float = Field(..., description="Minor years (debilitated condition)")
    middle: float = Field(..., description="Middle years (peregrine condition)")
    major: float = Field(..., description="Major years (dignified condition)")


class YearModification(BaseModel):
    """A modification to the base years."""

    reason: str = Field(..., description="Reason for the modification")
    adjustment: int = Field(..., description="Years added or subtracted")
    type: str | None = Field(None, description="Type of modification")


class AlcochodenResponse(BaseModel):
    """Complete Alcochoden calculation response."""

    alcochoden: str | None = Field(
        None, description="Name of the Alcochoden planet, or null if not found"
    )
    alcochoden_longitude: float | None = Field(
        None, description="Ecliptic longitude of the Alcochoden"
    )
    alcochoden_sign: str | None = Field(None, description="Zodiac sign of the Alcochoden")
    alcochoden_house: int | None = Field(
        None, ge=1, le=12, description="House number of the Alcochoden"
    )
    hyleg_degree: float | None = Field(None, description="Degree of the Hyleg within its sign")
    hyleg_sign: str | None = Field(None, description="Sign of the Hyleg")
    dignity_at_hyleg: dict[str, Any] | None = Field(
        None, description="Dignity the Alcochoden has at Hyleg's degree"
    )
    aspect_to_hyleg: dict[str, Any] | None = Field(
        None, description="Aspect from Alcochoden to Hyleg"
    )
    alcochoden_condition: dict[str, Any] | None = Field(
        None, description="Condition of the Alcochoden"
    )
    years: dict[str, float] | None = Field(
        None, description="Minor, middle, and major years for this planet"
    )
    year_type_selected: str | None = Field(
        None, description="Which year type was selected (minor/middle/major)"
    )
    base_years: float | None = Field(None, description="Base years before modifications")
    modifications: list[YearModification] = Field(
        default_factory=list, description="Year modifications applied"
    )
    final_years: float | None = Field(None, description="Final years after all modifications")
    candidates_evaluated: list[AlcochodenCandidate] = Field(
        default_factory=list, description="All candidates that were evaluated"
    )
    no_alcochoden_reason: str | None = Field(None, description="Reason if no Alcochoden was found")


class LongevitySummary(BaseModel):
    """Summary of the longevity analysis."""

    vital_force: str = Field(
        ..., description="Strength of vital force (strong, moderate, weak, undetermined)"
    )
    vital_force_description: str | None = Field(None, description="Description of the vital force")
    potential_years: float | None = Field(
        None, description="Potential years from Alcochoden calculation"
    )
    years_confidence: str = Field(
        ..., description="Confidence level (high, moderate, low, undetermined)"
    )
    hyleg_found: bool = Field(..., description="Whether a Hyleg was found")
    alcochoden_found: bool = Field(..., description="Whether an Alcochoden was found")
    method: str = Field("ptolemaic", description="Calculation method used")


class LongevityResponse(BaseModel):
    """Complete longevity analysis response combining Hyleg and Alcochoden."""

    hyleg: HylegResponse | None = Field(
        None, description="Hyleg (Giver of Life) calculation result"
    )
    alcochoden: AlcochodenResponse | None = Field(
        None, description="Alcochoden (Giver of Years) calculation result"
    )
    summary: LongevitySummary = Field(..., description="Summary of the longevity analysis")
    educational_disclaimer: str = Field(
        ...,
        description="Important disclaimer about the educational nature of this calculation",
    )
