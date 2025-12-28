/**
 * Chart Detail Page - complete birth chart visualization
 */

import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { chartsService, BirthChart } from '../services/charts';
import { amplitudeService } from '../services/amplitude';
import { useAmplitudePageView } from '../hooks/useAmplitudePageView';
import {
  interpretationsService,
  RAGInterpretations,
  RAGSourceInfo,
} from '../services/interpretations';
import { generateChartPDF, getPDFStatus, downloadChartPDF } from '../services/pdf';
import { getToken } from '../services/api';
import type { PDFStatus } from '../types/pdf';
import { ChartWheelAstro } from '../components/ChartWheelAstro';
import { PlanetList } from '../components/PlanetList';
import { HouseTable } from '../components/HouseTable';
import { AspectGrid } from '../components/AspectGrid';
import { LunarPhase } from '../components/LunarPhase';
import { SolarPhase } from '../components/SolarPhase';
import { LordOfNativity } from '../components/LordOfNativity';
import { TemperamentDisplay } from '../components/TemperamentDisplay';
import { MentalityCard } from '../components/MentalityCard';
import { ArabicPartsTable } from '../components/ArabicPartsTable';
import { SectAnalysis } from '../components/SectAnalysis';
import { GrowthSuggestions } from '../components/GrowthSuggestions';
import { Skeleton } from '@/components/ui/skeleton';

// Lazy load LongevityAnalysis for code splitting (premium feature)
const LongevityAnalysis = lazy(() =>
  import('../components/LongevityAnalysis').then((module) => ({
    default: module.LongevityAnalysis,
  }))
);
import { InfoTooltip } from '../components/InfoTooltip';
import { getSignSymbol } from '../utils/astro';
import { formatBirthDateTime } from '@/utils/datetime';
import { useAstroTranslation } from '../hooks/useAstroTranslation';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { EmailVerificationModal } from '../components/EmailVerificationModal';
import { InterpretationLanguageNotice } from '../components/InterpretationLanguageNotice';
import { useEmailVerification } from '../hooks/useEmailVerification';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { BigThreeBadge } from '@/components/ui/big-three-badge';
import { Trash2, ArrowLeft, Sparkles, FileDown, Loader2, Edit } from 'lucide-react';

