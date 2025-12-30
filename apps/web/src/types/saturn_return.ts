/**
 * Saturn Return types for API responses.
 */

export interface SaturnReturnPass {
  date: string;
  longitude: number;
  is_retrograde: boolean;
  pass_number: number;
}

export interface SaturnReturn {
  return_number: number;
  passes: SaturnReturnPass[];
  start_date: string;
  end_date: string;
  age_at_return: number;
}

export interface SaturnReturnAnalysis {
  natal_saturn_longitude: number;
  natal_saturn_sign: string;
  natal_saturn_house: number;
  natal_saturn_degree: number;
  current_saturn_longitude: number;
  current_saturn_sign: string;
  cycle_progress_percent: number;
  days_until_next_return: number | null;
  past_returns: SaturnReturn[];
  current_return: SaturnReturn | null;
  next_return: SaturnReturn | null;
}

export interface SaturnReturnInterpretation {
  title: string;
  natal_saturn_sign: string;
  natal_saturn_house: number;
  general_introduction: string;
  general_interpretation: string;
  sign_interpretation: string;
  house_interpretation: string;
  current_phase_interpretation: string | null;
}
