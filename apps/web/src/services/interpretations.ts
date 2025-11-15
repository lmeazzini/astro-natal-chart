/**
 * Chart interpretations service for AI-generated interpretations
 */

import { apiClient } from './api';

export interface ChartInterpretations {
  planets: Record<string, string>;
  houses: Record<string, string>;
  aspects: Record<string, string>;
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
};
