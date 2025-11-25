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
 * Single interpretation item with RAG metadata
 */
export interface InterpretationItem {
  content: string;
  source: 'standard' | 'rag';
  rag_sources: RAGSourceInfo[];
}

/**
 * RAG-enhanced interpretations response
 */
export interface RAGInterpretations {
  planets: Record<string, InterpretationItem>;
  houses: Record<string, InterpretationItem>;
  aspects: Record<string, InterpretationItem>;
  arabic_parts?: Record<string, InterpretationItem>;
  source: 'rag';
  documents_used: number;
  /** Language code of the interpretations (e.g., 'pt-BR' or 'en-US') */
  language: string;
}

// Legacy type alias for backwards compatibility
export type ChartInterpretations = RAGInterpretations;

export const interpretationsService = {
  /**
   * Get all RAG-enhanced interpretations for a birth chart
   */
  async getByChartId(chartId: string, token: string): Promise<RAGInterpretations> {
    return apiClient.get<RAGInterpretations>(`/api/v1/charts/${chartId}/interpretations`, token);
  },

  /**
   * Regenerate RAG-enhanced interpretations for a birth chart
   */
  async regenerate(chartId: string, token: string): Promise<RAGInterpretations> {
    return apiClient.post<RAGInterpretations>(
      `/api/v1/charts/${chartId}/interpretations/regenerate`,
      {},
      token
    );
  },
};
