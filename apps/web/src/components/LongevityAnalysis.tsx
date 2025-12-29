/**
 * LongevityAnalysis - Traditional astrology longevity analysis display.
 *
 * Combines Hyleg (Giver of Life) and Alcochoden (Giver of Years) calculations.
 * This is a premium-only feature with educational disclaimer.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { getSignSymbol } from '@/utils/astro';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';
import { HeartPulse, Clock, AlertTriangle, CheckCircle2, XCircle, Info } from 'lucide-react';
import { PremiumFeatureGate } from './PremiumFeatureGate';

// Import types from external file (only import what's directly used in this module)
import type { HylegData, AlcochodenData, LongevityAnalysisProps } from '@/types/longevity';

// Re-export types for backwards compatibility
export type { LongevityData, HylegData, AlcochodenData } from '@/types/longevity';

// ============================================================================
// Constants (defined outside component for performance)
// ============================================================================

const planetSymbols: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
  Ascendant: 'ASC',
  'Part of Fortune': '⊕',
  'Prenatal Syzygy (New Moon)': '🌑',
  'Prenatal Syzygy (Full Moon)': '🌕',
};

const classificationColors: Record<string, string> = {
  dignified: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
  peregrine: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20',
  debilitated: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20',
};

const yearTypeColors: Record<string, string> = {
  major: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
  middle: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20',
  minor: 'bg-orange-500/10 text-orange-700 dark:text-orange-400 border-orange-500/20',
};

// ============================================================================
// Loading Skeleton Component
// ============================================================================

function LongevitySkeleton() {
  return (
    <div className="space-y-6">
      {/* Disclaimer skeleton */}
      <Skeleton className="h-24 w-full" />

      {/* Summary skeleton */}
      <Skeleton className="h-32 w-full" />

      {/* Cards skeleton */}
      <div className="grid md:grid-cols-2 gap-6">
        <Skeleton className="h-80 w-full" />
        <Skeleton className="h-80 w-full" />
      </div>
    </div>
  );
}

// ============================================================================
// Hyleg Display Component
// ============================================================================

