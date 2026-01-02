/**
 * Stripe payment service
 */

import { apiClient } from './api';

export interface StripeConfig {
  publishable_key: string;
  enabled: boolean;
  plans: {
    [key: string]: {
      name: string;
      price_id: string | null;
      credits: number | null;
      price_brl: number;
    };
  };
}

export interface CheckoutSessionResponse {
  session_id: string;
  checkout_url: string;
}

export interface PortalSessionResponse {
  portal_url: string;
}

export interface SubscriptionStatus {
  has_subscription: boolean;
  plan_type: string;
  status: string | null;
  stripe_subscription_id: string | null;
  current_period_start: string | null;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  days_until_renewal: number | null;
}

export interface CancelSubscriptionResponse {
  success: boolean;
  message: string;
  cancel_at_period_end: boolean;
  current_period_end: string | null;
}

export interface PaymentRecord {
  id: string;
  amount: number;
  currency: string;
  status: string;
  receipt_url: string | null;
  description: string | null;
  created_at: string;
}

export interface PaymentHistoryResponse {
  payments: PaymentRecord[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

/**
 * Get Stripe configuration (public key, plans)
 */
export async function getStripeConfig(): Promise<StripeConfig> {
  return apiClient.get<StripeConfig>('/api/v1/stripe/config');
}

/**
 * Create a checkout session for a plan
 */
export async function createCheckoutSession(
  planType: 'starter' | 'pro' | 'unlimited',
  successUrl?: string,
  cancelUrl?: string
): Promise<CheckoutSessionResponse> {
  return apiClient.post<CheckoutSessionResponse>('/api/v1/stripe/create-checkout-session', {
    plan_type: planType,
    success_url: successUrl,
    cancel_url: cancelUrl,
  });
}

/**
 * Create a customer portal session
 */
export async function createPortalSession(returnUrl?: string): Promise<PortalSessionResponse> {
  return apiClient.post<PortalSessionResponse>('/api/v1/stripe/create-portal-session', {
    return_url: returnUrl,
  });
}

/**
 * Get current subscription status
 */
export async function getSubscriptionStatus(): Promise<SubscriptionStatus> {
  return apiClient.get<SubscriptionStatus>('/api/v1/stripe/subscription-status');
}

/**
 * Cancel subscription
 */
export async function cancelSubscription(
  atPeriodEnd: boolean = true
): Promise<CancelSubscriptionResponse> {
  return apiClient.post<CancelSubscriptionResponse>('/api/v1/stripe/cancel-subscription', {
    at_period_end: atPeriodEnd,
  });
}

/**
 * Reactivate a cancelled subscription
 */
export async function reactivateSubscription(): Promise<CancelSubscriptionResponse> {
  return apiClient.post<CancelSubscriptionResponse>('/api/v1/stripe/reactivate-subscription');
}

/**
 * Get payment history
 */
export async function getPaymentHistory(
  page: number = 1,
  pageSize: number = 20
): Promise<PaymentHistoryResponse> {
  return apiClient.get<PaymentHistoryResponse>(
    `/api/v1/stripe/payment-history?page=${page}&page_size=${pageSize}`
  );
}

/**
 * Format price in BRL
 */
export function formatPriceBRL(cents: number): string {
  return `R$ ${(cents / 100).toFixed(2).replace('.', ',')}`;
}

/**
 * Redirect to checkout
 */
export async function redirectToCheckout(planType: 'starter' | 'pro' | 'unlimited'): Promise<void> {
  const { checkout_url } = await createCheckoutSession(planType);
  window.location.href = checkout_url;
}

/**
 * Redirect to customer portal
 */
export async function redirectToPortal(): Promise<void> {
  const { portal_url } = await createPortalSession();
  window.location.href = portal_url;
}
