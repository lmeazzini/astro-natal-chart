/**
 * Chart Detail Page - complete birth chart visualization
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { chartsService, BirthChart } from '../services/charts';
import { ChartWheel } from '../components/ChartWheel';
import { PlanetList } from '../components/PlanetList';
import { HouseTable } from '../components/HouseTable';
import { AspectGrid } from '../components/AspectGrid';
import { getSignSymbol } from '../utils/astro';

const TOKEN_KEY = 'astro_access_token';

export function ChartDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [chart, setChart] = useState<BirthChart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState<'visual' | 'planets' | 'houses' | 'aspects'>('visual');

  useEffect(() => {
    loadChart();
  }, [id]);

  async function loadChart() {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        navigate('/login');
        return;
      }

      if (!id) {
        setError('ID do mapa natal não fornecido');
        return;
      }

      const chartData = await chartsService.getById(id, token);
      setChart(chartData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar mapa natal');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete() {
    if (!confirm('Tem certeza que deseja excluir este mapa natal?')) {
      return;
    }

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token || !id) return;

      await chartsService.delete(id, token);
      navigate('/charts');
    } catch (err) {
      alert('Erro ao excluir mapa');
    }
  }

  function formatDateTime(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  function getAscendantSign(): string {
    if (!chart?.chart_data) return '';
    const ascLongitude = chart.chart_data.ascendant;
    const signIndex = Math.floor(ascLongitude / 30);
    const signs = [
      'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
      'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ];
    return signs[signIndex];
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando mapa natal...</p>
        </div>
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              Erro
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              {error || 'Mapa natal não encontrado'}
            </p>
            <Link
              to="/charts"
              className="inline-block w-full text-center py-2 px-4 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition"
            >
              Voltar para Meus Mapas
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const ascSign = getAscendantSign();
  const ascDegree = chart.chart_data?.ascendant
    ? Math.floor((chart.chart_data.ascendant % 30))
    : 0;

  // Get Sun and Moon signs for the "Big Three"
  function getSunSign(): string {
    if (!chart) return '';
    const sun = chart.chart_data?.planets.find(p => p.name === 'Sun');
    return sun?.sign || '';
  }

  function getMoonSign(): string {
    if (!chart) return '';
    const moon = chart.chart_data?.planets.find(p => p.name === 'Moon');
    return moon?.sign || '';
  }

  const sunSign = getSunSign();
  const moonSign = getMoonSign();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="bg-card border-b border-border sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                {chart.person_name}
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                {formatDateTime(chart.birth_datetime)} • {chart.city}
                {chart.country && `, ${chart.country}`}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={handleDelete}
                className="px-4 py-2 text-sm text-destructive hover:bg-destructive/10 rounded-md transition"
              >
                Excluir
              </button>
              <Link
                to="/charts"
                className="px-4 py-2 text-sm bg-secondary text-secondary-foreground rounded-md hover:opacity-90 transition"
              >
                ← Voltar
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* Chart Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Ascendente</p>
            <p className="text-2xl font-semibold text-foreground flex items-center gap-2">
              {getSignSymbol(ascSign)} {ascSign} {ascDegree}°
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Sistema de Casas</p>
            <p className="text-2xl font-semibold text-foreground capitalize">
              {chart.house_system}
            </p>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground mb-1">Tipo de Zodíaco</p>
            <p className="text-2xl font-semibold text-foreground capitalize">
              {chart.zodiac_type}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-border overflow-x-auto">
          <button
            onClick={() => setActiveTab('visual')}
            className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'visual'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Visualização
          </button>
          <button
            onClick={() => setActiveTab('planets')}
            className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'planets'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Planetas ({chart.chart_data?.planets.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('houses')}
            className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'houses'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Casas (12)
          </button>
          <button
            onClick={() => setActiveTab('aspects')}
            className={`px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === 'aspects'
                ? 'text-primary border-b-2 border-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Aspectos ({chart.chart_data?.aspects.length || 0})
          </button>
        </div>

        {/* Tab Content */}
        <div className="bg-card border border-border rounded-lg p-6">
          {activeTab === 'visual' && chart.chart_data && (
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-6">
                Mapa Natal
              </h2>

              {/* Big Three Summary */}
              <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Sun */}
                <div className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border border-yellow-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl" title="Sol">
                      ☉
                    </span>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        Sua essência
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        Sol em {getSignSymbol(sunSign)} {sunSign}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Identidade e propósito de vida
                  </p>
                </div>

                {/* Moon */}
                <div className="bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl" title="Lua">
                      ☽
                    </span>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        Suas emoções
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        Lua em {getSignSymbol(moonSign)} {moonSign}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Mundo emocional e necessidades
                  </p>
                </div>

                {/* Ascendant */}
                <div className="bg-gradient-to-br from-green-500/10 to-teal-500/10 border border-green-500/20 rounded-lg p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-3xl font-bold text-primary" title="Ascendente">
                      ASC
                    </span>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        Sua aparência
                      </p>
                      <p className="text-lg font-semibold text-foreground">
                        {getSignSymbol(ascSign)} {ascSign}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Como os outros te veem
                  </p>
                </div>
              </div>

              <ChartWheel
                planets={chart.chart_data.planets}
                houses={chart.chart_data.houses}
                aspects={chart.chart_data.aspects}
                ascendant={chart.chart_data.ascendant}
                midheaven={chart.chart_data.midheaven}
              />
            </div>
          )}

          {activeTab === 'planets' && chart.chart_data && (
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-6">
                Posições Planetárias
              </h2>
              <PlanetList planets={chart.chart_data.planets} />
            </div>
          )}

          {activeTab === 'houses' && chart.chart_data && (
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-6">
                Casas Astrológicas
              </h2>
              <HouseTable houses={chart.chart_data.houses} />
            </div>
          )}

          {activeTab === 'aspects' && chart.chart_data && (
            <div>
              <h2 className="text-xl font-semibold text-foreground mb-6">
                Aspectos Planetários
              </h2>
              <AspectGrid aspects={chart.chart_data.aspects} />
            </div>
          )}
        </div>

        {/* Notes */}
        {chart.notes && (
          <div className="mt-6 bg-card border border-border rounded-lg p-6">
            <h3 className="text-lg font-semibold text-foreground mb-3">
              Anotações
            </h3>
            <p className="text-sm text-muted-foreground whitespace-pre-wrap">
              {chart.notes}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
