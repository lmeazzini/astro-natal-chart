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
import { EmptyState } from '@/components/ui/empty-state';
import { BigThreeBadge } from '@/components/ui/big-three-badge';
import { AlertCircle, Trash2, Plus, ArrowLeft, Sparkles } from 'lucide-react';

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
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <p className="text-body text-muted-foreground">Carregando mapas...</p>
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
            aria-label="Voltar ao Dashboard"
          >
            <img
              src="/logo.png"
              alt="Astro"
              className="h-8 w-8"
            />
            <h1 className="text-h3 font-display text-foreground">Meus Mapas Natais</h1>
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
          <div className="animate-fade-in">
            <EmptyState
              icon={Sparkles}
              title="Nenhum mapa natal ainda"
              description="Crie seu primeiro mapa natal para começar sua jornada astrológica e descobrir os segredos do seu céu de nascimento"
              action={{
                label: 'Criar Meu Primeiro Mapa',
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
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(chart.id)}
                      className="text-destructive hover:text-destructive hover:bg-destructive/10 -mr-2 -mt-1"
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
                    <div className="pt-4 border-t border-border/50">
                      <p className="text-xs text-muted-foreground mb-3 font-medium">Big Three</p>
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
                      Ver Detalhes Completos
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
