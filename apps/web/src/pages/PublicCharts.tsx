import * as React from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  listPublicCharts,
  getCategories,
  getCategoryLabel,
  type PublicChartPreview,
  type CategoryCount,
} from '../services/publicCharts';
import { formatBirthDateTime } from '../utils/datetime';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { useAuth } from '../contexts/AuthContext';

export function PublicChartsPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [charts, setCharts] = React.useState<PublicChartPreview[]>([]);
  const [categories, setCategories] = React.useState<CategoryCount[]>([]);
  const [total, setTotal] = React.useState(0);
  const [loading, setLoading] = React.useState(true);
  const [searchInput, setSearchInput] = React.useState(searchParams.get('search') || '');

  const category = searchParams.get('category') || undefined;
  const search = searchParams.get('search') || undefined;
  const sort = (searchParams.get('sort') as 'name' | 'date' | 'views') || 'name';
  const page = parseInt(searchParams.get('page') || '1', 10);
  const pageSize = 12;

  const loadData = React.useCallback(async () => {
    setLoading(true);
    try {
      const data = await listPublicCharts({
        category,
        search,
        sort,
        page,
        page_size: pageSize,
      });
      setCharts(data.charts);
      setTotal(data.total);
    } catch (error) {
      console.error('Error loading public charts:', error);
    } finally {
      setLoading(false);
    }
  }, [category, search, sort, page, pageSize]);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  React.useEffect(() => {
    loadCategories();
  }, []);

  async function loadCategories() {
    try {
      const data = await getCategories();
      setCategories(data.filter((c) => c.count > 0));
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const newParams = new URLSearchParams(searchParams);
    if (searchInput) {
      newParams.set('search', searchInput);
    } else {
      newParams.delete('search');
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  }

  function handleCategoryClick(cat: string | null) {
    const newParams = new URLSearchParams(searchParams);
    if (cat) {
      newParams.set('category', cat);
    } else {
      newParams.delete('category');
    }
    newParams.set('page', '1');
    setSearchParams(newParams);
  }

  function handleSortChange(newSort: 'name' | 'date' | 'views') {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('sort', newSort);
    newParams.set('page', '1');
    setSearchParams(newParams);
  }

  function handlePageChange(newPage: number) {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-4">
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
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-primary/10 to-background py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            {t('publicCharts.title', 'Mapas de Pessoas Famosas')}
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {t(
              'publicCharts.subtitle',
              'Explore mapas natais de personalidades históricas e avalie nossas interpretações com IA.'
            )}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex gap-2 flex-1">
            <Input
              type="text"
              placeholder={t('publicCharts.searchPlaceholder', 'Buscar por nome...')}
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="flex-1"
            />
            <Button type="submit">{t('common.search', 'Buscar')}</Button>
          </form>

          {/* Sort */}
          <div className="flex gap-2">
            <Button
              variant={sort === 'name' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleSortChange('name')}
            >
              {t('publicCharts.sortName', 'A-Z')}
            </Button>
            <Button
              variant={sort === 'date' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleSortChange('date')}
            >
              {t('publicCharts.sortDate', 'Data')}
            </Button>
            <Button
              variant={sort === 'views' ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleSortChange('views')}
            >
              {t('publicCharts.sortViews', 'Populares')}
            </Button>
          </div>
        </div>

        {/* Categories */}
        {categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-8">
            <Button
              variant={!category ? 'default' : 'outline'}
              size="sm"
              onClick={() => handleCategoryClick(null)}
            >
              {t('publicCharts.allCategories', 'Todos')}
            </Button>
            {categories.map((cat) => (
              <Button
                key={cat.category}
                variant={category === cat.category ? 'default' : 'outline'}
                size="sm"
                onClick={() => handleCategoryClick(cat.category)}
              >
                {getCategoryLabel(cat.category)} ({cat.count})
              </Button>
            ))}
          </div>
        )}

        {/* Results count */}
        <p className="text-sm text-muted-foreground mb-4">
          {t('publicCharts.resultsCount', '{{count}} mapas encontrados', { count: total })}
        </p>

        {/* Chart Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <Skeleton className="h-24 w-24 rounded-full mx-auto mb-4" />
                  <Skeleton className="h-6 w-3/4 mx-auto mb-2" />
                  <Skeleton className="h-4 w-1/2 mx-auto" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : charts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">
              {t('publicCharts.noResults', 'Nenhum mapa encontrado.')}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {charts.map((chart) => (
              <PublicChartCard key={chart.id} chart={chart} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => handlePageChange(page - 1)}
            >
              {t('common.previous', 'Anterior')}
            </Button>
            <span className="flex items-center px-4 text-sm text-muted-foreground">
              {t('common.pageOf', 'Página {{page}} de {{total}}', {
                page,
                total: totalPages,
              })}
            </span>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => handlePageChange(page + 1)}
            >
              {t('common.next', 'Próximo')}
            </Button>
          </div>
        )}

        {/* CTA */}
        <div className="mt-12 bg-primary/10 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            {user
              ? t('publicCharts.ctaTitleLoggedIn', 'Crie Mais Mapas Natais')
              : t('publicCharts.ctaTitle', 'Crie Seu Próprio Mapa Natal')}
          </h2>
          <p className="text-muted-foreground mb-6">
            {t(
              'publicCharts.ctaDescription',
              'Descubra os segredos do seu mapa astrológico com análise profissional e interpretações IA.'
            )}
          </p>
          <Button size="lg" asChild>
            <Link to={user ? '/charts/new' : '/register'}>
              {user
                ? t('publicCharts.ctaButtonLoggedIn', 'Criar Novo Mapa')
                : t('publicCharts.ctaButton', 'Começar Grátis')}
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}

function PublicChartCard({ chart }: { chart: PublicChartPreview }) {
  const { t } = useTranslation();
  return (
    <Link to={`/public-charts/${chart.slug}`}>
      <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
        <CardContent className="p-6 flex flex-col items-center text-center">
          {chart.photo_url ? (
            <img
              src={chart.photo_url}
              alt={chart.full_name}
              className="h-24 w-24 rounded-full object-cover mb-4"
            />
          ) : (
            <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-4">
              <span className="text-3xl font-bold text-muted-foreground">
                {chart.full_name.charAt(0)}
              </span>
            </div>
          )}
          <h3 className="text-lg font-semibold text-foreground mb-1">{chart.full_name}</h3>
          {chart.category && (
            <Badge variant="secondary" className="mb-2">
              {getCategoryLabel(chart.category)}
            </Badge>
          )}
          <p className="text-sm text-muted-foreground">
            {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone)}
          </p>
          {chart.city && chart.country && (
            <p className="text-xs text-muted-foreground mt-1">
              {chart.city}, {chart.country}
            </p>
          )}
          {chart.view_count > 0 && (
            <p className="text-xs text-muted-foreground mt-2">
              {chart.view_count} {t('publicCharts.views', 'visualizações')}
            </p>
          )}
        </CardContent>
      </Card>
    </Link>
  );
}
