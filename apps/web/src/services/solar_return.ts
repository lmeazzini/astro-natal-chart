/**
 * Solar Return API service.
 */

import { apiClient } from './api';
import type {
  SolarReturnResponse,
  SolarReturnInterpretation,
  SolarReturnListResponse,
} from '@/types/solar_return';

export interface SolarReturnOptions {
  year?: number;
  lat?: number;
  lon?: number;
  city?: string;
  country?: string;
}

/**
 * Get Solar Return chart for a specific year.
 * Premium feature - requires premium or admin access.
 */
export async function getSolarReturn(
  chartId: string,
  options?: SolarReturnOptions
): Promise<SolarReturnResponse> {
  const params = new URLSearchParams();
  if (options?.year) params.append('year', options.year.toString());
  if (options?.lat) params.append('lat', options.lat.toString());
  if (options?.lon) params.append('lon', options.lon.toString());
  if (options?.city) params.append('city', options.city);
  if (options?.country) params.append('country', options.country);

  const queryString = params.toString();
  const url = `/api/v1/charts/${chartId}/solar-return${queryString ? `?${queryString}` : ''}`;

  return apiClient.get<SolarReturnResponse>(url);
}

/**
 * Get Solar Return charts for multiple years.
 * Premium feature - requires premium or admin access.
 */
export async function getSolarReturns(
  chartId: string,
  startYear: number,
  endYear: number,
  options?: { lat?: number; lon?: number }
): Promise<SolarReturnListResponse> {
  const params = new URLSearchParams();
  params.append('start_year', startYear.toString());
  params.append('end_year', endYear.toString());
  if (options?.lat) params.append('lat', options.lat.toString());
  if (options?.lon) params.append('lon', options.lon.toString());

  return apiClient.get<SolarReturnListResponse>(
    `/api/v1/charts/${chartId}/solar-returns?${params.toString()}`
  );
}

/**
 * Get Solar Return interpretation.
 * Premium feature - requires premium or admin access.
 */
export async function getSolarReturnInterpretation(
  chartId: string,
  options?: SolarReturnOptions
): Promise<SolarReturnInterpretation> {
  const params = new URLSearchParams();
  if (options?.year) params.append('year', options.year.toString());
  if (options?.lat) params.append('lat', options.lat.toString());
  if (options?.lon) params.append('lon', options.lon.toString());

  const queryString = params.toString();
  const url = `/api/v1/charts/${chartId}/solar-return/interpretation${queryString ? `?${queryString}` : ''}`;

  return apiClient.get<SolarReturnInterpretation>(url);
}
