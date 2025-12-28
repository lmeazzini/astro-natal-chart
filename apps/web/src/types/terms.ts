/**
 * TypeScript types for Planetary Terms (Bounds) Analysis
 *
 * These types correspond to the backend Pydantic schemas in:
 * apps/api/app/schemas/terms.py
 */

// ============================================================================
// Term System Types
// ============================================================================

export type TermSystem = 'egyptian' | 'ptolemaic' | 'chaldean' | 'dorothean';

// ============================================================================
// Term Entry Types
// ============================================================================

export interface TermEntry {
  ruler: string;
  start: number;
  end: number;
}

// ============================================================================
// Term Ruler Lookup Response
// ============================================================================

export interface TermRulerResponse {
  longitude: number;
  sign: string;
  degree_in_sign: number;
  term_ruler: string;
  term_start: number;
  term_end: number;
  term_system: TermSystem;
}

// ============================================================================
// Chart Terms Types
// ============================================================================

export interface PlanetTermInfo {
  planet: string;
  term_ruler: string;
  in_own_term: boolean;
}

export interface TermsSummary {
  planets_in_own_term: string[];
  term_ruler_frequency: Record<string, number>;
}

export interface ChartTermsData {
  system: TermSystem;
  planets: PlanetTermInfo[];
  summary: TermsSummary;
}

// ============================================================================
// Terms Table Types
// ============================================================================

export interface TermsTableData {
  system: TermSystem;
  signs: Record<string, TermEntry[]>;
}

// ============================================================================
// Component Props
// ============================================================================

export interface PlanetaryTermsProps {
  chartId: string;
  isLoading?: boolean;
}

export interface TermsTableProps {
  system: TermSystem;
  onSystemChange?: (system: TermSystem) => void;
}

export interface PlanetTermsDisplayProps {
  termsData: ChartTermsData;
  isLoading?: boolean;
}
