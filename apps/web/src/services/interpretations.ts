/**
 * Chart interpretations service for AI-generated interpretations
 * All interpretations now use RAG (Retrieval-Augmented Generation) by default
 */

import { apiClient } from './api';

/**
 * RAG source information for enhanced interpretations
 */
export interface RAGSourceInfo {
  source: string;
  page: string | null;
  relevance_score: number;
  content_preview: string;
}

/**
 * Single interpretation item with enhanced metadata
 */
export interface InterpretationItem {
  content: string;
  source: 'database' | 'cache' | 'rag';
  rag_sources: RAGSourceInfo[] | null;
  is_outdated?: boolean;
  cached?: boolean;
  prompt_version?: string;
  generated_at?: string;
}

/**
 * Growth suggestions data structure
 */
export interface GrowthPoint {
  area: string;
  indicator: string;
  explanation: string;
  practical_actions: string[];
  mindset_shift: string;
}

export interface Challenge {
  name: string;
  pattern: string;
  manifestation: string;
  strategy: string;
  practices: string[];
}

export interface Opportunity {
  talent: string;
  indicator: string;
  description: string;
  leverage_tips: string[];
}

export interface Purpose {
  soul_direction: string;
  vocation: string;
  contribution: string;
  integration: string;
  next_steps: string[];
}

export interface GrowthSuggestionsData {
  growth_points: GrowthPoint[];
  challenges: Challenge[];
  opportunities: Opportunity[];
  purpose: Purpose | null;
  summary: string;
}

/**
 * Interpretation metadata (cache statistics)
 */
export interface InterpretationMetadata {
  total_items: number;
  cache_hits_db: number;
  cache_hits_cache: number;
  rag_generations: number;
  outdated_count: number;
  documents_used: number;
  prompt_version_current: string;
  response_time_ms?: number;
}

/**
 * Unified interpretations response from new endpoint
 */
export interface UnifiedInterpretationsResponse {
  planets: Record<string, InterpretationItem>;
  houses: Record<string, InterpretationItem>;
  aspects: Record<string, InterpretationItem>;
  arabic_parts: Record<string, InterpretationItem>;
  growth: Record<string, InterpretationItem>;
  metadata: InterpretationMetadata;
  language: string;
}

// Legacy type alias for backwards compatibility
export type RAGInterpretations = UnifiedInterpretationsResponse;
export type ChartInterpretations = UnifiedInterpretationsResponse;

export const interpretationsService = {
  /**
   * Get all interpretations (planets, houses, aspects, arabic_parts, growth) in a single call
   * @param chartId - Chart UUID
   * @param token - Auth token
   * @param language - Optional language code (e.g., 'pt-BR', 'en-US'). If not provided, uses user's profile language.
   */
  async getByChartId(
    chartId: string,
    token: string,
    language?: string
  ): Promise<UnifiedInterpretationsResponse> {
    const langParam = language ? `?lang=${language}` : '';
    return apiClient.get<UnifiedInterpretationsResponse>(
      `/api/v1/charts/${chartId}/interpretations${langParam}`,
      token
    );
  },

  /**
   * Regenerate specific interpretation types
   * @param chartId - Chart UUID
   * @param token - Auth token
   * @param types - Array of types to regenerate (e.g., ['planets', 'houses', 'growth'])
   */
  async regenerate(
    chartId: string,
    token: string,
    types?: string[]
  ): Promise<UnifiedInterpretationsResponse> {
    const regenerateParam = types && types.length > 0 ? `?regenerate=${types.join(',')}` : '';
    return apiClient.get<UnifiedInterpretationsResponse>(
      `/api/v1/charts/${chartId}/interpretations${regenerateParam}`,
      token
    );
  },
};