function HylegDisplay({ hyleg }: { hyleg: HylegData }) {
  const { t } = useTranslation();
  const { translatePlanet, translateSign } = useAstroTranslation();

  const planetSymbol =
    hyleg.hyleg && planetSymbols[hyleg.hyleg]
      ? planetSymbols[hyleg.hyleg]
      : hyleg.hyleg?.includes('Prenatal')
        ? hyleg.hyleg.includes('New')
          ? '🌑'
          : '🌕'
        : '★';

  const hylegName = hyleg.hyleg
    ? hyleg.hyleg.startsWith('Prenatal')
      ? hyleg.hyleg
      : translatePlanet(hyleg.hyleg)
    : t('components.longevity.noHyleg', { defaultValue: 'Not found' });

  return (
    <Card className="bg-gradient-to-br from-rose-500/10 to-pink-500/10 border-rose-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-3">
          <HeartPulse className="h-6 w-6 text-rose-600 dark:text-rose-400" />
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground flex items-center gap-2">
              {t('components.longevity.hyleg.title', { defaultValue: 'Hyleg (Giver of Life)' })}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.longevity.hyleg.subtitle', {
                defaultValue: 'The vital force significator',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {hyleg.hyleg ? (
          <>
            {/* Hyleg Planet */}
            <div className="flex items-center gap-4">
              <div className="text-4xl">{planetSymbol}</div>
              <div className="flex-1">
                <p className="text-xl font-bold text-foreground">{hylegName}</p>
                <p className="text-sm text-muted-foreground">
                  {getSignSymbol(hyleg.hyleg_sign || '')} {translateSign(hyleg.hyleg_sign || '')} •{' '}
                  {t('components.longevity.house', { defaultValue: 'House' })} {hyleg.hyleg_house}
                </p>
              </div>
              <Badge
                variant="outline"
                className={`text-xs ${hyleg.hyleg_dignity ? classificationColors[hyleg.hyleg_dignity.classification] || '' : 'bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20'}`}
              >
                {hyleg.is_day_chart
                  ? t('components.longevity.dayChart', { defaultValue: 'Day Chart' })
                  : t('components.longevity.nightChart', { defaultValue: 'Night Chart' })}
              </Badge>
            </div>

            {/* Qualification */}
            <div className="space-y-1">
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                {t('components.longevity.hyleg.qualification', { defaultValue: 'Qualification' })}
              </p>
              <p className="text-sm text-foreground">{hyleg.qualification_reason}</p>
            </div>

            {/* Domicile Lord */}
            {hyleg.domicile_lord && (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  {t('components.longevity.hyleg.domicileLord', { defaultValue: 'Domicile Lord' })}
                </p>
                <p className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <span>{planetSymbols[hyleg.domicile_lord] || '★'}</span>
                  {translatePlanet(hyleg.domicile_lord)}
                </p>
              </div>
            )}

            {/* Aspecting Planets */}
            {hyleg.aspecting_planets && hyleg.aspecting_planets.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  {t('components.longevity.hyleg.aspectingPlanets', {
                    defaultValue: 'Aspecting Planets',
                  })}
                </p>
                <div className="flex flex-wrap gap-2">
                  {hyleg.aspecting_planets.map((planet: string) => (
                    <Badge key={planet} variant="secondary" className="text-xs">
                      {planetSymbols[planet] || '★'} {translatePlanet(planet)}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Candidates Evaluated */}
            {hyleg.candidates_evaluated && hyleg.candidates_evaluated.length > 0 && (
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  {t('components.longevity.hyleg.candidatesEvaluated', {
                    defaultValue: 'Candidates Evaluated',
                  })}
                </p>
                <div className="space-y-1">
                  {hyleg.candidates_evaluated.map((candidate, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-2 rounded-md bg-card/50 border border-border/50"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{planetSymbols[candidate.candidate] || '★'}</span>
                        <span className="text-sm">
                          {candidate.candidate.startsWith('Prenatal')
                            ? candidate.candidate
                            : translatePlanet(candidate.candidate)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {candidate.is_qualified ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-4">
            <p className="text-muted-foreground">
              {t('components.longevity.hyleg.notFound', {
                defaultValue: 'No Hyleg could be determined for this chart.',
              })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Alcochoden Display Component
// ============================================================================

function AlcochodenDisplay({ alcochoden }: { alcochoden: AlcochodenData }) {
  const { t } = useTranslation();
  const { translatePlanet, translateSign } = useAstroTranslation();

  if (!alcochoden.alcochoden) {
    return (
      <Card className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/20">
        <CardHeader className="pb-2">
          <CardTitle className="flex items-center gap-3">
            <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            <div className="flex-1">
              <div className="text-lg font-semibold text-foreground">
                {t('components.longevity.alcochoden.title', {
                  defaultValue: 'Alcochoden (Giver of Years)',
                })}
              </div>
              <div className="text-xs text-muted-foreground font-normal mt-1">
                {t('components.longevity.alcochoden.subtitle', {
                  defaultValue: 'The planet determining lifespan',
                })}
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p className="text-muted-foreground">
              {alcochoden.no_alcochoden_reason ||
                t('components.longevity.alcochoden.notFound', {
                  defaultValue: 'No Alcochoden could be determined.',
                })}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const planetSymbol = planetSymbols[alcochoden.alcochoden] || '★';

  return (
    <Card className="bg-gradient-to-br from-blue-500/10 to-indigo-500/10 border-blue-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-3">
          <Clock className="h-6 w-6 text-blue-600 dark:text-blue-400" />
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground">
              {t('components.longevity.alcochoden.title', {
                defaultValue: 'Alcochoden (Giver of Years)',
              })}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.longevity.alcochoden.subtitle', {
                defaultValue: 'The planet determining lifespan',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Alcochoden Planet */}
        <div className="flex items-center gap-4">
          <div className="text-4xl">{planetSymbol}</div>
          <div className="flex-1">
            <p className="text-xl font-bold text-foreground">
              {translatePlanet(alcochoden.alcochoden)}
            </p>
            <p className="text-sm text-muted-foreground">
              {getSignSymbol(alcochoden.alcochoden_sign || '')}{' '}
              {translateSign(alcochoden.alcochoden_sign || '')} •{' '}
              {t('components.longevity.house', { defaultValue: 'House' })}{' '}
              {alcochoden.alcochoden_house}
            </p>
          </div>
          <Badge
            variant="outline"
            className={`text-xs ${yearTypeColors[alcochoden.year_type || 'middle'] || ''}`}
          >
            {t(`components.longevity.alcochoden.yearType.${alcochoden.year_type || 'undefined'}`, {
              defaultValue: alcochoden.year_type || 'Unknown',
            })}
          </Badge>
        </div>

        {/* Planetary Years Table */}
        {alcochoden.years && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.longevity.alcochoden.planetaryYears', {
                defaultValue: 'Planetary Years',
              })}
            </p>
            <div className="grid grid-cols-3 gap-2">
              <div
                className={`p-2 rounded-md text-center ${alcochoden.year_type === 'minor' ? 'ring-2 ring-blue-500' : 'bg-card/50 border border-border/50'}`}
              >
                <p className="text-xs text-muted-foreground">
                  {t('components.longevity.alcochoden.minor', { defaultValue: 'Minor' })}
                </p>
                <p className="text-lg font-bold">{alcochoden.years.minor}</p>
              </div>
              <div
                className={`p-2 rounded-md text-center ${alcochoden.year_type === 'middle' ? 'ring-2 ring-blue-500' : 'bg-card/50 border border-border/50'}`}
              >
                <p className="text-xs text-muted-foreground">
                  {t('components.longevity.alcochoden.middle', { defaultValue: 'Middle' })}
                </p>
                <p className="text-lg font-bold">{alcochoden.years.middle}</p>
              </div>
              <div
                className={`p-2 rounded-md text-center ${alcochoden.year_type === 'major' ? 'ring-2 ring-blue-500' : 'bg-card/50 border border-border/50'}`}
              >
                <p className="text-xs text-muted-foreground">
                  {t('components.longevity.alcochoden.major', { defaultValue: 'Major' })}
                </p>
                <p className="text-lg font-bold">{alcochoden.years.major}</p>
              </div>
            </div>
          </div>
        )}

        {/* Year Calculation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.longevity.alcochoden.calculation', { defaultValue: 'Calculation' })}
          </p>
          <div className="p-3 rounded-md bg-card/50 border border-border/50">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">
                {t('components.longevity.alcochoden.baseYears', { defaultValue: 'Base Years' })}
              </span>
              <span className="font-mono font-bold">{alcochoden.base_years}</span>
            </div>
            {alcochoden.modifications && alcochoden.modifications.length > 0 && (
              <>
                <Separator className="my-2" />
                {alcochoden.modifications.map((mod, idx) => (
                  <div key={idx} className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">{mod.description}</span>
                    <span
                      className={`font-mono ${mod.value >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}
                    >
                      {mod.value >= 0 ? '+' : ''}
                      {mod.value}
                    </span>
                  </div>
                ))}
                <Separator className="my-2" />
                <div className="flex justify-between items-center">
                  <span className="font-semibold">
                    {t('components.longevity.alcochoden.totalYears', { defaultValue: 'Total' })}
                  </span>
                  <span className="font-mono font-bold text-lg">{alcochoden.modified_years}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Candidates */}
        {alcochoden.candidates_evaluated && alcochoden.candidates_evaluated.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.longevity.alcochoden.candidatesEvaluated', {
                defaultValue: 'Candidates Evaluated',
              })}
            </p>
            <div className="space-y-1">
              {alcochoden.candidates_evaluated.slice(0, 5).map((candidate, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 rounded-md bg-card/50 border border-border/50"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{planetSymbols[candidate.planet] || '★'}</span>
                    <span className="text-sm">{translatePlanet(candidate.planet)}</span>
                    <Badge variant="outline" className="text-xs">
                      {candidate.dignity_type}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      {candidate.total_dignity_points} pts
                    </span>
                    {candidate.planet === alcochoden.alcochoden && (
                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ============================================================================
// Main LongevityAnalysis Component
// ============================================================================

export function LongevityAnalysis({ longevity, isLoading = false }: LongevityAnalysisProps) {
  const { t } = useTranslation();

  // Show loading skeleton
  if (isLoading) {
    return (
      <PremiumFeatureGate feature="longevity">
        <LongevitySkeleton />
      </PremiumFeatureGate>
    );
  }

  if (!longevity) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">
          {t('components.longevity.noData', {
            defaultValue: 'Longevity data not available for this chart.',
          })}
        </p>
      </div>
    );
  }

  return (
    <PremiumFeatureGate feature="longevity">
      <div className="space-y-6">
        {/* Educational Disclaimer */}
        <Alert className="border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30">
          <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          <AlertTitle className="text-amber-900 dark:text-amber-100">
            {t('components.longevity.disclaimer.title', {
              defaultValue: 'Educational Purpose Only',
            })}
          </AlertTitle>
          <AlertDescription className="text-amber-800 dark:text-amber-200">
            {longevity.educational_disclaimer ||
              t('components.longevity.disclaimer.text', {
                defaultValue:
                  'These calculations are presented for historical and educational purposes only. They are not scientifically validated and should never be used for health predictions or medical decisions.',
              })}
          </AlertDescription>
        </Alert>

        {/* Summary Card */}
        {longevity.summary && (
          <Card className="bg-gradient-to-br from-purple-500/10 to-violet-500/10 border-purple-500/20">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-3">
                <Info className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                <span>
                  {t('components.longevity.summary.title', { defaultValue: 'Analysis Summary' })}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t('components.longevity.summary.vitalForce', { defaultValue: 'Vital Force' })}
                  </p>
                  <p className="text-sm">
                    {longevity.summary.vital_force_planet ? (
                      <>
                        <span className="font-semibold">
                          {planetSymbols[longevity.summary.vital_force_planet] || '★'}{' '}
                          {longevity.summary.vital_force_planet}
                        </span>
                        <span className="text-muted-foreground">
                          {' '}
                          - {longevity.summary.vital_force_assessment}
                        </span>
                      </>
                    ) : (
                      <span className="text-muted-foreground">
                        {t('components.longevity.summary.notDetermined', {
                          defaultValue: 'Could not be determined',
                        })}
                      </span>
                    )}
                  </p>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground uppercase tracking-wide">
                    {t('components.longevity.summary.yearsIndicator', {
                      defaultValue: 'Years Indicator',
                    })}
                  </p>
                  <p className="text-sm">
                    {longevity.summary.years_planet ? (
                      <>
                        <span className="font-semibold">
                          {planetSymbols[longevity.summary.years_planet] || '★'}{' '}
                          {longevity.summary.years_planet}
                        </span>
                        {longevity.summary.estimated_years && (
                          <span className="text-muted-foreground">
                            {' '}
                            ({longevity.summary.estimated_years}{' '}
                            {t('components.longevity.years', { defaultValue: 'years' })})
                          </span>
                        )}
                      </>
                    ) : (
                      <span className="text-muted-foreground">
                        {t('components.longevity.summary.notDetermined', {
                          defaultValue: 'Could not be determined',
                        })}
                      </span>
                    )}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Hyleg and Alcochoden Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {longevity.hyleg && <HylegDisplay hyleg={longevity.hyleg} />}
          {longevity.alcochoden && <AlcochodenDisplay alcochoden={longevity.alcochoden} />}
        </div>
      </div>
    </PremiumFeatureGate>
  );
}
