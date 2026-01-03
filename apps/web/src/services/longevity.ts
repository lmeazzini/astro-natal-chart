/**
 * Longevity Analysis Service
 *
 * Provides API calls for the Longevity (Hyleg + Alcochoden) analysis feature.
 */

import { apiClient } from './api';
import type { LongevityData } from '../types/longevity';

/**
 * Get complete longevity analysis for a chart.
 *
 * This is a premium feature that consumes 3 credits (first calculation only).
 * Subsequent calls return cached results without consuming credits.
 *
 * @param chartId - The chart UUID
 * @returns Longevity analysis data
 * @throws Error if the request fails (402 for insufficient credits, 404 for not found)
 */
export async function getLongevityAnalysis(chartId: string): Promise<LongevityData> {
  return apiClient.get<LongevityData>(`/api/v1/charts/${chartId}/longevity`);
}

export default { getLongevityAnalysis };
