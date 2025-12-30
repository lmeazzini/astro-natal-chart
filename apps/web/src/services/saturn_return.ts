/**
 * Saturn Return API service.
 */

import { apiClient } from './api';
import type { SaturnReturnAnalysis, SaturnReturnInterpretation } from '@/types/saturn_return';

/**
 * Get Saturn Return analysis for a chart.
 * Premium feature - requires premium or admin access.
 */
export async function getSaturnReturn(chartId: string): Promise<SaturnReturnAnalysis> {
  return apiClient.get<SaturnReturnAnalysis>(`/api/v1/charts/${chartId}/saturn-return`);
}

/**
 * Get Saturn Return interpretation for a chart.
 * Premium feature - requires premium or admin access.
 */
export async function getSaturnReturnInterpretation(
  chartId: string
): Promise<SaturnReturnInterpretation> {
  return apiClient.get<SaturnReturnInterpretation>(
    `/api/v1/charts/${chartId}/saturn-return/interpretation`
  );
}
