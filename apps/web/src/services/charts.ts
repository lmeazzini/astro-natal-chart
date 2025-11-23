/**
 * Birth chart service for creating and managing natal charts
 */

import { apiClient } from './api';
import type { LunarPhaseData } from '@/components/LunarPhase';
import type { SolarPhaseData } from '@/components/SolarPhase';
import type { LordOfNativityData } from '@/components/LordOfNativity';
import type { TemperamentData } from '@/components/TemperamentDisplay';

export interface BirthChartCreate {
  person_name: string;
  gender?: string | null;
  birth_datetime: string; // ISO format
  birth_timezone: string;
  latitude: number;
  longitude: number;
  city?: string | null;
  country?: string | null;
  notes?: string | null;
  tags?: string[] | null;
  house_system?: string;
  zodiac_type?: string;
  node_type?: string;
}

export interface BirthChartUpdate {
  // Personal info (no recalculation needed)
  person_name?: string | null;
  gender?: string | null;
  notes?: string | null;
  tags?: string[] | null;
  visibility?: string | null;
  // Birth data (triggers recalculation if changed)
  birth_datetime?: string | null; // ISO format
  birth_timezone?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  city?: string | null;
  country?: string | null;
  // Technical settings (triggers recalculation if changed)
  house_system?: string | null;
  zodiac_type?: string | null;
  node_type?: string | null;
}

export interface PlanetPosition {
  name: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
  house: number;
  retrograde: boolean;
}

export interface HousePosition {
  house: number;
  longitude: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
}

export interface AspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  angle: number;
  orb: number;
  applying: boolean;
}

export interface ArabicPart {
  longitude: number;
  sign: string;
  degree: number;
  house: number;
}

export interface ArabicParts {
  fortune: ArabicPart;
  spirit: ArabicPart;
  eros: ArabicPart;
  necessity: ArabicPart;
}

export interface PlanetSectStatus {
  name: string;
  sign: string;
  house: number;
  degree: number;
  planet_sect: 'diurnal' | 'nocturnal' | 'neutral';
  in_sect: boolean;
  faction: 'benefic' | 'malefic' | 'luminary' | 'neutral';
  performance: 'optimal' | 'moderate' | 'challenging';
}

export interface SectAnalysisData {
  sect: 'diurnal' | 'nocturnal';
  sun_house: number;
  planets_by_sect: {
    in_sect: PlanetSectStatus[];
    out_of_sect: PlanetSectStatus[];
    neutral: PlanetSectStatus[];
  };
  benefics: {
    in_sect: PlanetSectStatus | null;
    out_of_sect: PlanetSectStatus | null;
  };
  malefics: {
    in_sect: PlanetSectStatus | null;
    out_of_sect: PlanetSectStatus | null;
  };
}

export interface BirthChart {
  id: string;
  user_id: string;
  person_name: string;
  gender: string | null;
  birth_datetime: string;
  birth_timezone: string;
  latitude: number;
  longitude: number;
  city: string | null;
  country: string | null;
  notes: string | null;
  tags: string[] | null;
  house_system: string;
  zodiac_type: string;
  node_type: string;
  status: string; // processing, completed, failed
  progress: number; // 0-100
  error_message: string | null;
  chart_data: {
    planets: PlanetPosition[];
    houses: HousePosition[];
    aspects: AspectData[];
    ascendant: number;
    midheaven: number;
    sect?: string;
    sect_analysis?: SectAnalysisData;
    lunar_phase?: LunarPhaseData;
    solar_phase?: SolarPhaseData;
    lord_of_nativity?: LordOfNativityData;
    temperament?: TemperamentData;
    arabic_parts?: ArabicParts;
    calculation_timestamp: string;
  } | null;
  visibility: string;
  share_uuid: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface BirthChartList {
  charts: BirthChart[];
  total: number;
  page: number;
  page_size: number;
}

export interface ChartStatus {
  id: string;
  status: string; // processing, completed, failed
  progress: number; // 0-100
  error_message: string | null;
  task_id: string | null;
}

export interface ChartLimitInfo {
  chart_count: number;
  limit: number;
  is_verified: boolean;
}

export const chartsService = {
  /**
   * Create a new birth chart
   */
  async create(data: BirthChartCreate, token: string): Promise<BirthChart> {
    return apiClient.post<BirthChart>('/api/v1/charts/', data, token);
  },

  /**
   * Get chart count for the current user (for limit checking)
   */
  async getCount(token: string): Promise<number> {
    const result = await apiClient.get<BirthChartList>(
      '/api/v1/charts/?page=1&page_size=1',
      token
    );
    return result.total;
  },

  /**
   * List user's birth charts
   */
  async list(
    token: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<BirthChartList> {
    return apiClient.get<BirthChartList>(
      `/api/v1/charts/?page=${page}&page_size=${pageSize}`,
      token
    );
  },

  /**
   * Get a specific birth chart
   */
  async getById(chartId: string, token: string): Promise<BirthChart> {
    return apiClient.get<BirthChart>(`/api/v1/charts/${chartId}`, token);
  },

  /**
   * Get chart processing status (for polling)
   */
  async getStatus(chartId: string, token: string): Promise<ChartStatus> {
    return apiClient.get<ChartStatus>(`/api/v1/charts/${chartId}/status`, token);
  },

  /**
   * Update a birth chart
   * If birth data changes, chart will be recalculated
   */
  async update(chartId: string, data: BirthChartUpdate, token: string): Promise<BirthChart> {
    return apiClient.put<BirthChart>(`/api/v1/charts/${chartId}`, data, token);
  },

  /**
   * Delete a birth chart
   */
  async delete(chartId: string, token: string, hardDelete: boolean = false): Promise<void> {
    return apiClient.delete<void>(
      `/api/v1/charts/${chartId}?hard_delete=${hardDelete}`,
      token
    );
  },

  /**
   * Recalculate a birth chart (forces recalculation of all chart data)
   * This triggers the same recalculation as updating birth data
   */
  async recalculate(chartId: string, token: string): Promise<BirthChart> {
    return apiClient.post<BirthChart>(`/api/v1/charts/${chartId}/recalculate`, {}, token);
  },
};
