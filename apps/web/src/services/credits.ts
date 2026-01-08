/**
 * Credits service for managing user credit balance and history
 */

import { apiClient } from './api';

// Response types
export interface UserCreditsResponse {
  plan_type: string;
  credits_balance: number;
  credits_limit: number | null;
  credits_used: number;
  usage_percentage: number;
  is_unlimited: boolean;
  purchased_credits: number;
  period_start: string;
  period_end: string | null;
  days_until_reset: number | null;
}

export interface CreditTransaction {
  id: string;
  transaction_type: 'debit' | 'credit' | 'reset' | 'upgrade' | 'bonus' | 'purchase';
  amount: number;
  balance_after: number;
  feature_type: string | null;
  resource_id: string | null;
  description: string | null;
  created_at: string;
}

export interface CreditHistoryResponse {
  transactions: CreditTransaction[];
  total: number;
  skip: number;
  limit: number;
}

export interface CreditUsageResponse {
  usage_by_feature: Record<string, number>;
  total_used: number;
  period_start: string;
  period_end: string | null;
}

export interface CreditCostInfo {
  feature_type: string;
  cost: number;
}

export interface CreditsInfoResponse {
  plans: Record<string, number | null>;
  feature_costs: CreditCostInfo[];
}

export interface UnlockedFeaturesResponse {
  unlocked_features: string[];
  unlocked_solar_return_years: number[];
}

// Error type for insufficient credits
export interface InsufficientCreditsError {
  error: 'insufficient_credits';
  message: string;
  feature_type: string;
  required_credits: number;
  available_credits: number;
  feature_cost: number;
}

/**
 * Get current user's credit balance
 */
export async function getCredits(): Promise<UserCreditsResponse> {
  return apiClient.get<UserCreditsResponse>('/api/v1/credits');
}

/**
 * Get credit transaction history
 */
export async function getCreditHistory(skip = 0, limit = 50): Promise<CreditHistoryResponse> {
  return apiClient.get<CreditHistoryResponse>(
    `/api/v1/credits/history?skip=${skip}&limit=${limit}`
  );
}

/**
 * Get credit usage breakdown by feature
 */
export async function getCreditUsage(): Promise<CreditUsageResponse> {
  return apiClient.get<CreditUsageResponse>('/api/v1/credits/usage');
}

/**
 * Get public information about credit costs and plans
 */
export async function getCreditsInfo(): Promise<CreditsInfoResponse> {
  return apiClient.get<CreditsInfoResponse>('/api/v1/credits/info');
}

/**
 * Get unlocked features for a specific chart
 *
 * Returns the list of premium features that have been paid for on this chart,
 * and the specific years of Solar Return that have been unlocked.
 */
export async function getUnlockedFeatures(chartId: string): Promise<UnlockedFeaturesResponse> {
  return apiClient.get<UnlockedFeaturesResponse>(
    `/api/v1/credits/charts/${chartId}/unlocked-features`
  );
}

/**
 * Check if a response is an insufficient credits error
 */
export function isInsufficientCreditsError(
  error: unknown
): error is { detail: InsufficientCreditsError } {
  if (
    error &&
    typeof error === 'object' &&
    'detail' in error &&
    error.detail &&
    typeof error.detail === 'object' &&
    'error' in error.detail
  ) {
    return (error.detail as { error: string }).error === 'insufficient_credits';
  }
  return false;
}

/**
 * Format credits display string
 */
export function formatCredits(credits: UserCreditsResponse): string {
  if (credits.is_unlimited) {
    return 'Unlimited';
  }
  return `${credits.credits_balance}/${credits.credits_limit}`;
}

/**
 * Get plan display name
 */
export function getPlanDisplayName(planType: string): string {
  const names: Record<string, string> = {
    free: 'Free',
    starter: 'Starter',
    pro: 'Pro',
    unlimited: 'Unlimited',
  };
  return names[planType] || planType;
}
