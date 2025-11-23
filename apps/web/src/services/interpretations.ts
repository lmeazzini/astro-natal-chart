/**
 * Chart interpretations service for AI-generated interpretations
 */

import { apiClient } from './api';

export interface ChartInterpretations {
  planets: Record<string, string>;
  houses: Record<string, string>;
  aspects: Record<string, string>;
  source?: 'standard' | 'rag';
}

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
 * RAG-enhanced interpretations response (admin only)
 */
export interface RAGInterpretations {
  planets: Record<string, InterpretationItem>;
  houses: Record<string, InterpretationItem>;
  aspects: Record<string, InterpretationItem>;
  source: 'rag';
  documents_used: number;
}

export const interpretationsService = {
  /**
   * Get all interpretations for a birth chart
   */
  async getByChartId(chartId: string, token: string): Promise<ChartInterpretations> {
    return apiClient.get<ChartInterpretations>(
      `/api/v1/charts/${chartId}/interpretations`,
      token
    );
  },

  /**
   * Regenerate interpretations for a birth chart
   */
  async regenerate(chartId: string, token: string): Promise<ChartInterpretations> {
    return apiClient.post<ChartInterpretations>(
      `/api/v1/charts/${chartId}/interpretations/regenerate`,
      {},
      token
    );
  },

  /**
   * Get RAG-enhanced interpretations for a birth chart (admin only)
   * This endpoint is only available to admin users for A/B testing
   */
  async getRAGByChartId(chartId: string, token: string): Promise<RAGInterpretations> {
    return apiClient.get<RAGInterpretations>(
      `/api/v1/charts/${chartId}/interpretations/rag`,
      token
    );
  },

  /**
   * Regenerate RAG-enhanced interpretations for a birth chart (admin only)
   * Forces regeneration bypassing cache
   */
  async regenerateRAG(chartId: string, token: string): Promise<RAGInterpretations> {
    return apiClient.post<RAGInterpretations>(
      `/api/v1/charts/${chartId}/interpretations/rag/regenerate`,
      {},
      token
    );
  },
};
