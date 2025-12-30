/**
 * SolarReturnAnalysis - Solar Return chart calculation and interpretation display.
 *
 * Shows the Solar Return chart for a specific year, including:
 * - SR Ascendant and Sun house
 * - Comparison to natal chart
 * - Key aspects between SR and natal
 * - Interpretations
 *
 * This is a premium-only feature.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { getSignSymbol, getAspectSymbol, getPlanetSymbol } from '@/utils/astro';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';
import {
  Sun,
  Calendar,
  MapPin,
  Home,
  ArrowLeftRight,
  Info,
  AlertCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { PremiumFeatureGate } from './PremiumFeatureGate';

import type {
  SolarReturnResponse,
  SolarReturnInterpretation,
  SRToNatalAspect,
} from '@/types/solar_return';

interface SolarReturnAnalysisProps {
  solarReturn: SolarReturnResponse | null;
  interpretation: SolarReturnInterpretation | null;
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
  onYearChange?: (year: number) => void;
  currentYear?: number;
}

// ============================================================================
// Loading Skeleton Component
// ============================================================================

export function SolarReturnSkeleton() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <Skeleton className="h-40 w-full" />

      {/* Chart info skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>

      {/* Comparison skeleton */}
      <Skeleton className="h-64 w-full" />
    </div>
  );
}

// ============================================================================
// Error Display Component
// ============================================================================

