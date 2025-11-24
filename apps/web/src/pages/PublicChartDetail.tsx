/**
 * Public Chart Detail Page - view famous person's natal chart
 *
 * This page uses the same components as ChartDetailPage but without
 * user-specific features (edit, delete, PDF export, RAG toggle).
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  getPublicChart,
  getCategoryLabel,
  getPublicChartInterpretations,
  type PublicChartDetail,
  type PublicChartInterpretations,
} from '../services/publicCharts';
import type {
  PlanetPosition,
  HousePosition,
  AspectData,
  SectAnalysisData,
  ArabicParts,
} from '../services/charts';
import type { LunarPhaseData } from '@/components/LunarPhase';
import type { SolarPhaseData } from '@/components/SolarPhase';
import type { LordOfNativityData } from '@/components/LordOfNativity';
import type { TemperamentData } from '@/components/TemperamentDisplay';
import { formatBirthDateTime } from '@/utils/datetime';
import { getSignSymbol } from '../utils/astro';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { useAstroTranslation } from '../hooks/useAstroTranslation';
import { useAuth } from '../contexts/AuthContext';

// Components
import { ChartWheelAstro } from '../components/ChartWheelAstro';
import { PlanetList } from '../components/PlanetList';
import { HouseTable } from '../components/HouseTable';
import { AspectGrid } from '../components/AspectGrid';
import { LunarPhase } from '../components/LunarPhase';
import { SolarPhase } from '../components/SolarPhase';
import { LordOfNativity } from '../components/LordOfNativity';
import { TemperamentDisplay } from '../components/TemperamentDisplay';
import { ArabicPartsTable } from '../components/ArabicPartsTable';
import { SectAnalysis } from '../components/SectAnalysis';
import { InfoTooltip } from '../components/InfoTooltip';
import { BigThreeBadge } from '@/components/ui/big-three-badge';

// UI Components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ArrowLeft, Sparkles, Eye, BookOpen, Loader2 } from 'lucide-react';

// Type for chart_data from public charts API
interface PublicChartData {
  planets: PlanetPosition[];
  houses: HousePosition[];
  aspects: AspectData[];
  ascendant: number;
  midheaven: number;
  sect?: string;
  sect_analysis?: SectAnalysisData;
  lunar_phase?: LunarPhaseData;
  solar_phase?: SolarPhaseData;
  lord_of_nativity?: LordOfNativityData;
  temperament?: TemperamentData;
  arabic_parts?: ArabicParts;
  calculation_timestamp?: string;
}

export function PublicChartDetailPage() {
  const { t } = useTranslation();
  const { translateSign, translatePlanet } = useAstroTranslation();
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();

  const [chart, setChart] = useState<PublicChartDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [interpretations, setInterpretations] = useState<PublicChartInterpretations | null>(null);
  const [isLoadingInterpretations, setIsLoadingInterpretations] = useState(false);

  const loadChart = useCallback(async () => {
    if (!slug) return;

    setIsLoading(true);
    setError('');

    try {
      const data = await getPublicChart(slug);
      setChart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chart');
    } finally {
      setIsLoading(false);
    }
  }, [slug]);

  const loadInterpretations = useCallback(async () => {
    if (!slug) return;

    setIsLoadingInterpretations(true);
    try {
      const data = await getPublicChartInterpretations(slug);
      setInterpretations(data);
    } catch (err) {
      console.error('Failed to load interpretations:', err);
      // Silently fail - interpretations are optional
    } finally {
      setIsLoadingInterpretations(false);
    }
  }, [slug]);

  useEffect(() => {
    loadChart();
  }, [loadChart]);

  // Load interpretations when chart is loaded
  useEffect(() => {
    if (chart?.chart_data) {
      loadInterpretations();
    }
  }, [chart?.chart_data, loadInterpretations]);

  // Helper functions
  function getAscendantSign(): string {
    const chartData = chart?.chart_data as PublicChartData | null;
    if (!chartData) return '';
    const ascLongitude = chartData.ascendant;
    const signIndex = Math.floor(ascLongitude / 30);
    const signs = [
      'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
      'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ];
    return signs[signIndex];
  }

  function getSunSign(): string {
    const chartData = chart?.chart_data as PublicChartData | null;
    if (!chartData) return '';
    const sun = chartData.planets?.find(p => p.name === 'Sun');
    return sun?.sign || '';
  }

  function getMoonSign(): string {
    const chartData = chart?.chart_data as PublicChartData | null;
    if (!chartData) return '';
    const moon = chartData.planets?.find(p => p.name === 'Moon');
    return moon?.sign || '';
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <p className="text-body text-muted-foreground">{t('chartDetail.loading', { defaultValue: 'Loading birth chart...' })}</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !chart) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center px-4">
        <div className="max-w-md w-full animate-fade-in">
          <div className="bg-destructive/10 border border-destructive/20 rounded-astro-lg p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              {t('publicCharts.notFound', 'Mapa não encontrado')}
            </h2>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <Button asChild className="w-full">
              <Link to="/public-charts">{t('common.back', 'Voltar')}</Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const chartData = chart.chart_data as PublicChartData | null;
  const ascSign = getAscendantSign();
  const ascDegree = chartData?.ascendant
    ? Math.floor((chartData.ascendant % 30))
    : 0;
  const sunSign = getSunSign();
  const moonSign = getMoonSign();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link
                to="/public-charts"
                className="hover:opacity-80 transition-all duration-200 flex-shrink-0"
                aria-label={t('common.back')}
              >
                <img
                  src="/logo.png"
                  alt="Real Astrology"
                  className="h-8 w-8"
                />
              </Link>
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-h3 font-display text-foreground">
                    {chart.full_name}
                  </h1>
                  {chart.category && (
                    <Badge variant="secondary">{getCategoryLabel(chart.category)}</Badge>
                  )}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone, true)}
                  {chart.city && ` • ${chart.city}`}
                  {chart.country && `, ${chart.country}`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-sm text-muted-foreground">
                <Eye className="h-4 w-4" />
                {chart.view_count}
              </span>
              <LanguageSelector />
              <ThemeToggle />
              {user ? (
                <Button size="sm" asChild>
                  <Link to="/dashboard">{t('nav.dashboard')}</Link>
                </Button>
              ) : (
                <>
                  <Button variant="outline" size="sm" asChild>
                    <Link to="/login">{t('nav.login')}</Link>
                  </Button>
                  <Button size="sm" asChild>
                    <Link to="/register">{t('nav.register')}</Link>
                  </Button>
                </>
              )}
              <Button asChild variant="secondary" size="sm">
                <Link to="/public-charts">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t('common.back')}
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 animate-fade-in">
        {/* Bio section for famous people */}
        {chart.short_bio && (
          <Card className="mb-6 border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <div className="flex items-start gap-6">
                {chart.photo_url ? (
                  <img
                    src={chart.photo_url}
                    alt={chart.full_name}
                    className="h-24 w-24 rounded-full object-cover flex-shrink-0"
                  />
                ) : (
                  <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                    <span className="text-3xl font-bold text-muted-foreground">
                      {chart.full_name.charAt(0)}
                    </span>
                  </div>
                )}
                <div>
                  <p className="text-muted-foreground">{chart.short_bio}</p>
                  {chart.highlights && chart.highlights.length > 0 && (
                    <div className="mt-4">
                      <h4 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                        <Sparkles className="h-4 w-4" />
                        {t('publicCharts.highlights', 'Destaques Astrológicos')}
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                        {chart.highlights.map((highlight, index) => (
                          <li key={index}>{highlight}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Chart Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">{t('chartDetail.ascendant')}</p>
              <p className="text-h3 font-display text-foreground flex items-center gap-2">
                {getSignSymbol(ascSign)} {translateSign(ascSign)} {ascDegree}°
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">{t('newChart.houseSystem')}</p>
              <p className="text-h3 font-display text-foreground capitalize">
                {chart.house_system}
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">{t('newChart.zodiacType')}</p>
              <p className="text-h3 font-display text-foreground capitalize">
                Tropical
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="visual" className="w-full">
          <TabsList className="w-full justify-start mb-6">
            <TabsTrigger value="visual">{t('chartDetail.tabs.visual')}</TabsTrigger>
            <TabsTrigger value="planets">
              {t('chartDetail.tabs.planets')} ({chartData?.planets?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="houses">{t('chartDetail.tabs.houses')} (12)</TabsTrigger>
            <TabsTrigger value="aspects">
              {t('chartDetail.tabs.aspects')} ({chartData?.aspects?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="arabic-parts">
              {t('chartDetail.tabs.arabicParts')} (4)
            </TabsTrigger>
            <TabsTrigger value="interpretations" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              {t('chartDetail.tabs.interpretations', 'Interpretações')}
              {isLoadingInterpretations && <Loader2 className="h-3 w-3 animate-spin" />}
            </TabsTrigger>
          </TabsList>

          {/* Tab Content: Visual */}
          <TabsContent value="visual" className="mt-0">
            {chartData && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display">{t('chartDetail.birthChart', { defaultValue: 'Birth Chart' })}</CardTitle>
                  <CardDescription>{t('chartDetail.birthChartDesc', { defaultValue: 'Complete visualization of your birth sky' })}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  {/* Big Three Summary */}
                  <div>
                    <h3 className="text-h4 font-display mb-4">{t('chartDetail.astroEssence', { defaultValue: 'Astrological Essence' })}</h3>
                    <BigThreeBadge
                      sunSign={sunSign}
                      moonSign={moonSign}
                      risingSign={ascSign}
                      variant="horizontal"
                    />
                  </div>

                  {/* Big Three Details */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Sun */}
                    <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl" title={t('chartDetail.sun')}>☉</span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourEssence', { defaultValue: 'Your essence' })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.sunTooltip', { defaultValue: 'The Sun represents your core identity, life purpose and vitality.' })}
                              side="top"
                            />
                          </div>
                          <p className="text-lg font-semibold text-foreground">
                            {translatePlanet('Sun')} {t('chartDetail.in', { defaultValue: 'in' })} {getSignSymbol(sunSign)} {translateSign(sunSign)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('chartDetail.bigThree.sunDesc', { defaultValue: 'Identity and life purpose' })}
                      </p>
                    </div>

                    {/* Moon */}
                    <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl" title={t('chartDetail.moon')}>☽</span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourEmotions', { defaultValue: 'Your emotions' })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.moonTooltip', { defaultValue: 'The Moon represents your emotions, instinctive needs and unconscious reactions.' })}
                              side="top"
                            />
                          </div>
                          <p className="text-lg font-semibold text-foreground">
                            {translatePlanet('Moon')} {t('chartDetail.in', { defaultValue: 'in' })} {getSignSymbol(moonSign)} {translateSign(moonSign)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('chartDetail.bigThree.moonDesc', { defaultValue: 'Emotional world and needs' })}
                      </p>
                    </div>

                    {/* Ascendant */}
                    <div className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl font-bold text-primary" title={t('chartDetail.ascendant')}>ASC</span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourAppearance', { defaultValue: 'Your appearance' })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.ascTooltip', { defaultValue: 'The Ascendant represents your social mask and first impression.' })}
                              side="top"
                            />
                          </div>
                          <p className="text-lg font-semibold text-foreground">
                            {getSignSymbol(ascSign)} {translateSign(ascSign)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('chartDetail.bigThree.ascDesc', { defaultValue: 'How others see you' })}
                      </p>
                    </div>
                  </div>

                  {/* Chart Wheel */}
                  <div>
                    <h3 className="text-h4 font-display mb-4">{t('chartDetail.chartWheel', { defaultValue: 'Natal Chart Wheel' })}</h3>
                    <ChartWheelAstro chartData={chartData} />
                  </div>

                  {/* Temperament */}
                  {chartData.temperament && (
                    <div>
                      <h3 className="text-h4 font-display mb-4">{t('chartDetail.temperament', { defaultValue: 'Temperament Analysis' })}</h3>
                      <TemperamentDisplay temperament={chartData.temperament} />
                    </div>
                  )}

                  {/* Lord of Nativity */}
                  {chartData.lord_of_nativity && (
                    <div>
                      <LordOfNativity lordOfNativity={chartData.lord_of_nativity} />
                    </div>
                  )}

                  {/* Lunar and Solar Phases */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {chartData.lunar_phase && (
                      <div>
                        <h3 className="text-h4 font-display mb-4">{t('chartDetail.lunarPhase', { defaultValue: 'Lunar Phase' })}</h3>
                        <LunarPhase lunarPhase={chartData.lunar_phase} />
                      </div>
                    )}
                    {chartData.solar_phase && (
                      <div>
                        <h3 className="text-h4 font-display mb-4">{t('chartDetail.solarPhase', { defaultValue: 'Solar Phase' })}</h3>
                        <SolarPhase solarPhase={chartData.solar_phase} />
                      </div>
                    )}
                  </div>

                  {/* Sect Analysis */}
                  {chartData.sect_analysis && (
                    <div>
                      <h3 className="text-h4 font-display mb-4">{t('components.sect.title', { defaultValue: 'Sect Analysis' })}</h3>
                      <SectAnalysis sectData={chartData.sect_analysis} />
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Planets */}
          <TabsContent value="planets" className="mt-0">
            {chartData && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.planetPositions', { defaultValue: 'Planetary Positions' })}
                    <InfoTooltip
                      content={t('chartDetail.planetPositionsTooltip', { defaultValue: 'Exact planetary positions calculated with Swiss Ephemeris (precision < 1 arcsecond).' })}
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <PlanetList
                    planets={chartData.planets}
                    showOnlyClassical={true}
                    lordOfNativity={chartData.lord_of_nativity}
                  />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Houses */}
          <TabsContent value="houses" className="mt-0">
            {chartData && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.astroHouses', { defaultValue: 'Astrological Houses' })}
                    <InfoTooltip
                      content={t('chartDetail.astroHousesTooltip', { defaultValue: 'The 12 houses divide the sky into sectors representing life areas. System used: {{system}}.', system: chart.house_system })}
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <HouseTable houses={chartData.houses} />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Aspects */}
          <TabsContent value="aspects" className="mt-0">
            {chartData && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.planetaryAspects', { defaultValue: 'Planetary Aspects' })}
                    <InfoTooltip
                      content={t('chartDetail.planetaryAspectsTooltip', { defaultValue: 'Aspects are geometric angles between planets that reveal how they interact.' })}
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AspectGrid aspects={chartData.aspects} />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Arabic Parts */}
          <TabsContent value="arabic-parts" className="mt-0">
            {chartData?.arabic_parts ? (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.arabicPartsLots', { defaultValue: 'Arabic Parts (Lots)' })}
                    <InfoTooltip
                      content={t('chartDetail.arabicPartsTooltip', { defaultValue: 'Arabic Parts (or Lots) are mathematically calculated points from planetary positions.' })}
                      side="right"
                    />
                  </CardTitle>
                  <CardDescription>
                    {t('chartDetail.arabicPartsDesc', { defaultValue: 'Sensitive points from Hellenistic astrological tradition' })}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ArabicPartsTable parts={chartData.arabic_parts} />

                  {/* Educational Section */}
                  <div className="mt-8 p-6 bg-muted/50 rounded-lg space-y-4">
                    <h4 className="text-lg font-semibold text-foreground flex items-center gap-2">
                      📚 {t('chartDetail.arabicParts.aboutTitle', { defaultValue: 'About Arabic Parts' })}
                    </h4>

                    <div className="space-y-3 text-sm text-muted-foreground">
                      <p>
                        <strong className="text-foreground">{t('chartDetail.arabicParts.whatAre', { defaultValue: 'What they are:' })}</strong> {t('chartDetail.arabicParts.whatAreDesc', { defaultValue: 'Arabic Parts (also called "Lots" in Hellenistic tradition) are mathematically calculated points from planetary and angular positions.' })}
                      </p>

                      <p>
                        <strong className="text-foreground">{t('chartDetail.arabicParts.formula', { defaultValue: 'General formula:' })}</strong> {t('chartDetail.arabicParts.formulaDesc', { defaultValue: 'Part = Ascendant + Planet1 - Planet2 (all in degrees 0-360).' })}
                      </p>

                      <p>
                        <strong className="text-foreground">{t('chartDetail.arabicParts.importance', { defaultValue: 'Importance:' })}</strong> {t('chartDetail.arabicParts.importanceDesc', { defaultValue: 'The house where a Part falls and the aspects it receives from natal planets are significant.' })}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardContent className="pt-6 text-center text-muted-foreground">
                  <p>{t('chartDetail.arabicParts.notAvailable', { defaultValue: 'Arabic Parts not available for this chart.' })}</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Interpretations */}
          <TabsContent value="interpretations" className="mt-0">
            <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-h3 font-display flex items-center gap-2">
                  <BookOpen className="h-6 w-6" />
                  {t('chartDetail.interpretations.title', 'Interpretações Astrológicas')}
                </CardTitle>
                <CardDescription>
                  {t('chartDetail.interpretations.description', 'Análises geradas por inteligência artificial com base em textos tradicionais de astrologia.')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoadingInterpretations ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="text-center">
                      <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
                      <p className="text-muted-foreground">
                        {t('chartDetail.interpretations.loading', 'Gerando interpretações...')}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        {t('chartDetail.interpretations.loadingHint', 'Isso pode levar alguns segundos na primeira vez.')}
                      </p>
                    </div>
                  </div>
                ) : interpretations ? (
                  <div className="space-y-6">
                    {/* Planet Interpretations */}
                    {Object.keys(interpretations.planets).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                          ☉ {t('chartDetail.interpretations.planets', 'Planetas')}
                        </h3>
                        <Accordion type="multiple" className="space-y-2">
                          {Object.entries(interpretations.planets).map(([planet, content]) => (
                            <AccordionItem key={planet} value={planet} className="border rounded-lg px-4">
                              <AccordionTrigger className="hover:no-underline">
                                <span className="text-left font-medium">{translatePlanet(planet)}</span>
                              </AccordionTrigger>
                              <AccordionContent>
                                <div className="prose prose-sm max-w-none text-muted-foreground pb-4">
                                  {content.split('\n').map((paragraph, i) => (
                                    <p key={i} className="mb-2 last:mb-0">{paragraph}</p>
                                  ))}
                                </div>
                              </AccordionContent>
                            </AccordionItem>
                          ))}
                        </Accordion>
                      </div>
                    )}

                    {/* House Interpretations */}
                    {Object.keys(interpretations.houses).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                          🏠 {t('chartDetail.interpretations.houses', 'Casas')}
                        </h3>
                        <Accordion type="multiple" className="space-y-2">
                          {Object.entries(interpretations.houses)
                            .sort(([a], [b]) => parseInt(a) - parseInt(b))
                            .map(([house, content]) => (
                              <AccordionItem key={house} value={`house-${house}`} className="border rounded-lg px-4">
                                <AccordionTrigger className="hover:no-underline">
                                  <span className="text-left font-medium">
                                    {t('chartDetail.interpretations.houseLabel', 'Casa {{number}}', { number: house })}
                                  </span>
                                </AccordionTrigger>
                                <AccordionContent>
                                  <div className="prose prose-sm max-w-none text-muted-foreground pb-4">
                                    {content.split('\n').map((paragraph, i) => (
                                      <p key={i} className="mb-2 last:mb-0">{paragraph}</p>
                                    ))}
                                  </div>
                                </AccordionContent>
                              </AccordionItem>
                            ))}
                        </Accordion>
                      </div>
                    )}

                    {/* Aspect Interpretations */}
                    {Object.keys(interpretations.aspects).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                          ✦ {t('chartDetail.interpretations.aspects', 'Aspectos')}
                        </h3>
                        <Accordion type="multiple" className="space-y-2">
                          {Object.entries(interpretations.aspects).map(([aspect, content]) => {
                            const parts = aspect.split('-');
                            const displayName = parts.length === 3
                              ? `${translatePlanet(parts[0])} ${parts[1]} ${translatePlanet(parts[2])}`
                              : aspect;
                            return (
                              <AccordionItem key={aspect} value={aspect} className="border rounded-lg px-4">
                                <AccordionTrigger className="hover:no-underline">
                                  <span className="text-left font-medium">{displayName}</span>
                                </AccordionTrigger>
                                <AccordionContent>
                                  <div className="prose prose-sm max-w-none text-muted-foreground pb-4">
                                    {content.split('\n').map((paragraph, i) => (
                                      <p key={i} className="mb-2 last:mb-0">{paragraph}</p>
                                    ))}
                                  </div>
                                </AccordionContent>
                              </AccordionItem>
                            );
                          })}
                        </Accordion>
                      </div>
                    )}

                    {/* Arabic Parts Interpretations */}
                    {interpretations.arabic_parts && Object.keys(interpretations.arabic_parts).length > 0 && (
                      <div>
                        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                          ⚜ {t('chartDetail.interpretations.arabicParts', 'Partes Árabes')}
                        </h3>
                        <Accordion type="multiple" className="space-y-2">
                          {Object.entries(interpretations.arabic_parts).map(([part, content]) => {
                            const partNames: Record<string, string> = {
                              fortune: t('arabicParts.fortune', 'Lote da Fortuna'),
                              spirit: t('arabicParts.spirit', 'Lote do Espírito'),
                              eros: t('arabicParts.eros', 'Lote de Eros'),
                              necessity: t('arabicParts.necessity', 'Lote da Necessidade'),
                            };
                            return (
                              <AccordionItem key={part} value={part} className="border rounded-lg px-4">
                                <AccordionTrigger className="hover:no-underline">
                                  <span className="text-left font-medium">{partNames[part] || part}</span>
                                </AccordionTrigger>
                                <AccordionContent>
                                  <div className="prose prose-sm max-w-none text-muted-foreground pb-4">
                                    {content.split('\n').map((paragraph, i) => (
                                      <p key={i} className="mb-2 last:mb-0">{paragraph}</p>
                                    ))}
                                  </div>
                                </AccordionContent>
                              </AccordionItem>
                            );
                          })}
                        </Accordion>
                      </div>
                    )}

                    {/* RAG Badge */}
                    {interpretations.source === 'rag' && (
                      <div className="mt-6 pt-6 border-t border-border">
                        <div className="flex items-center gap-2">
                          <Badge variant="secondary" className="flex items-center gap-2 w-fit">
                            <Sparkles className="h-3 w-3" />
                            {t('rag.badge', 'Aprimorado com RAG')}
                          </Badge>
                          <InfoTooltip
                            content={t('rag.tooltipLong', 'RAG (Retrieval-Augmented Generation) combina inteligência artificial com uma base de conhecimento de livros clássicos de astrologia, resultando em interpretações mais precisas e fundamentadas na tradição astrológica.')}
                            side="right"
                          />
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          {t('rag.description', 'Interpretações baseadas em textos clássicos de astrologia tradicional.')}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12 text-muted-foreground">
                    <BookOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>{t('chartDetail.interpretations.notAvailable', 'Interpretações não disponíveis.')}</p>
                    <Button
                      variant="outline"
                      className="mt-4"
                      onClick={loadInterpretations}
                    >
                      {t('chartDetail.interpretations.retry', 'Tentar novamente')}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* CTA */}
        <div className="mt-12 bg-primary/10 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            {user
              ? t('publicCharts.ctaTitleLoggedIn', 'Crie Mais Mapas Natais')
              : t('publicCharts.ctaTitle', 'Crie Seu Próprio Mapa Natal')
            }
          </h2>
          <p className="text-muted-foreground mb-6">
            {t(
              'publicCharts.ctaDescription',
              'Descubra os segredos do seu mapa astrológico com análise profissional e interpretações IA.'
            )}
          </p>
          <Button size="lg" asChild>
            <Link to={user ? "/charts/new" : "/register"}>
              {user
                ? t('publicCharts.ctaButtonLoggedIn', 'Criar Novo Mapa')
                : t('publicCharts.ctaButton', 'Começar Grátis')
              }
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
