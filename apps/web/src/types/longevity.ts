/**
 * TypeScript types for Longevity Analysis (Hyleg + Alcochoden)
 *
 * These types correspond to the backend Pydantic schemas in:
 * apps/api/app/schemas/longevity.py
 */

// ============================================================================
// Hyleg Types
// ============================================================================

export interface HylegCandidateEvaluation {
  candidate: string;
  longitude: number;
  sign: string;
  house: number;
  in_hylegical_place: boolean;
  is_qualified: boolean;
  qualification_reason: string;
  aspecting_planets: string[];
}

export interface HylegDignity {
  planet: string;
  sign: string;
  total_score: number;
  classification: string;
  dignities: Record<string, unknown>;
}

export interface HylegData {
  hyleg: string | null;
  hyleg_longitude: number | null;
  hyleg_sign: string | null;
  hyleg_house: number | null;
  is_day_chart: boolean;
  method: string;
  qualification_reason: string;
  hyleg_dignity: HylegDignity | null;
  aspecting_planets: string[];
  domicile_lord: string | null;
  candidates_evaluated: HylegCandidateEvaluation[];
}

// ============================================================================
// Alcochoden Types
// ============================================================================

export interface YearModification {
  type: string;
  description: string;
  value: number;
}

export interface AlcochodenCandidate {
  planet: string;
  dignity_type: string;
  dignity_points: number;
  total_dignity_points: number;
  aspects_hyleg: boolean;
  is_combust: boolean;
  in_domicile: boolean;
  in_exaltation: boolean;
  in_detriment: boolean;
  in_fall: boolean;
  classification: string;
}

export interface PlanetaryYears {
  minor: number;
  middle: number;
  major: number;
}

export interface AlcochodenData {
  alcochoden: string | null;
  alcochoden_longitude: number | null;
  alcochoden_sign: string | null;
  alcochoden_house: number | null;
  years: PlanetaryYears | null;
  year_type: string | null;
  base_years: number | null;
  modified_years: number | null;
  modifications: YearModification[];
  candidates_evaluated: AlcochodenCandidate[];
  no_alcochoden_reason: string | null;
}

// ============================================================================
// Combined Longevity Types
// ============================================================================

export interface LongevitySummary {
  vital_force_planet: string | null;
  vital_force_assessment: string;
  years_planet: string | null;
  years_type: string | null;
  estimated_years: number | null;
}

export interface LongevityData {
  hyleg: HylegData | null;
  alcochoden: AlcochodenData | null;
  summary: LongevitySummary;
  educational_disclaimer: string;
}

// ============================================================================
// Component Props
// ============================================================================

export interface LongevityAnalysisProps {
  longevity: LongevityData | null;
  isLoading?: boolean;
}

export interface HylegDisplayProps {
  hyleg: HylegData;
}

export interface AlcochodenDisplayProps {
  alcochoden: AlcochodenData;
}
