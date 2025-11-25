/**
 * PremiumUpsell - Component to encourage free users to upgrade to Premium.
 *
 * Displayed when a free user tries to access a premium-only feature.
 * Links to the /pricing page for subscription options.
 */

import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Crown, Sparkles, ArrowRight } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface PremiumUpsellProps {
  /** Feature name to display (e.g., "horary", "profections") */
  feature?: string;
  /** Custom title override */
  title?: string;
  /** Custom description override */
  description?: string;
  /** Whether to use compact layout */
  compact?: boolean;
}

/**
 * Displays an upsell message encouraging users to upgrade to Premium.
 *
 * @example
 * ```tsx
 * // Basic usage
 * <PremiumUpsell feature="horary" />
 *
 * // Compact inline usage
 * <PremiumUpsell feature="profections" compact />
 *
 * // Custom message
 * <PremiumUpsell
 *   title="Unlock Advanced Features"
 *   description="Get access to all premium features"
 * />
 * ```
 */
export function PremiumUpsell({
  feature,
  title,
  description,
  compact = false,
}: PremiumUpsellProps) {
  const { t } = useTranslation();

  // Resolve display text
  const displayTitle =
    title ??
    (feature
      ? t('premium.featureLockedTitle', {
          feature: t(`premium.features.${feature}`, { defaultValue: feature }),
          defaultValue: '{{feature}} is a Premium Feature',
        })
      : t('premium.upgradeToPremium', { defaultValue: 'Upgrade to Premium' }));

  const displayDescription =
    description ??
    (feature
      ? t('premium.featureLockedDescription', {
          feature: t(`premium.features.${feature}`, { defaultValue: feature }),
          defaultValue:
            'This feature is exclusive to Premium subscribers. Upgrade your plan to unlock {{feature}} and other advanced features.',
        })
      : t('premium.genericDescription', {
          defaultValue:
            'Get access to advanced astrology features like horary, profections, firdaria, and more!',
        }));

  if (compact) {
    return (
      <div className="flex items-center gap-3 p-3 rounded-lg bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950 dark:to-yellow-950 border border-amber-200 dark:border-amber-800">
        <Crown className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-amber-800 dark:text-amber-200 truncate">
            {displayTitle}
          </p>
        </div>
        <Button
          asChild
          size="sm"
          variant="outline"
          className="flex-shrink-0 border-amber-300 dark:border-amber-700 text-amber-700 dark:text-amber-300 hover:bg-amber-100 dark:hover:bg-amber-900"
        >
          <Link to="/pricing">{t('premium.upgrade', { defaultValue: 'Upgrade' })}</Link>
        </Button>
      </div>
    );
  }

  return (
    <Alert className="border-amber-300 dark:border-amber-700 bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950 dark:to-yellow-950">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-full bg-amber-100 dark:bg-amber-900">
          <Crown className="h-5 w-5 text-amber-600 dark:text-amber-400" />
        </div>
        <div className="flex-1">
          <AlertTitle className="flex items-center gap-2 text-amber-800 dark:text-amber-200 mb-1">
            <Sparkles className="h-4 w-4" />
            {displayTitle}
          </AlertTitle>
          <AlertDescription className="text-amber-700 dark:text-amber-300">
            <p className="mb-4">{displayDescription}</p>
            <Button
              asChild
              className="bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white shadow-md"
            >
              <Link to="/pricing" className="inline-flex items-center gap-2">
                {t('premium.viewPlans', { defaultValue: 'View Plans' })}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
}
