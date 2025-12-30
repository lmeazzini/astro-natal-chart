/**
 * SaturnReturnAnalysis - Saturn Return calculation and interpretation display.
 *
 * Shows Saturn Return timing, cycle progress, and interpretations.
 * This is a premium-only feature.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { getSignSymbol } from '@/utils/astro';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';
import {
  Clock,
  CalendarDays,
  ArrowRight,
  RotateCcw,
  Info,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { PremiumFeatureGate } from './PremiumFeatureGate';

import type {
  SaturnReturnAnalysis as SaturnReturnAnalysisType,
  SaturnReturnInterpretation,
  SaturnReturn,
  SaturnReturnPass,
} from '@/types/saturn_return';

interface SaturnReturnAnalysisProps {
  analysis: SaturnReturnAnalysisType | null;
  interpretation: SaturnReturnInterpretation | null;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

// ============================================================================
// Loading Skeleton Component
// ============================================================================

function SaturnReturnSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <Skeleton className="h-32 w-full" />

      {/* Progress skeleton */}
      <Skeleton className="h-24 w-full" />

      {/* Returns skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    </div>
  );
}

// ============================================================================
// Error Display Component
// ============================================================================

function SaturnReturnError({ error, onRetry }: { error: string; onRetry?: () => void }) {
  const { t } = useTranslation();

  return (
    <Card className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/20">
      <CardContent className="flex flex-col items-center justify-center py-12 space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold text-foreground">
            {t('astrology.saturnReturn.errorTitle', {
              defaultValue: 'Unable to load Saturn Return',
            })}
          </h3>
          <p className="text-sm text-muted-foreground max-w-md">{error}</p>
        </div>
        {onRetry && (
          <Button variant="outline" onClick={onRetry} className="mt-4">
            <RefreshCw className="h-4 w-4 mr-2" />
            {t('common.retry', { defaultValue: 'Try Again' })}
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Pass Display Component
// ============================================================================

function PassDisplay({ pass, locale }: { pass: SaturnReturnPass; locale: string }) {
  const date = new Date(pass.date);
  const formattedDate = date.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="flex items-center justify-between p-2 rounded-md bg-card/50 border border-border/50">
      <div className="flex items-center gap-2">
        <Badge
          variant="outline"
          className={`text-xs ${pass.is_retrograde ? 'bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20' : 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20'}`}
        >
          {pass.is_retrograde ? (
            <RotateCcw className="h-3 w-3 mr-1" />
          ) : (
            <ArrowRight className="h-3 w-3 mr-1" />
          )}
          {pass.pass_number}
        </Badge>
        <span className="text-sm">{formattedDate}</span>
      </div>
      <span className="text-xs text-muted-foreground">
        {pass.is_retrograde ? 'Retrograde' : 'Direct'}
      </span>
    </div>
  );
}

// ============================================================================
// Return Display Component
// ============================================================================

function ReturnDisplay({
  saturnReturn,
  locale,
  isCurrent = false,
  isFuture = false,
}: {
  saturnReturn: SaturnReturn;
  locale: string;
  isCurrent?: boolean;
  isFuture?: boolean;
}) {
  const { t } = useTranslation();

  const getReturnLabel = (num: number) => {
    switch (num) {
      case 1:
        return t('astrology.saturnReturn.firstReturn', { defaultValue: '1st Saturn Return' });
      case 2:
        return t('astrology.saturnReturn.secondReturn', { defaultValue: '2nd Saturn Return' });
      case 3:
        return t('astrology.saturnReturn.thirdReturn', { defaultValue: '3rd Saturn Return' });
      default:
        return `${num}th Saturn Return`;
    }
  };

  const cardClass = isCurrent
    ? 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20'
    : isFuture
      ? 'bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/20'
      : 'bg-gradient-to-br from-slate-500/10 to-gray-500/10 border-slate-500/20';

  return (
    <Card className={cardClass}>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CalendarDays className="h-5 w-5" />
            <span className="text-base">{getReturnLabel(saturnReturn.return_number)}</span>
          </div>
          {isCurrent && (
            <Badge className="bg-amber-500 text-white">
              {t('astrology.saturnReturn.current', { defaultValue: 'Current' })}
            </Badge>
          )}
          {isFuture && (
            <Badge variant="outline" className="border-blue-500 text-blue-600 dark:text-blue-400">
              {t('astrology.saturnReturn.upcoming', { defaultValue: 'Upcoming' })}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Age */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology.saturnReturn.ageAtReturn', { defaultValue: 'Age' })}
          </span>
          <span className="font-semibold">{saturnReturn.age_at_return.toFixed(1)}</span>
        </div>

        {/* Passes */}
        <div className="space-y-2">
          <span className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology.saturnReturn.passes', { defaultValue: 'Passes' })}
          </span>
          <div className="space-y-1">
            {saturnReturn.passes.map((pass, idx) => (
              <PassDisplay key={idx} pass={pass} locale={locale} />
            ))}
          </div>
        </div>

        {/* Duration */}
        <div className="text-xs text-muted-foreground">
          {t('astrology.saturnReturn.duration', { defaultValue: 'Duration' })}:{' '}
          {Math.round(
            (new Date(saturnReturn.end_date).getTime() -
              new Date(saturnReturn.start_date).getTime()) /
              (1000 * 60 * 60 * 24)
          )}{' '}
          {t('astrology.saturnReturn.days', { defaultValue: 'days' })}
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Interpretation Display Component
// ============================================================================

function InterpretationDisplay({ interpretation }: { interpretation: SaturnReturnInterpretation }) {
  const { t } = useTranslation();
  const { translateSign } = useAstroTranslation();

  return (
    <Card className="bg-gradient-to-br from-purple-500/10 to-violet-500/10 border-purple-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-3">
          <Info className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          <span>
            {t('astrology.saturnReturn.interpretation', { defaultValue: 'Interpretation' })}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* General Introduction */}
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {interpretation.general_introduction}
          </p>
        </div>

        <Separator />

        {/* General Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology.saturnReturn.generalMeaning', { defaultValue: 'General Meaning' })}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.general_interpretation}</p>
        </div>

        <Separator />

        {/* Sign Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology.saturnReturn.inSign', { defaultValue: 'Saturn in' })}{' '}
            {getSignSymbol(interpretation.natal_saturn_sign)}{' '}
            {translateSign(interpretation.natal_saturn_sign)}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.sign_interpretation}</p>
        </div>

        <Separator />

        {/* House Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology.saturnReturn.inHouse', { defaultValue: 'Saturn in House' })}{' '}
            {interpretation.natal_saturn_house}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.house_interpretation}</p>
        </div>

        {/* Phase Interpretation */}
        {interpretation.current_phase_interpretation && (
          <>
            <Separator />
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                {t('astrology.saturnReturn.currentPhase', { defaultValue: 'Current Phase' })}
              </p>
              <p className="text-sm leading-relaxed">
                {interpretation.current_phase_interpretation}
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main SaturnReturnAnalysis Component
// ============================================================================

export function SaturnReturnAnalysis({
  analysis,
  interpretation,
  isLoading = false,
  error = null,
  onRetry,
}: SaturnReturnAnalysisProps) {
  const { t, i18n } = useTranslation();
  const { translateSign } = useAstroTranslation();
  const locale = i18n.language;

  // Show loading skeleton
  if (isLoading) {
    return (
      <PremiumFeatureGate feature="saturn-return">
        <SaturnReturnSkeleton />
      </PremiumFeatureGate>
    );
  }

  // Show error state
  if (error) {
    return (
      <PremiumFeatureGate feature="saturn-return">
        <SaturnReturnError error={error} onRetry={onRetry} />
      </PremiumFeatureGate>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          {t('astrology.saturnReturn.noData', {
            defaultValue: 'Saturn Return data not available for this chart.',
          })}
        </p>
      </div>
    );
  }

  return (
    <PremiumFeatureGate feature="saturn-return">
      <div className="space-y-6">
        {/* Natal Saturn Info Card */}
        <Card className="bg-gradient-to-br from-yellow-500/10 to-amber-500/10 border-yellow-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-3">
              <span className="text-3xl">♄</span>
              <div className="flex-1">
                <div className="text-lg font-semibold text-foreground">
                  {t('astrology.saturnReturn.title', { defaultValue: 'Saturn Return' })}
                </div>
                <div className="text-xs text-muted-foreground font-normal mt-1">
                  {t('astrology.saturnReturn.subtitle', {
                    defaultValue: 'Major life transit occurring every ~29.5 years',
                  })}
                </div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Natal Saturn Position */}
            <div className="flex items-center gap-4">
              <div className="flex-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  {t('astrology.saturnReturn.natalSaturn', { defaultValue: 'Natal Saturn' })}
                </p>
                <p className="text-xl font-bold text-foreground">
                  {getSignSymbol(analysis.natal_saturn_sign)}{' '}
                  {translateSign(analysis.natal_saturn_sign)}{' '}
                  {analysis.natal_saturn_degree.toFixed(1)}°
                </p>
                <p className="text-sm text-muted-foreground">
                  {t('astrology.saturnReturn.house', { defaultValue: 'House' })}{' '}
                  {analysis.natal_saturn_house}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  {t('astrology.saturnReturn.currentSaturn', { defaultValue: 'Current Saturn' })}
                </p>
                <p className="text-lg font-semibold">
                  {getSignSymbol(analysis.current_saturn_sign)}{' '}
                  {translateSign(analysis.current_saturn_sign)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cycle Progress */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-3">
              <Clock className="h-5 w-5" />
              <span>
                {t('astrology.saturnReturn.cycleProgress', { defaultValue: 'Cycle Progress' })}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">
                  {t('astrology.saturnReturn.throughCycle', {
                    defaultValue: 'Through current cycle',
                  })}
                </span>
                <span className="font-semibold">{analysis.cycle_progress_percent.toFixed(1)}%</span>
              </div>
              <Progress value={analysis.cycle_progress_percent} className="h-3" />
            </div>

            {analysis.days_until_next_return && (
              <div className="flex items-center justify-between p-3 rounded-md bg-muted/50">
                <span className="text-sm text-muted-foreground">
                  {t('astrology.saturnReturn.daysUntilNext', {
                    defaultValue: 'Days until next return',
                  })}
                </span>
                <span className="font-semibold">
                  {analysis.days_until_next_return.toLocaleString(locale)}
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Saturn Returns Grid */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            {t('astrology.saturnReturn.returns', { defaultValue: 'Saturn Returns' })}
          </h3>
          <div className="grid md:grid-cols-2 gap-4">
            {/* Current Return */}
            {analysis.current_return && (
              <ReturnDisplay
                saturnReturn={analysis.current_return}
                locale={locale}
                isCurrent={true}
              />
            )}

            {/* Next Return */}
            {analysis.next_return && (
              <ReturnDisplay saturnReturn={analysis.next_return} locale={locale} isFuture={true} />
            )}

            {/* Past Returns */}
            {analysis.past_returns.map((sr, idx) => (
              <ReturnDisplay key={idx} saturnReturn={sr} locale={locale} />
            ))}
          </div>
        </div>

        {/* Interpretation */}
        {interpretation && <InterpretationDisplay interpretation={interpretation} />}
      </div>
    </PremiumFeatureGate>
  );
}
