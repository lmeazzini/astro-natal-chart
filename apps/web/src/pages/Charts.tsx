/**
 * Birth Charts list page
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { chartsService, BirthChart } from '../services/charts';
import { getSignSymbol } from '../utils/astro';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Trash2, Plus, ArrowLeft } from 'lucide-react';

const TOKEN_KEY = 'astro_access_token';

export function ChartsPage() {
  const navigate = useNavigate();

  const [charts, setCharts] = useState<BirthChart[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCharts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadCharts() {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) {
        navigate('/login');
        return;
      }

      const response = await chartsService.list(token);
      setCharts(response.charts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar mapas');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleDelete(chartId: string) {
    if (!confirm('Tem certeza que deseja excluir este mapa natal?')) {
      return;
    }

    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) return;

      await chartsService.delete(chartId, token);
      setCharts(charts.filter((c) => c.id !== chartId));
    } catch (err) {
      alert('Erro ao excluir mapa');
    }
  }

  function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Carregando mapas...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label="Voltar ao Dashboard"
          >
            <img
              src="/logo.png"
              alt="Astro"
              className="h-8 w-8"
            />
            <h1 className="text-2xl font-bold text-foreground">Astro</h1>
          </Link>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button asChild>
              <Link to="/charts/new">
                <Plus className="mr-2 h-4 w-4" />
                Novo Mapa
              </Link>
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate('/dashboard')}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Dashboard
            </Button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-7xl mx-auto py-8 px-4">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {charts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌟</div>
            <h2 className="text-2xl font-semibold text-foreground mb-2">
              Nenhum mapa natal ainda
            </h2>
            <p className="text-muted-foreground mb-6">
              Crie seu primeiro mapa natal para começar sua jornada astrológica
            </p>
            <Button asChild size="lg">
              <Link to="/charts/new">
                <Plus className="mr-2 h-4 w-4" />
                Criar Meu Primeiro Mapa
              </Link>
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {charts.map((chart) => (
              <Card key={chart.id} className="hover:shadow-lg transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{chart.person_name}</CardTitle>
                      {chart.gender && (
                        <CardDescription>{chart.gender}</CardDescription>
                      )}
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(chart.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>
                      <strong className="text-foreground">Nascimento:</strong>{' '}
                      {formatDate(chart.birth_datetime)}
                    </p>
                    <p>
                      <strong className="text-foreground">Local:</strong> {chart.city}
                      {chart.country && `, ${chart.country}`}
                    </p>
                    <p>
                      <strong className="text-foreground">Sistema:</strong> {chart.house_system}
                    </p>
                  </div>

                  {chart.chart_data && (
                    <div className="pt-4 border-t border-border">
                      <p className="text-xs text-muted-foreground mb-2">Big Three</p>
                      <div className="grid grid-cols-3 gap-2 text-xs">
                        <div className="text-center">
                          <p className="text-muted-foreground mb-1">☉ Sol</p>
                          <p className="font-medium text-foreground flex items-center justify-center gap-1">
                            <span className="text-base">
                              {getSignSymbol(chart.chart_data.planets.find(p => p.name === 'Sun')?.sign || '')}
                            </span>
                            {chart.chart_data.planets.find(p => p.name === 'Sun')?.sign || 'N/A'}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-muted-foreground mb-1">☽ Lua</p>
                          <p className="font-medium text-foreground flex items-center justify-center gap-1">
                            <span className="text-base">
                              {getSignSymbol(chart.chart_data.planets.find(p => p.name === 'Moon')?.sign || '')}
                            </span>
                            {chart.chart_data.planets.find(p => p.name === 'Moon')?.sign || 'N/A'}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-muted-foreground mb-1">ASC</p>
                          <p className="font-medium text-foreground flex items-center justify-center gap-1">
                            <span className="text-base">
                              {getSignSymbol(getSignFromLongitude(chart.chart_data.ascendant))}
                            </span>
                            {getSignFromLongitude(chart.chart_data.ascendant)}
                          </p>
                        </div>
                      </div>
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
                  <Button asChild variant="secondary" className="w-full">
                    <Link to={`/charts/${chart.id}`}>
                      Ver Detalhes
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
