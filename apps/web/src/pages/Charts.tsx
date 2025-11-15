/**
 * Birth Charts list page
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { chartsService, BirthChart } from '../services/charts';

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
          <h1 className="text-2xl font-bold text-foreground">Meus Mapas Natais</h1>
          <div className="flex items-center gap-4">
            <Link
              to="/charts/new"
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition"
            >
              + Novo Mapa
            </Link>
            <button
              onClick={() => navigate('/dashboard')}
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              ← Dashboard
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <div className="max-w-7xl mx-auto py-8 px-4">
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
            <p className="text-sm text-destructive">{error}</p>
          </div>
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
            <Link
              to="/charts/new"
              className="inline-block px-6 py-3 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition font-medium"
            >
              Criar Meu Primeiro Mapa
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {charts.map((chart) => (
              <div
                key={chart.id}
                className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-foreground">
                      {chart.person_name}
                    </h3>
                    {chart.gender && (
                      <p className="text-sm text-muted-foreground">{chart.gender}</p>
                    )}
                  </div>
                  <button
                    onClick={() => handleDelete(chart.id)}
                    className="text-destructive hover:text-destructive/80 text-sm"
                  >
                    Excluir
                  </button>
                </div>

                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>
                    <strong>Nascimento:</strong>{' '}
                    {formatDate(chart.birth_datetime)}
                  </p>
                  <p>
                    <strong>Local:</strong> {chart.city}
                    {chart.country && `, ${chart.country}`}
                  </p>
                  <p>
                    <strong>Sistema:</strong> {chart.house_system}
                  </p>
                </div>

                {chart.chart_data && (
                  <div className="mt-4 pt-4 border-t border-border">
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-muted-foreground">Ascendente</p>
                        <p className="font-medium text-foreground">
                          {chart.chart_data.planets.find(p => p.name === 'Sun')?.sign || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Planetas</p>
                        <p className="font-medium text-foreground">
                          {chart.chart_data.planets.length}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {chart.notes && (
                  <div className="mt-4 pt-4 border-t border-border">
                    <p className="text-xs text-muted-foreground line-clamp-2">
                      {chart.notes}
                    </p>
                  </div>
                )}

                <div className="mt-4">
                  <Link
                    to={`/charts/${chart.id}`}
                    className="block w-full text-center py-2 px-4 bg-secondary text-secondary-foreground rounded-md hover:opacity-90 transition text-sm font-medium"
                  >
                    Ver Detalhes
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