export function ChartDetailPage() {
  const { t, i18n } = useTranslation();
  const { translateSign, translatePlanet } = useAstroTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Track page view
  useAmplitudePageView('Chart Detail Page');

  const [chart, setChart] = useState<BirthChart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  // All interpretations now use RAG by default
  const [interpretations, setInterpretations] = useState<RAGInterpretations | null>(null);

  // PDF export state
  const [pdfStatus, setPdfStatus] = useState<PDFStatus>('idle');
  // @ts-expect-error - TODO: Display error message in UI
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [pdfError, setPdfError] = useState<string | null>(null);

  // Interpretations loading state
  const [isLoadingInterpretations, setIsLoadingInterpretations] = useState(false);

  // Tab tracking for Amplitude
  const [currentTab, setCurrentTab] = useState('visual');

  // Track the last language we loaded interpretations for (to avoid reload loops)
  const lastLoadedLanguageRef = useRef<string | null>(null);

  // Email verification for premium features
  const {
    isEmailVerified,
    showModal: showVerificationModal,
    setShowModal: setShowVerificationModal,
    featureName: verificationFeatureName,
    requireEmailVerification,
    checkVerificationStatus,
    isCheckingStatus,
  } = useEmailVerification();

  useEffect(() => {
    loadChart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Load interpretations when email verification status changes
  useEffect(() => {
    if (isEmailVerified) {
      loadInterpretations();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id, isEmailVerified]);

  // Reload chart data and interpretations when UI language changes
  // Chart data is stored with language keys, so we need to re-fetch to get the correct language slice
  // Interpretations are stored with language column, so the API returns the correct language version
  useEffect(() => {
    const normalizedUiLang = i18n.language.split('-')[0];

    // Only reload if we have already loaded once (avoid double-load on mount)
    if (lastLoadedLanguageRef.current && lastLoadedLanguageRef.current !== normalizedUiLang) {
      // Reload chart data with new language
      loadChart();
      // Reload interpretations with new language (if verified)
      if (isEmailVerified) {
        loadInterpretations();
      }
    }

    lastLoadedLanguageRef.current = normalizedUiLang;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language]);

  // Polling effect for processing charts
  // Note: i18n.language is intentionally not in deps to avoid restarting the poll on language change
  useEffect(() => {
    if (!chart || chart.status !== 'processing') {
      return; // Only poll if chart is processing
    }

    const pollInterval = setInterval(async () => {
      try {
        const token = getToken();
        if (!token || !id) return;

        const status = await chartsService.getStatus(id, token);

        if (status.status === 'completed' || status.status === 'failed') {
          // Reload full chart data when done (with current language)
          const chartData = await chartsService.getById(id, token, i18n.language);
          setChart(chartData);
          clearInterval(pollInterval);
        } else {
          // Update progress
          setChart((prev) => (prev ? { ...prev, progress: status.progress } : null));
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chart, id]);

  async function loadChart() {
    try {
      const token = getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      if (!id) {
        setError(t('chartDetail.errors.noId', { defaultValue: 'Birth chart ID not provided' }));
        return;
      }

      const chartData = await chartsService.getById(id, token, i18n.language);
      setChart(chartData);

      // Track chart detail viewed
      amplitudeService.track('chart_detail_viewed', {
        chart_id: id,
        has_interpretations: false, // Interpretations loaded separately
        is_own_chart: true, // User's own chart (not public)
        house_system: chartData.house_system,
        source: 'chart_detail_page',
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('chartDetail.errors.loadError', { defaultValue: 'Error loading birth chart' })
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function loadInterpretations() {
    try {
      const token = getToken();
      if (!token || !id) return;

      // Skip loading if email not verified (will get 403)
      if (!isEmailVerified) {
        console.log('Skipping interpretations - email not verified');
        return;
      }

      setIsLoadingInterpretations(true);

      // Track interpretation generation started
      amplitudeService.track('interpretation_generation_started', {
        chart_id: id,
        interpretation_type: 'rag',
        source: 'chart_detail_page',
      });

      const startTime = Date.now();
      const data = await interpretationsService.getByChartId(id, token, i18n.language);
      const generationTime = Date.now() - startTime;

      setInterpretations(data);

      // Track interpretation generated
      amplitudeService.track('interpretation_generated', {
        chart_id: id,
        interpretation_type: 'rag',
        generation_time_ms: generationTime,
        used_cache: false, // TODO: Add cache indicator from API
        source: 'chart_detail_page',
      });
    } catch (err) {
      // Check if it's a 403 email verification error
      if (err instanceof Error && err.message.includes('403')) {
        console.log('Interpretations require email verification');

        // Track interpretation failure
        amplitudeService.track('interpretation_generation_failed', {
          chart_id: id || '',
          error_type: 'email_not_verified',
          source: 'chart_detail_page',
        });
        return;
      }

      // Track interpretation failure
      amplitudeService.track('interpretation_generation_failed', {
        chart_id: id || '',
        error_type: err instanceof Error ? err.name : 'unknown_error',
        source: 'chart_detail_page',
      });

      // Silently fail - interpretations are optional
      console.error('Failed to load interpretations:', err);
    } finally {
      setIsLoadingInterpretations(false);
    }
  }

  // Handle modal close - reload interpretations in case user verified email
  function handleVerificationModalClose(open: boolean) {
    setShowVerificationModal(open);
    // If modal is closing, try to reload interpretations
    // (user might have verified email in another tab)
    if (!open) {
      loadInterpretations();
    }
  }

  // Track tab changes for Amplitude
  function handleTabChange(newTab: string) {
    amplitudeService.track('interpretation_tab_changed', {
      tab_name: newTab,
      previous_tab: currentTab,
      chart_id: id || '',
      source: 'chart_detail_page',
    });
    setCurrentTab(newTab);
  }

  // Regenerate interpretations (forces new generation, used for language change)
  async function handleRegenerateInterpretations() {
    if (!isEmailVerified) {
      requireEmailVerification(
        () => {},
        t('chartDetail.interpretations', { defaultValue: 'AI Interpretations' })
      );
      return;
    }

    try {
      const token = getToken();
      if (!token || !id) return;

      setIsLoadingInterpretations(true);
      const data = await interpretationsService.regenerate(id, token);
      setInterpretations(data);
    } catch (err) {
      console.error('Failed to regenerate interpretations:', err);
    } finally {
      setIsLoadingInterpretations(false);
    }
  }

  // Helper to extract content from interpretation item (handles both string and object formats)
  function extractContent(item: unknown): string {
    if (typeof item === 'string') return item;
    if (item && typeof item === 'object' && 'content' in item) {
      return (item as { content: string }).content;
    }
    return '';
  }

  // Helper to get interpretations content from RAG format
  function getCurrentInterpretations(): {
    planets?: Record<string, string>;
    houses?: Record<string, string>;
    aspects?: Record<string, string>;
    arabic_parts?: Record<string, string>;
  } | null {
    if (!interpretations) return null;

    return {
      planets: Object.fromEntries(
        Object.entries(interpretations.planets).map(([key, item]) => [key, extractContent(item)])
      ),
      houses: Object.fromEntries(
        Object.entries(interpretations.houses).map(([key, item]) => [key, extractContent(item)])
      ),
      aspects: Object.fromEntries(
        Object.entries(interpretations.aspects).map(([key, item]) => [key, extractContent(item)])
      ),
      arabic_parts: interpretations.arabic_parts
        ? Object.fromEntries(
            Object.entries(interpretations.arabic_parts).map(([key, item]) => [
              key,
              extractContent(item),
            ])
          )
        : undefined,
    };
  }

  // Helper to extract RAG sources from interpretation item (handles both formats)
  function extractRAGSources(item: unknown): RAGSourceInfo[] {
    if (item && typeof item === 'object' && 'rag_sources' in item) {
      return (item as { rag_sources: RAGSourceInfo[] }).rag_sources || [];
    }
    return [];
  }

  // Helper to get RAG sources for interpretations
  function getRAGSources(): {
    planets?: Record<string, RAGSourceInfo[]>;
    houses?: Record<string, RAGSourceInfo[]>;
    aspects?: Record<string, RAGSourceInfo[]>;
  } | null {
    if (!interpretations) return null;

    return {
      planets: Object.fromEntries(
        Object.entries(interpretations.planets).map(([key, item]) => [key, extractRAGSources(item)])
      ),
      houses: Object.fromEntries(
        Object.entries(interpretations.houses).map(([key, item]) => [key, extractRAGSources(item)])
      ),
      aspects: Object.fromEntries(
        Object.entries(interpretations.aspects).map(([key, item]) => [key, extractRAGSources(item)])
      ),
    };
  }

  async function handleDelete() {
    if (!confirm(t('dashboard.confirmDelete'))) {
      return;
    }

    try {
      const token = getToken();
      if (!token || !id) return;

      await chartsService.delete(id, token);
      navigate('/charts');
    } catch (err) {
      alert(t('dashboard.deleteError'));
    }
  }

  async function handleExportPDF() {
    if (!id || !chart) return;

    const token = getToken();
    if (!token) {
      navigate('/login');
      return;
    }

    // Require email verification for PDF export
    if (!isEmailVerified) {
      requireEmailVerification(
        () => {},
        t('chartDetail.pdf.export', { defaultValue: 'Export PDF' })
      );
      return;
    }

    try {
      setPdfStatus('generating');
      setPdfError(null);

      // Step 1: Trigger PDF generation
      await generateChartPDF(id, token);

      // Step 2: Poll for completion
      const pollInterval = setInterval(async () => {
        try {
          const status = await getPDFStatus(id, token);

          if (status.status === 'ready') {
            clearInterval(pollInterval);
            setPdfStatus('ready');

            // Step 3: Auto-download when ready
            await downloadChartPDF(id, token, chart.person_name);

            // Reset to idle after download (2 seconds delay)
            setTimeout(() => setPdfStatus('idle'), 2000);
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            setPdfStatus('failed');
            setPdfError(
              status.message ||
                t('chartDetail.pdf.generateError', { defaultValue: 'Error generating PDF' })
            );
          }
          // If status is 'generating', continue polling
        } catch (err) {
          clearInterval(pollInterval);
          setPdfStatus('failed');
          setPdfError(
            err instanceof Error
              ? err.message
              : t('chartDetail.pdf.statusError', { defaultValue: 'Error checking PDF status' })
          );
        }
      }, 2000); // Poll every 2 seconds

      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (pdfStatus === 'generating') {
          setPdfStatus('failed');
          setPdfError(t('chartDetail.pdf.timeout', { defaultValue: 'PDF generation timed out' }));
        }
      }, 300000); // 5 minutes
    } catch (err) {
      setPdfStatus('failed');
      setPdfError(
        err instanceof Error
          ? err.message
          : t('chartDetail.pdf.startError', { defaultValue: 'Error starting PDF generation' })
      );
    }
  }

  function getAscendantSign(): string {
    if (!chart?.chart_data) return '';
    const ascLongitude = chart.chart_data.ascendant;
    const signIndex = Math.floor(ascLongitude / 30);
    const signs = [
      'Aries',
      'Taurus',
      'Gemini',
      'Cancer',
      'Leo',
      'Virgo',
      'Libra',
      'Scorpio',
      'Sagittarius',
      'Capricorn',
      'Aquarius',
      'Pisces',
    ];
    return signs[signIndex];
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <p className="text-body text-muted-foreground">
            {t('chartDetail.loading', { defaultValue: 'Loading birth chart...' })}
          </p>
        </div>
      </div>
    );
  }

  // Show processing state
  if (chart && chart.status === 'processing') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <h2 className="text-headline-3 font-display mb-astro-sm">
            {t('chartDetail.generating', { defaultValue: 'Generating your Birth Chart...' })}
          </h2>
          <p className="text-body text-muted-foreground mb-astro-md">
            {t('chartDetail.generatingDesc', {
              defaultValue:
                'We are calculating planetary positions and generating astrological interpretations.',
            })}
          </p>
          <div className="w-full bg-muted rounded-full h-2 mb-astro-sm">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${chart.progress}%` }}
            />
          </div>
          <p className="text-caption text-muted-foreground">
            {chart.progress}% {t('chartDetail.complete', { defaultValue: 'complete' })}
          </p>
        </div>
      </div>
    );
  }

  // Show failed state
  if (chart && chart.status === 'failed') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center max-w-md">
          <h2 className="text-headline-3 font-display mb-astro-sm text-destructive">
            {t('chartDetail.errors.generateFailed', { defaultValue: 'Error Generating Chart' })}
          </h2>
          <p className="text-body text-muted-foreground mb-astro-md">
            {chart.error_message ||
              t('chartDetail.errors.processError', {
                defaultValue: 'An error occurred while processing your birth chart.',
              })}
          </p>
          <Button onClick={() => navigate('/charts')}>
            {t('chartDetail.backToCharts', { defaultValue: 'Back to Charts' })}
          </Button>
        </div>
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center px-4">
        <div className="max-w-md w-full animate-fade-in">
          <div className="bg-destructive/10 border border-destructive/20 rounded-astro-lg p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">{t('common.error')}</h2>
            <p className="text-sm text-muted-foreground mb-4">
              {error || t('chartDetail.errors.notFound', { defaultValue: 'Birth chart not found' })}
            </p>
            <Button asChild className="w-full">
              <Link to="/charts">
                {t('chartDetail.backToMyCharts', { defaultValue: 'Back to My Charts' })}
              </Link>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const ascSign = getAscendantSign();
  const ascDegree = chart.chart_data?.ascendant ? Math.floor(chart.chart_data.ascendant % 30) : 0;

  // Get Sun and Moon signs for the "Big Three"
  function getSunSign(): string {
    if (!chart) return '';
    const sun = chart.chart_data?.planets.find((p) => p.name === 'Sun');
    return sun?.sign || '';
  }

  function getMoonSign(): string {
    if (!chart) return '';
    const moon = chart.chart_data?.planets.find((p) => p.name === 'Moon');
    return moon?.sign || '';
  }

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
                to="/dashboard"
                className="hover:opacity-80 transition-all duration-200 flex-shrink-0"
                aria-label={t('common.back')}
              >
                <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
              </Link>
              <div>
                <h1 className="text-h3 font-display text-foreground">{chart.person_name}</h1>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone || 'UTC', true)} •{' '}
                  {chart.city}
                  {chart.country && `, ${chart.country}`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <LanguageSelector />
              <ThemeToggle />

              {/* PDF Export Button */}
              <Button
                variant={pdfStatus === 'ready' ? 'default' : 'outline'}
                size="sm"
                onClick={handleExportPDF}
                disabled={pdfStatus === 'generating'}
                className={pdfStatus === 'failed' ? 'border-destructive text-destructive' : ''}
              >
                {pdfStatus === 'generating' ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    {t('chartDetail.generatingPDF')}
                  </>
                ) : pdfStatus === 'ready' ? (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    {t('chartDetail.pdf.downloaded', { defaultValue: 'PDF Downloaded!' })}
                  </>
                ) : pdfStatus === 'failed' ? (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    {t('chartDetail.pdf.retry', { defaultValue: 'Try Again' })}
                  </>
                ) : (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    {t('chartDetail.pdf.export', { defaultValue: 'Export PDF' })}
                  </>
                )}
              </Button>

              {/* Edit Button */}
              <Button variant="outline" size="sm" onClick={() => navigate(`/charts/${id}/edit`)}>
                <Edit className="mr-2 h-4 w-4" />
                {t('common.edit', { defaultValue: 'Edit' })}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                {t('common.delete')}
              </Button>
              <Button asChild variant="secondary" size="sm">
                <Link to="/charts">
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
        {/* Chart Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">
                {t('chartDetail.ascendant')}
              </p>
              <p className="text-h3 font-display text-foreground flex items-center gap-2">
                {getSignSymbol(ascSign)} {translateSign(ascSign)} {ascDegree}°
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">
                {t('newChart.houseSystem')}
              </p>
              <p className="text-h3 font-display text-foreground capitalize">
                {chart.house_system}
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">
                {t('newChart.zodiacType')}
              </p>
              <p className="text-h3 font-display text-foreground capitalize">{chart.zodiac_type}</p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="visual" className="w-full" onValueChange={handleTabChange}>
          <TabsList className="w-full justify-start mb-6">
            <TabsTrigger value="visual">{t('chartDetail.tabs.visual')}</TabsTrigger>
            <TabsTrigger value="planets">
              {t('chartDetail.tabs.planets')} ({chart.chart_data?.planets.length || 0})
            </TabsTrigger>
            <TabsTrigger value="houses">{t('chartDetail.tabs.houses')} (12)</TabsTrigger>
            <TabsTrigger value="aspects">
              {t('chartDetail.tabs.aspects')} ({chart.chart_data?.aspects.length || 0})
            </TabsTrigger>
            <TabsTrigger value="arabic-parts">
              {t('chartDetail.tabs.arabicParts')} (
              {chart.chart_data?.arabic_parts
                ? Object.keys(chart.chart_data.arabic_parts).length
                : 0}
              )
            </TabsTrigger>
            <TabsTrigger value="growth">
              {t('chartDetail.tabs.growth', { defaultValue: 'Growth' })}
            </TabsTrigger>
            <TabsTrigger value="longevity">
              {t('chartDetail.tabs.longevity', { defaultValue: 'Longevity' })}
            </TabsTrigger>
          </TabsList>

          {/* Tab Content: Visual */}
          <TabsContent value="visual" className="mt-0">
            {chart.chart_data && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display">
                    {t('chartDetail.birthChart', { defaultValue: 'Birth Chart' })}
                  </CardTitle>
                  <CardDescription>
                    {t('chartDetail.birthChartDesc', {
                      defaultValue: 'Complete visualization of your birth sky',
                    })}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  {/* Big Three Summary */}
                  <div>
                    <h3 className="text-h4 font-display mb-4">
                      {t('chartDetail.astroEssence', { defaultValue: 'Astrological Essence' })}
                    </h3>
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
                        <span className="text-3xl" title={t('chartDetail.sun')}>
                          ☉
                        </span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourEssence', {
                                defaultValue: 'Your essence',
                              })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.sunTooltip', {
                                defaultValue:
                                  'The Sun represents your core identity, life purpose and vitality. It is the nucleus of your conscious personality.',
                              })}
                              side="top"
                            />
                          </div>
                          <p className="text-lg font-semibold text-foreground">
                            {translatePlanet('Sun')} {t('chartDetail.in', { defaultValue: 'in' })}{' '}
                            {getSignSymbol(sunSign)} {translateSign(sunSign)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('chartDetail.bigThree.sunDesc', {
                          defaultValue: 'Identity and life purpose',
                        })}
                      </p>
                    </div>

                    {/* Moon */}
                    <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-3xl" title={t('chartDetail.moon')}>
                          ☽
                        </span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourEmotions', {
                                defaultValue: 'Your emotions',
                              })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.moonTooltip', {
                                defaultValue:
                                  'The Moon represents your emotions, instinctive needs and unconscious reactions. It reveals how you feel safe and comfortable.',
                              })}
                              side="top"
                            />
                          </div>
                          <p className="text-lg font-semibold text-foreground">
                            {translatePlanet('Moon')} {t('chartDetail.in', { defaultValue: 'in' })}{' '}
                            {getSignSymbol(moonSign)} {translateSign(moonSign)}
                          </p>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {t('chartDetail.bigThree.moonDesc', {
                          defaultValue: 'Emotional world and needs',
                        })}
                      </p>
                    </div>

                    {/* Ascendant */}
                    <div className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 rounded-lg p-4">
                      <div className="flex items-center gap-3 mb-2">
                        <span
                          className="text-3xl font-bold text-primary"
                          title={t('chartDetail.ascendant')}
                        >
                          ASC
                        </span>
                        <div>
                          <div className="flex items-center gap-1">
                            <p className="text-xs text-muted-foreground uppercase tracking-wide">
                              {t('chartDetail.bigThree.yourAppearance', {
                                defaultValue: 'Your appearance',
                              })}
                            </p>
                            <InfoTooltip
                              content={t('chartDetail.bigThree.ascTooltip', {
                                defaultValue:
                                  'The Ascendant is the sign that was rising on the eastern horizon at your birth. It represents your social mask and first impression.',
                              })}
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

                  {/* Chart Wheel (PRIMEIRO) */}
                  <div>
                    <h3 className="text-h4 font-display mb-4">
                      {t('chartDetail.sections.chartWheel', { defaultValue: 'Roda do Mapa Natal' })}
                    </h3>
                    <ChartWheelAstro chartData={chart.chart_data} width={600} height={600} />
                  </div>

                  {/* Temperament (SEGUNDO) */}
                  {chart.chart_data.temperament && (
                    <div>
                      <h3 className="text-h4 font-display mb-4">
                        {t('chartDetail.sections.temperament', {
                          defaultValue: 'Cálculo Final do Temperamento',
                        })}
                      </h3>
                      <TemperamentDisplay temperament={chart.chart_data.temperament} />
                    </div>
                  )}

                  {/* Mentality (Issue #57) */}
                  {chart.chart_data.mentality && (
                    <div>
                      <h3 className="text-h4 font-display mb-4">
                        {t('chartDetail.sections.mentality', {
                          defaultValue: 'Análise de Mentalidade',
                        })}
                      </h3>
                      <MentalityCard mentality={chart.chart_data.mentality} />
                    </div>
                  )}

                  {/* Lord of Nativity */}
                  {chart.chart_data.lord_of_nativity && (
                    <div>
                      <LordOfNativity lordOfNativity={chart.chart_data.lord_of_nativity} />
                    </div>
                  )}

                  {/* Lunar and Solar Phases - with explicit labels */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {chart.chart_data.lunar_phase && (
                      <div>
                        <h3 className="text-h4 font-display mb-4">
                          {t('chartDetail.lunarPhase', { defaultValue: 'Lunar Phase' })}
                        </h3>
                        <LunarPhase lunarPhase={chart.chart_data.lunar_phase} />
                      </div>
                    )}
                    {chart.chart_data.solar_phase && (
                      <div>
                        <h3 className="text-h4 font-display mb-4">
                          {t('chartDetail.solarPhase', { defaultValue: 'Solar Phase' })}
                        </h3>
                        <SolarPhase solarPhase={chart.chart_data.solar_phase} />
                      </div>
                    )}
                  </div>

                  {/* Sect Analysis */}
                  {chart.chart_data.sect_analysis && (
                    <div>
                      <h3 className="text-h4 font-display mb-4">
                        {t('components.sect.title', { defaultValue: 'Sect Analysis' })}
                      </h3>
                      <SectAnalysis sectData={chart.chart_data.sect_analysis} />
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Planets */}
          <TabsContent value="planets" className="mt-0">
            {chart.chart_data && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.planetPositions', { defaultValue: 'Planetary Positions' })}
                    <InfoTooltip
                      content={t('chartDetail.planetPositionsTooltip', {
                        defaultValue:
                          'Exact planetary positions calculated with Swiss Ephemeris (precision < 1 arcsecond). Includes longitude, latitude, speed and retrograde state.',
                      })}
                      side="right"
                    />
                  </CardTitle>
                  {interpretations && (
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="flex items-center gap-1.5">
                        <Sparkles className="h-3 w-3" />
                        {t('rag.badge', 'Aprimorado com RAG')}
                      </Badge>
                      <InfoTooltip
                        content={t(
                          'rag.tooltipLong',
                          'RAG (Retrieval-Augmented Generation) combina inteligência artificial com uma base de conhecimento de livros clássicos de astrologia, resultando em interpretações mais precisas e fundamentadas na tradição astrológica.'
                        )}
                        side="right"
                      />
                    </CardDescription>
                  )}
                  {interpretations?.language && (
                    <div className="mt-3">
                      <InterpretationLanguageNotice
                        interpretationLanguage={interpretations.language}
                        onRegenerate={handleRegenerateInterpretations}
                        isRegenerating={isLoadingInterpretations}
                      />
                    </div>
                  )}
                  {!interpretations && !isLoadingInterpretations && !isEmailVerified && (
                    <CardDescription className="flex items-center gap-2 mt-2 text-amber-600 dark:text-amber-400">
                      <Sparkles className="h-4 w-4" />
                      {t('chartDetail.verifyForInterpretations', {
                        defaultValue: 'Verify your email to unlock AI interpretations',
                      })}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <PlanetList
                    planets={chart.chart_data.planets}
                    showOnlyClassical={true}
                    interpretations={getCurrentInterpretations()?.planets}
                    ragSources={getRAGSources()?.planets}
                    lordOfNativity={chart.chart_data.lord_of_nativity}
                  />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Houses */}
          <TabsContent value="houses" className="mt-0">
            {chart.chart_data && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.astroHouses', { defaultValue: 'Astrological Houses' })}
                    <InfoTooltip
                      content={t('chartDetail.astroHousesTooltip', {
                        defaultValue:
                          'The 12 houses divide the sky into sectors representing life areas. System used: {{system}}. Each house has a cusp (beginning) and a planetary ruler.',
                        system: chart.house_system,
                      })}
                      side="right"
                    />
                  </CardTitle>
                  {interpretations && (
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="flex items-center gap-1.5">
                        <Sparkles className="h-3 w-3" />
                        {t('rag.badge', 'Aprimorado com RAG')}
                      </Badge>
                      <InfoTooltip
                        content={t(
                          'rag.tooltipLong',
                          'RAG (Retrieval-Augmented Generation) combina inteligência artificial com uma base de conhecimento de livros clássicos de astrologia, resultando em interpretações mais precisas e fundamentadas na tradição astrológica.'
                        )}
                        side="right"
                      />
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <HouseTable
                    houses={chart.chart_data.houses}
                    interpretations={getCurrentInterpretations()?.houses}
                    ragSources={getRAGSources()?.houses}
                  />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Aspects */}
          <TabsContent value="aspects" className="mt-0">
            {chart.chart_data && (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.planetaryAspects', { defaultValue: 'Planetary Aspects' })}
                    <InfoTooltip
                      content={t('chartDetail.planetaryAspectsTooltip', {
                        defaultValue:
                          'Aspects are geometric angles between planets that reveal how they interact. We detect major aspects (conjunction, opposition, trine, square, sextile) and minor (quincunx, semisextile, etc.) with configurable orbs.',
                      })}
                      side="right"
                    />
                  </CardTitle>
                  {interpretations && (
                    <CardDescription className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="flex items-center gap-1.5">
                        <Sparkles className="h-3 w-3" />
                        {t('rag.badge', 'Aprimorado com RAG')}
                      </Badge>
                      <InfoTooltip
                        content={t(
                          'rag.tooltipLong',
                          'RAG (Retrieval-Augmented Generation) combina inteligência artificial com uma base de conhecimento de livros clássicos de astrologia, resultando em interpretações mais precisas e fundamentadas na tradição astrológica.'
                        )}
                        side="right"
                      />
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <AspectGrid
                    aspects={chart.chart_data.aspects}
                    interpretations={getCurrentInterpretations()?.aspects}
                    ragSources={getRAGSources()?.aspects}
                  />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Arabic Parts */}
          <TabsContent value="arabic-parts" className="mt-0">
            {chart.chart_data?.arabic_parts ? (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-h3 font-display flex items-center gap-2">
                    {t('chartDetail.arabicPartsLots', { defaultValue: 'Arabic Parts (Lots)' })}
                    <InfoTooltip
                      content={t('chartDetail.arabicPartsTooltip', {
                        defaultValue:
                          'Arabic Parts (or Lots) are mathematically calculated points from planetary positions. They reveal specific life themes according to Hellenistic tradition.',
                      })}
                      side="right"
                    />
                  </CardTitle>
                  <CardDescription>
                    {t('chartDetail.arabicPartsDesc', {
                      defaultValue: 'Sensitive points from Hellenistic astrological tradition',
                    })}
                  </CardDescription>
                  {interpretations && (
                    <div className="flex items-center gap-2 mt-2">
                      <Badge variant="secondary" className="flex items-center gap-1.5">
                        <Sparkles className="h-3 w-3" />
                        {t('rag.badge', 'Aprimorado com RAG')}
                      </Badge>
                      <InfoTooltip
                        content={t(
                          'rag.tooltipLong',
                          'RAG (Retrieval-Augmented Generation) combina inteligência artificial com uma base de conhecimento de livros clássicos de astrologia, resultando em interpretações mais precisas e fundamentadas na tradição astrológica.'
                        )}
                        side="right"
                      />
                    </div>
                  )}
                </CardHeader>
                <CardContent>
                  <ArabicPartsTable
                    parts={chart.chart_data.arabic_parts}
                    interpretations={getCurrentInterpretations()?.arabic_parts}
                  />

                  {/* Educational Section */}
                  <div className="mt-8 p-6 bg-muted/50 rounded-lg space-y-4">
                    <h4 className="text-lg font-semibold text-foreground flex items-center gap-2">
                      📚{' '}
                      {t('chartDetail.arabicParts.aboutTitle', {
                        defaultValue: 'About Arabic Parts',
                      })}
                    </h4>

                    <div className="space-y-3 text-sm text-muted-foreground">
                      <p>
                        <strong className="text-foreground">
                          {t('chartDetail.arabicParts.whatAre', { defaultValue: 'What they are:' })}
                        </strong>{' '}
                        {t('chartDetail.arabicParts.whatAreDesc', {
                          defaultValue:
                            'Arabic Parts (also called "Lots" in Hellenistic tradition) are mathematically calculated points from planetary and angular positions. They function as "virtual planets", revealing specific life themes.',
                        })}
                      </p>

                      <p>
                        <strong className="text-foreground">
                          {t('chartDetail.arabicParts.formula', {
                            defaultValue: 'General formula:',
                          })}
                        </strong>{' '}
                        {t('chartDetail.arabicParts.formulaDesc', {
                          defaultValue:
                            'Part = Ascendant + Planet1 - Planet2 (all in degrees 0-360). Formulas differ between day charts (☀️ Sun above horizon) and night charts (🌙 Sun below horizon).',
                        })}
                      </p>

                      <p>
                        <strong className="text-foreground">
                          {t('chartDetail.arabicParts.importance', { defaultValue: 'Importance:' })}
                        </strong>{' '}
                        {t('chartDetail.arabicParts.importanceDesc', {
                          defaultValue:
                            'The house where a Part falls and the aspects it receives from natal planets are significant. The Lot of Fortune is especially important - medieval astrologers treated it with the same importance as the Ascendant.',
                        })}
                      </p>

                      <p>
                        <strong className="text-foreground">
                          {t('chartDetail.arabicParts.origin', { defaultValue: 'Origin:' })}
                        </strong>{' '}
                        {t('chartDetail.arabicParts.originDesc', {
                          defaultValue:
                            'Developed in Hellenistic astrology (Greece/Rome, 100 BC - 600 AD) and expanded by medieval Arab astrologers (700-1400 AD). There are hundreds of cataloged Parts, but the 4 presented here are the most fundamental.',
                        })}
                      </p>

                      <div className="pt-4 border-t border-border">
                        <p className="text-xs italic">
                          <strong>
                            {t('chartDetail.arabicParts.technicalNote', {
                              defaultValue: 'Technical note:',
                            })}
                          </strong>{' '}
                          {t('chartDetail.arabicParts.technicalNoteDesc', {
                            defaultValue:
                              'Your chart is {{sect}} ({{sectDesc}}), so the formulas used follow the sect rules of Hellenistic tradition.',
                            sect:
                              chart.chart_data.sect === 'diurnal'
                                ? t('chartDetail.diurnal', { defaultValue: 'diurnal' })
                                : t('chartDetail.nocturnal', { defaultValue: 'nocturnal' }),
                            sectDesc:
                              chart.chart_data.sect === 'diurnal'
                                ? t('chartDetail.sunAbove', { defaultValue: 'Sun above horizon' })
                                : t('chartDetail.sunBelow', { defaultValue: 'Sun below horizon' }),
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardContent className="pt-6 text-center text-muted-foreground">
                  <p>
                    {t('chartDetail.arabicParts.notAvailable', {
                      defaultValue: 'Arabic Parts not available for this chart.',
                    })}
                  </p>
                  <p className="text-sm mt-2">
                    {t('chartDetail.arabicParts.willBeCalculated', {
                      defaultValue:
                        'Parts will be automatically calculated for charts created or updated after this feature.',
                    })}
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Tab Content: Growth */}
          <TabsContent value="growth" className="mt-0">
            {id && (
              <GrowthSuggestions chartId={id} initialGrowth={interpretations?.growth ?? null} />
            )}
          </TabsContent>

          {/* Tab Content: Longevity (Premium) - Lazy loaded */}
          <TabsContent value="longevity" className="mt-0">
            <Suspense
              fallback={
                <div className="space-y-6">
                  <Skeleton className="h-24 w-full" />
                  <Skeleton className="h-32 w-full" />
                  <div className="grid md:grid-cols-2 gap-6">
                    <Skeleton className="h-80 w-full" />
                    <Skeleton className="h-80 w-full" />
                  </div>
                </div>
              }
            >
              <LongevityAnalysis longevity={chart.chart_data?.longevity ?? null} />
            </Suspense>
          </TabsContent>
        </Tabs>

        {/* Notes */}
        {chart.notes && (
          <Card className="mt-6 border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-h4 font-display">{t('chartDetail.notes')}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-body text-muted-foreground whitespace-pre-wrap">{chart.notes}</p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Email Verification Modal */}
      <EmailVerificationModal
        open={showVerificationModal}
        onOpenChange={handleVerificationModalClose}
        featureName={verificationFeatureName}
        onCheckStatus={checkVerificationStatus}
        isCheckingStatus={isCheckingStatus}
      />
    </div>
  );
}
