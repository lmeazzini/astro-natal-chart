/**
 * PremiumFeatureGate - Conditional render wrapper for premium-only features.
 *
 * Shows children for premium/admin users, or shows a fallback component
 * (default: PremiumUpsell) for free users.
 */

import { ReactNode } from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { PremiumUpsell } from './PremiumUpsell';

interface PremiumFeatureGateProps {
  /** Content to show for premium/admin users */
  children: ReactNode;
  /** Optional custom fallback for free users (default: PremiumUpsell) */
  fallback?: ReactNode;
  /** Feature name to display in the upsell (e.g., "horary", "profections") */
  feature?: string;
}

/**
 * Conditionally renders content based on user's premium status.
 *
 * @example
 * ```tsx
 * <PremiumFeatureGate feature="horary">
 *   <HorarySection />
 * </PremiumFeatureGate>
 * ```
 */
export function PremiumFeatureGate({
  children,
  fallback,
  feature,
}: PremiumFeatureGateProps) {
  const { isPremium } = usePermissions();

  if (isPremium) {
    return <>{children}</>;
  }

  // Show custom fallback or default PremiumUpsell
  return <>{fallback ?? <PremiumUpsell feature={feature} />}</>;
}
