/**
 * Birth Charts list page
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { chartsService, BirthChart } from '../services/charts';
import { interpretationsService } from '../services/interpretations';
import { getToken } from '../services/api';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { EmptyState } from '@/components/ui/empty-state';
import { BigThreeBadge } from '@/components/ui/big-three-badge';
import { AlertCircle, Trash2, Plus, ArrowLeft, Sparkles, RefreshCw, Pencil } from 'lucide-react';
import { formatBirthDateTime } from '@/utils/datetime';
import { EducationalBanner } from '@/components/EducationalBanner';

export function ChartsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const [charts, setCharts] = useState<BirthChart[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [recalculatingChartId, setRecalculatingChartId] = useState<string | null>(null);

  useEffect(() => {
    loadCharts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadCharts() {
    try {
      const token = getToken();
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await chartsService.list(token);
      setCharts(response.charts);
    } catch (err) {
      setError(err instanceof Error ? err.message : t('dashboard.deleteError'));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete(chartId: string) {
    if (!confirm(t('dashboard.confirmDelete'))) {
      return;
    }

    try {
      const token = getToken();
      if (!token) return;

      await chartsService.delete(chartId, token);
      setCharts(charts.filter((c) => c.id !== chartId));
    } catch (err) {
      alert(t('dashboard.deleteError'));
    }
  }

  async function handleRecalculate(chartId: string) {
    try {
      const token = getToken();
      if (!token) return;

      setRecalculatingChartId(chartId);
      setError('');

      // Recalculate chart data
      const updatedChart = await chartsService.recalculate(chartId, token);

      // Regenerate RAG interpretations (now default for all users)
      await interpretationsService.regenerate(chartId, token);

      // Update the chart in the list
      setCharts(charts.map((c) => c.id === chartId ? updatedChart : c));
    } catch (err) {
      setError(err instanceof Error ? err.message : t('charts.recalculateError', { defaultValue: 'Erro ao recalcular mapa' }));
    } finally {
      setRecalculatingChartId(null);
    }
  }

  function getSignFromLongitude(longitude: number): string {
    const signIndex = Math.floor(longitude / 30);
    const signs = [
      'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
      'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ];
    return signs[signIndex] || 'N/A';
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <p className="text-body text-muted-foreground">{t('dashboard.loading', { defaultValue: 'Carregando mapas...' })}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-all duration-200"
            aria-label={t('common.back')}
          >
            <img
              src="/logo.png"
              alt="Real Astrology"
              className="h-8 w-8"
            />
            <h1 className="text-h3 font-display text-foreground">{t('dashboard.title')}</h1>
          </Link>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <ThemeToggle />
            <Button asChild>
              <Link to="/charts/new">
                <Plus className="mr-2 h-4 w-4" />
                {t('dashboard.newChart')}
              </Link>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              {t('nav.dashboard')}
            </Button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* Educational Banner */}
        <EducationalBanner
          title={t('educationalBanner.title')}
          description={t('educationalBanner.description')}
          dismissible={true}
          storageKey="educational-banner-charts"
          className="mb-6"
        />

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {charts.length === 0 ? (
          <div className="animate-fade-in">
            <EmptyState
              icon={Sparkles}
              title={t('dashboard.noCharts')}
              description={t('dashboard.noChartsSubtitle')}
              action={{
                label: t('dashboard.createFirst', { defaultValue: 'Criar Meu Primeiro Mapa' }),
                onClick: () => navigate('/charts/new'),
              }}
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
            {charts.map((chart) => (
              <Card key={chart.id} className="border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 bg-card/90 backdrop-blur-sm">
                <CardHeader className="pb-3 border-b border-border/30">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-h4 font-display">{chart.person_name}</CardTitle>
                      {chart.gender && (
                        <CardDescription className="text-sm mt-1">{chart.gender}</CardDescription>
                      )}
                    </div>
                    <div className="flex items-center gap-1 -mr-2 -mt-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(`/charts/${chart.id}/edit`)}
                        className="text-muted-foreground hover:text-foreground hover:bg-muted/50"
                        title={t('charts.edit', { defaultValue: 'Editar mapa' })}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRecalculate(chart.id)}
                        disabled={recalculatingChartId === chart.id}
                        className="text-muted-foreground hover:text-primary hover:bg-primary/10"
                        title={t('charts.recalculate', { defaultValue: 'Recalcular mapa e interpretações' })}
                      >
                        <RefreshCw className={`h-4 w-4 ${recalculatingChartId === chart.id ? 'animate-spin' : ''}`} />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(chart.id)}
                        className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        title={t('charts.delete', { defaultValue: 'Excluir mapa' })}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>
                      <strong className="text-foreground">{t('chartDetail.birthDateTime')}:</strong>{' '}
                      {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone || 'UTC', false)}
                    </p>
                    <p>
                      <strong className="text-foreground">{t('chartDetail.location')}:</strong> {chart.city}
                      {chart.country && `, ${chart.country}`}
                    </p>
                    <p>
                      <strong className="text-foreground">{t('newChart.houseSystem')}:</strong> {chart.house_system}
                    </p>
                  </div>

                  {chart.chart_data && (
                    <div className="pt-4 border-t border-border/50">
                      <p className="text-xs text-muted-foreground mb-3 font-medium">{t('chartDetail.bigThree.title')}</p>
                      <BigThreeBadge
                        sunSign={chart.chart_data.planets.find(p => p.name === 'Sun')?.sign || 'N/A'}
                        moonSign={chart.chart_data.planets.find(p => p.name === 'Moon')?.sign || 'N/A'}
                        risingSign={getSignFromLongitude(chart.chart_data.ascendant)}
                        variant="vertical"
                      />
                    </div>
                  )}

                  {chart.notes && (
                    <div className="pt-4 border-t border-border">
                      <p className="text-xs text-muted-foreground line-clamp-2">
                        {chart.notes}
                      </p>
                    </div>
                  )}
                </CardContent>

                <CardFooter>
                  <Button asChild className="w-full group">
                    <Link to={`/charts/${chart.id}`}>
                      {t('dashboard.viewChart')}
                      <ArrowLeft className="ml-2 h-4 w-4 rotate-180 transition-transform group-hover:translate-x-1" />
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
