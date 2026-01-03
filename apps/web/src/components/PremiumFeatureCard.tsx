/**
 * Premium Feature Card Component
 *
 * Displays a card prompting users to generate premium features that consume credits.
 * Shows credit cost and handles generation with loading/error states.
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Loader2, Sparkles, AlertCircle, Coins } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useCredits } from '@/contexts/CreditsContext';
import { InsufficientCreditsModal } from '@/components/InsufficientCreditsModal';

export type FeatureType = 'growth' | 'longevity' | 'saturn_return' | 'solar_return';

interface PremiumFeatureCardProps {
  feature: FeatureType;
  title: string;
  description: string;
  credits: number;
  icon?: React.ReactNode;
  onGenerate: () => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
  onClearError?: () => void;
}

export function PremiumFeatureCard({
  feature,
  title,
  description,
  credits,
  icon,
  onGenerate,
  isLoading = false,
  error = null,
  onClearError,
}: PremiumFeatureCardProps) {
  const { t } = useTranslation();
  const { credits: creditsData, refreshCredits, hasCredits } = useCredits();
  const [showInsufficientModal, setShowInsufficientModal] = useState(false);
  const [internalLoading, setInternalLoading] = useState(false);
  const [internalError, setInternalError] = useState<string | null>(null);

  const loading = isLoading || internalLoading;
  const displayError = error || internalError;
  const userCreditsBalance = creditsData?.credits_balance ?? null;
  const isUnlimited = creditsData?.is_unlimited ?? false;

  const handleGenerate = async () => {
    // Check if user has enough credits (skip if unlimited)
    if (!isUnlimited && !hasCredits(credits)) {
      setShowInsufficientModal(true);
      return;
    }

    setInternalError(null);
    setInternalLoading(true);

    try {
      await onGenerate();
      // Refresh credits after successful generation
      await refreshCredits();
    } catch (err) {
      console.error(`Error generating ${feature}:`, err);
      if (err instanceof Error) {
        // Check for 402 (insufficient credits)
        if (err.message.includes('402')) {
          setShowInsufficientModal(true);
        } else if (err.message.includes('403')) {
          setInternalError(
            t('premiumFeature.errors.unauthorized', 'You do not have access to this feature.')
          );
        } else if (err.message.includes('404')) {
          setInternalError(t('premiumFeature.errors.notFound', 'Chart not found.'));
        } else {
          setInternalError(err.message);
        }
      } else {
        setInternalError(t('premiumFeature.errors.network', 'Network error. Please try again.'));
      }
    } finally {
      setInternalLoading(false);
    }
  };

  const clearError = () => {
    setInternalError(null);
    onClearError?.();
  };

  return (
    <>
      <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="text-h3 font-display flex items-center gap-2">
            {icon || <Sparkles className="h-6 w-6 text-primary" />}
            {title}
          </CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Credit cost info */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Coins className="h-4 w-4" />
            <span>
              {t('premiumFeature.creditCost', '{{count}} credits required', { count: credits })}
            </span>
            {userCreditsBalance !== null && (
              <span className="ml-auto">
                {isUnlimited
                  ? t('premiumFeature.unlimited', 'Unlimited')
                  : t('premiumFeature.yourCredits', 'You have: {{count}}', {
                      count: userCreditsBalance,
                    })}
              </span>
            )}
          </div>

          {/* Error display */}
          {displayError && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="flex items-center justify-between">
                <span>{displayError}</span>
                <Button variant="ghost" size="sm" onClick={clearError}>
                  {t('common.dismiss', 'Dismiss')}
                </Button>
              </AlertDescription>
            </Alert>
          )}

          {/* Generate button */}
          <Button
            onClick={handleGenerate}
            disabled={loading}
            className="w-full sm:w-auto"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t('premiumFeature.generating', 'Generating...')}
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                {t('premiumFeature.generate', 'Generate Analysis')}
              </>
            )}
          </Button>

          {/* Loading message */}
          {loading && (
            <p className="text-xs text-muted-foreground">
              {t('premiumFeature.generatingTime', 'This may take a few seconds...')}
            </p>
          )}

          {/* Link to pricing */}
          {!isUnlimited && userCreditsBalance !== null && userCreditsBalance < credits && (
            <p className="text-sm text-muted-foreground">
              {t('premiumFeature.needMoreCredits', 'Need more credits?')}{' '}
              <Link to="/pricing" className="text-primary hover:underline">
                {t('premiumFeature.upgradePlan', 'Upgrade your plan')}
              </Link>
            </p>
          )}
        </CardContent>
      </Card>

      {/* Insufficient Credits Modal */}
      <InsufficientCreditsModal
        isOpen={showInsufficientModal}
        onClose={() => setShowInsufficientModal(false)}
        featureType={feature}
        requiredCredits={credits}
        availableCredits={userCreditsBalance ?? 0}
      />
    </>
  );
}

export default PremiumFeatureCard;