function SolarReturnError({ error, onRetry }: { error: string; onRetry?: () => void }) {
  const { t } = useTranslation();

  return (
    <Card className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border-red-500/20">
      <CardContent className="flex flex-col items-center justify-center py-12 space-y-4">
        <AlertCircle className="h-12 w-12 text-red-500" />
        <div className="text-center space-y-2">
          <h3 className="text-lg font-semibold text-foreground">
            {t('astrology:solarReturn.errorTitle', {
              defaultValue: 'Unable to load Solar Return',
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
// Year Navigator Component
// ============================================================================

function YearNavigator({
  currentYear,
  onYearChange,
}: {
  currentYear: number;
  onYearChange?: (year: number) => void;
}) {
  const { t } = useTranslation();

  return (
    <div className="flex items-center justify-center gap-4 p-4 bg-muted/30 rounded-lg">
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onYearChange?.(currentYear - 1)}
        aria-label={t('common.previousYear', { defaultValue: 'Previous year' })}
      >
        <ChevronLeft className="h-5 w-5" />
      </Button>
      <span className="text-xl font-bold min-w-[80px] text-center">{currentYear}</span>
      <Button
        variant="ghost"
        size="icon"
        onClick={() => onYearChange?.(currentYear + 1)}
        aria-label={t('common.nextYear', { defaultValue: 'Next year' })}
      >
        <ChevronRight className="h-5 w-5" />
      </Button>
    </div>
  );
}

// ============================================================================
// SR to Natal Aspect Display
// ============================================================================

function AspectDisplay({ aspect }: { aspect: SRToNatalAspect }) {
  const { translateAspect } = useAstroTranslation();

  return (
    <div
      className={`flex items-center justify-between p-2 rounded-md ${
        aspect.is_major
          ? 'bg-primary/5 border border-primary/10'
          : 'bg-muted/30 border border-border/50'
      }`}
    >
      <div className="flex items-center gap-2">
        <span className="text-lg">{getPlanetSymbol(aspect.sr_planet)}</span>
        <span className="text-xs text-muted-foreground">SR</span>
        <span className="text-lg">{getAspectSymbol(aspect.aspect)}</span>
        <span className="text-lg">{getPlanetSymbol(aspect.natal_planet)}</span>
        <span className="text-xs text-muted-foreground">Natal</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-sm">{translateAspect(aspect.aspect)}</span>
        <Badge variant="outline" className="text-xs">
          {aspect.orb.toFixed(1)}°
        </Badge>
      </div>
    </div>
  );
}

// ============================================================================
// Planets in Houses Display
// ============================================================================

function PlanetsInHousesDisplay({
  title,
  planetsInHouses,
}: {
  title: string;
  planetsInHouses: Record<string, number>;
}) {
  const { translatePlanet } = useAstroTranslation();
  const { t } = useTranslation();

  const entries = Object.entries(planetsInHouses);
  if (entries.length === 0) return null;

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        {title}
      </h4>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {entries.map(([planet, house]) => (
          <div
            key={planet}
            className="flex items-center gap-2 p-2 rounded-md bg-muted/30 border border-border/50"
          >
            <span className="text-lg">{getPlanetSymbol(planet)}</span>
            <span className="text-sm">{translatePlanet(planet)}</span>
            <span className="text-xs text-muted-foreground ml-auto">
              {t('astrology:houses.house', { defaultValue: 'House' })} {house}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Interpretation Display Component
// ============================================================================

function InterpretationDisplay({ interpretation }: { interpretation: SolarReturnInterpretation }) {
  const { t } = useTranslation();
  const { translateSign } = useAstroTranslation();

  return (
    <Card className="bg-gradient-to-br from-purple-500/10 to-violet-500/10 border-purple-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-3">
          <Info className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          <span>
            {t('astrology:solarReturn.interpretation', { defaultValue: 'Interpretation' })}
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
            {t('astrology:solarReturn.yearlyThemes', { defaultValue: 'Yearly Themes' })}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.general_interpretation}</p>
        </div>

        <Separator />

        {/* Ascendant Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology:solarReturn.srAscendant', { defaultValue: 'SR Ascendant' })}{' '}
            {getSignSymbol(interpretation.sr_ascendant_sign)}{' '}
            {translateSign(interpretation.sr_ascendant_sign)}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.ascendant_interpretation}</p>
        </div>

        <Separator />

        {/* Sun House Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('astrology:solarReturn.srSunHouse', { defaultValue: 'SR Sun in House' })}{' '}
            {interpretation.sr_sun_house}
          </p>
          <p className="text-sm leading-relaxed">{interpretation.sun_house_interpretation}</p>
        </div>
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main SolarReturnAnalysis Component
// ============================================================================

export function SolarReturnAnalysis({
  solarReturn,
  interpretation,
  isLoading = false,
  error = null,
  onRetry,
  onYearChange,
  currentYear,
}: SolarReturnAnalysisProps) {
  const { t, i18n } = useTranslation();
  const { translateSign } = useAstroTranslation();
  const locale = i18n.language;

  // Show loading skeleton
  if (isLoading) {
    return (
      <PremiumFeatureGate feature="solar-return">
        <SolarReturnSkeleton />
      </PremiumFeatureGate>
    );
  }

  // Show error state
  if (error) {
    return (
      <PremiumFeatureGate feature="solar-return">
        <SolarReturnError error={error} onRetry={onRetry} />
      </PremiumFeatureGate>
    );
  }

  if (!solarReturn) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          {t('astrology:solarReturn.noData', {
            defaultValue: 'Solar Return data not available for this chart.',
          })}
        </p>
      </div>
    );
  }

  const { chart, comparison } = solarReturn;
  const returnDate = new Date(chart.return_datetime);
  const formattedReturnDate = returnDate.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <PremiumFeatureGate feature="solar-return">
      <div className="space-y-6">
        {/* Year Navigator */}
        {onYearChange && currentYear && (
          <YearNavigator currentYear={currentYear} onYearChange={onYearChange} />
        )}

        {/* Header Card - SR Overview */}
        <Card className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/20">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-3">
              <Sun className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
              <div className="flex-1">
                <div className="text-lg font-semibold text-foreground">
                  {t('astrology:solarReturn.title', { defaultValue: 'Solar Return' })}{' '}
                  {chart.return_year}
                </div>
                <div className="text-xs text-muted-foreground font-normal mt-1">
                  {t('astrology:solarReturn.subtitle', {
                    defaultValue: 'Annual chart for your Sun return',
                  })}
                </div>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Return Date & Location */}
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t('astrology:solarReturn.returnDate', { defaultValue: 'Return Date' })}
                  </p>
                  <p className="font-semibold">{formattedReturnDate}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <MapPin className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t('astrology:solarReturn.location', { defaultValue: 'Location' })}
                  </p>
                  <p className="font-semibold">
                    {chart.location.city
                      ? `${chart.location.city}, ${chart.location.country}`
                      : `${chart.location.latitude.toFixed(2)}°, ${chart.location.longitude.toFixed(2)}°`}
                  </p>
                </div>
              </div>
            </div>

            <Separator />

            {/* Key Positions */}
            <div className="grid sm:grid-cols-3 gap-4">
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  {t('astrology:solarReturn.srAscendant', { defaultValue: 'SR Ascendant' })}
                </p>
                <p className="text-2xl font-bold">
                  {getSignSymbol(chart.ascendant_sign)} {chart.ascendant_degree.toFixed(0)}°
                </p>
                <p className="text-sm text-muted-foreground">
                  {translateSign(chart.ascendant_sign)}
                </p>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  {t('astrology:solarReturn.srSunHouse', { defaultValue: 'SR Sun House' })}
                </p>
                <p className="text-2xl font-bold">
                  <Home className="h-6 w-6 inline-block mr-1" />
                  {chart.sun_house}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t('astrology:houses.house', { defaultValue: 'House' })} {chart.sun_house}
                </p>
              </div>
              <div className="text-center p-3 rounded-lg bg-muted/30">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                  {t('astrology:solarReturn.srMidheaven', { defaultValue: 'SR Midheaven' })}
                </p>
                <p className="text-2xl font-bold">
                  {getSignSymbol(chart.midheaven_sign)} {chart.midheaven_degree.toFixed(0)}°
                </p>
                <p className="text-sm text-muted-foreground">
                  {translateSign(chart.midheaven_sign)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Comparison to Natal Card */}
        {comparison && (
          <Card className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-3">
                <ArrowLeftRight className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <span>
                  {t('astrology:solarReturn.comparison', { defaultValue: 'Natal Comparison' })}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* SR angles in natal houses */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                    {t('astrology:solarReturn.srAscInNatal', {
                      defaultValue: 'SR Ascendant in Natal House',
                    })}
                  </p>
                  <p className="text-xl font-bold">{comparison.sr_asc_in_natal_house}</p>
                </div>
                <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
                    {t('astrology:solarReturn.srMcInNatal', {
                      defaultValue: 'SR MC in Natal House',
                    })}
                  </p>
                  <p className="text-xl font-bold">{comparison.sr_mc_in_natal_house}</p>
                </div>
              </div>

              <Separator />

              {/* SR planets in natal houses */}
              <PlanetsInHousesDisplay
                title={t('astrology:solarReturn.srPlanetsInNatal', {
                  defaultValue: 'SR Planets in Natal Houses',
                })}
                planetsInHouses={comparison.sr_planets_in_natal_houses}
              />

              <Separator />

              {/* Key aspects between SR and natal */}
              {comparison.key_aspects.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                    {t('astrology:solarReturn.keyAspects', {
                      defaultValue: 'Key Aspects (SR to Natal)',
                    })}
                  </h4>
                  <div className="space-y-2">
                    {comparison.key_aspects.slice(0, 6).map((aspect, idx) => (
                      <AspectDisplay key={idx} aspect={aspect} />
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Interpretation */}
        {interpretation && <InterpretationDisplay interpretation={interpretation} />}
      </div>
    </PremiumFeatureGate>
  );
}
