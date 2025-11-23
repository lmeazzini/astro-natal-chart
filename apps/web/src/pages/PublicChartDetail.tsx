/**
 * Public Chart Detail Page - view famous person's natal chart
 *
 * This page displays public charts with simplified components
 * since the public chart data structure differs from user charts.
 */

import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { getPublicChart, getCategoryLabel, type PublicChartDetail } from '../services/publicCharts';
import { formatBirthDateTime } from '@/utils/datetime';
import { getSignSymbol, getPlanetSymbol } from '../utils/astro';
import { ThemeToggle } from '../components/ThemeToggle';
import { LanguageSelector } from '../components/LanguageSelector';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { ArrowLeft, Sparkles, Eye, Sun, Moon, Compass } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

// Type definitions for chart data
interface ChartPlanet {
  name: string;
  sign: string;
  degree: number;
  minute: number;
  house: number;
  retrograde: boolean;
  longitude: number;
  latitude: number;
  speed: number;
}

interface ChartHouse {
  house: number;
  sign: string;
  degree: number;
  minute: number;
  longitude: number;
}

interface ChartAspect {
  planet1: string;
  planet2: string;
  aspect: string;
  orb: number;
  applying: boolean;
}

interface ChartData {
  planets?: ChartPlanet[];
  houses?: ChartHouse[];
  aspects?: ChartAspect[];
}

export function PublicChartDetailPage() {
  const { t } = useTranslation();
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();

  const [chart, setChart] = useState<PublicChartDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

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

  useEffect(() => {
    loadChart();
  }, [loadChart]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <nav className="bg-card border-b border-border">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <Skeleton className="h-8 w-48" />
          </div>
        </nav>
        <div className="max-w-7xl mx-auto py-8 px-4">
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">
            {t('publicCharts.notFound', 'Mapa não encontrado')}
          </h1>
          <p className="text-muted-foreground mb-6">{error}</p>
          <Button asChild>
            <Link to="/public-charts">{t('common.back', 'Voltar')}</Link>
          </Button>
        </div>
      </div>
    );
  }

  const chartData = chart.chart_data as ChartData | null;

  // Extract Big Three
  const sunData = chartData?.planets?.find((p) => p.name === 'Sun');
  const moonData = chartData?.planets?.find((p) => p.name === 'Moon');
  const ascendantSign = chartData?.houses?.[0]?.sign;

  // Format degree display
  const formatDegree = (degree: number, minute: number) => {
    return `${degree}°${minute.toString().padStart(2, '0')}'`;
  };

  // Get aspect symbol
  const getAspectSymbol = (aspect: string): string => {
    const symbols: Record<string, string> = {
      conjunction: '☌',
      opposition: '☍',
      trine: '△',
      square: '□',
      sextile: '⚹',
      quincunx: '⚻',
    };
    return symbols[aspect.toLowerCase()] || aspect;
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link to="/public-charts">
                <ArrowLeft className="h-4 w-4 mr-2" />
                {t('common.back', 'Voltar')}
              </Link>
            </Button>
            <Link
              to="/"
              className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            >
              <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
              <span className="text-xl font-bold text-foreground">Real Astrology</span>
            </Link>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSelector />
            <ThemeToggle />
            {!user && (
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

      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* Header */}
        <div className="flex flex-col md:flex-row gap-6 mb-8">
          {chart.photo_url ? (
            <img
              src={chart.photo_url}
              alt={chart.full_name}
              className="h-32 w-32 rounded-full object-cover"
            />
          ) : (
            <div className="h-32 w-32 rounded-full bg-muted flex items-center justify-center">
              <span className="text-4xl font-bold text-muted-foreground">
                {chart.full_name.charAt(0)}
              </span>
            </div>
          )}

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-foreground">{chart.full_name}</h1>
              {chart.category && (
                <Badge variant="secondary">{getCategoryLabel(chart.category)}</Badge>
              )}
            </div>

            {chart.short_bio && (
              <p className="text-muted-foreground mb-4">{chart.short_bio}</p>
            )}

            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <span>
                {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone)}
              </span>
              {chart.city && chart.country && (
                <span>
                  {chart.city}, {chart.country}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Eye className="h-4 w-4" />
                {chart.view_count} visualizações
              </span>
            </div>

            {/* Big Three */}
            {sunData && moonData && ascendantSign && (
              <div className="flex flex-wrap gap-3 mt-4">
                <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
                  <Sun className="h-4 w-4 text-yellow-500" />
                  <span className="font-medium">Sol:</span>
                  <span>{getSignSymbol(sunData.sign)} {sunData.sign}</span>
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
                  <Moon className="h-4 w-4 text-slate-400" />
                  <span className="font-medium">Lua:</span>
                  <span>{getSignSymbol(moonData.sign)} {moonData.sign}</span>
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
                  <Compass className="h-4 w-4 text-purple-500" />
                  <span className="font-medium">Asc:</span>
                  <span>{getSignSymbol(ascendantSign)} {ascendantSign}</span>
                </Badge>
              </div>
            )}
          </div>
        </div>

        {/* Highlights */}
        {chart.highlights && chart.highlights.length > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                {t('publicCharts.highlights', 'Destaques Astrológicos')}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-2">
                {chart.highlights.map((highlight, index) => (
                  <li key={index} className="text-muted-foreground">
                    {highlight}
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        {/* Detailed Tabs */}
        <Tabs defaultValue="planets" className="mt-8">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="planets">
              {t('chartDetail.planets', 'Planetas')}
            </TabsTrigger>
            <TabsTrigger value="houses">
              {t('chartDetail.houses', 'Casas')}
            </TabsTrigger>
            <TabsTrigger value="aspects">
              {t('chartDetail.aspects', 'Aspectos')}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="planets">
            <Card>
              <CardHeader>
                <CardTitle>{t('chartDetail.planets', 'Planetas')}</CardTitle>
              </CardHeader>
              <CardContent>
                {chartData?.planets ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('chartDetail.planet', 'Planeta')}</TableHead>
                        <TableHead>{t('chartDetail.sign', 'Signo')}</TableHead>
                        <TableHead>{t('chartDetail.degree', 'Grau')}</TableHead>
                        <TableHead>{t('chartDetail.house', 'Casa')}</TableHead>
                        <TableHead>{t('chartDetail.retrograde', 'R')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {chartData.planets.map((planet) => (
                        <TableRow key={planet.name}>
                          <TableCell className="font-medium">
                            {getPlanetSymbol(planet.name)} {planet.name}
                          </TableCell>
                          <TableCell>
                            {getSignSymbol(planet.sign)} {planet.sign}
                          </TableCell>
                          <TableCell>{formatDegree(planet.degree, planet.minute)}</TableCell>
                          <TableCell>{planet.house}</TableCell>
                          <TableCell>{planet.retrograde ? '℞' : ''}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    {t('chartDetail.noData', 'Dados não disponíveis')}
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="houses">
            <Card>
              <CardHeader>
                <CardTitle>{t('chartDetail.houses', 'Casas')}</CardTitle>
              </CardHeader>
              <CardContent>
                {chartData?.houses ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('chartDetail.house', 'Casa')}</TableHead>
                        <TableHead>{t('chartDetail.sign', 'Signo')}</TableHead>
                        <TableHead>{t('chartDetail.degree', 'Grau')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {chartData.houses.map((house) => (
                        <TableRow key={house.house}>
                          <TableCell className="font-medium">{house.house}</TableCell>
                          <TableCell>
                            {getSignSymbol(house.sign)} {house.sign}
                          </TableCell>
                          <TableCell>{formatDegree(house.degree, house.minute)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    {t('chartDetail.noData', 'Dados não disponíveis')}
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="aspects">
            <Card>
              <CardHeader>
                <CardTitle>{t('chartDetail.aspects', 'Aspectos')}</CardTitle>
              </CardHeader>
              <CardContent>
                {chartData?.aspects && chartData.aspects.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>{t('chartDetail.planet', 'Planeta')} 1</TableHead>
                        <TableHead>{t('chartDetail.aspect', 'Aspecto')}</TableHead>
                        <TableHead>{t('chartDetail.planet', 'Planeta')} 2</TableHead>
                        <TableHead>{t('chartDetail.orb', 'Orbe')}</TableHead>
                        <TableHead>{t('chartDetail.applying', 'Aplicando')}</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {chartData.aspects.map((aspect, idx) => (
                        <TableRow key={idx}>
                          <TableCell>{getPlanetSymbol(aspect.planet1)} {aspect.planet1}</TableCell>
                          <TableCell className="text-xl">{getAspectSymbol(aspect.aspect)}</TableCell>
                          <TableCell>{getPlanetSymbol(aspect.planet2)} {aspect.planet2}</TableCell>
                          <TableCell>{aspect.orb.toFixed(1)}°</TableCell>
                          <TableCell>{aspect.applying ? '→' : '←'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-muted-foreground text-center py-8">
                    {t('chartDetail.noData', 'Dados não disponíveis')}
                  </p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* CTA */}
        <div className="mt-12 bg-primary/10 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-foreground mb-4">
            {t('publicCharts.ctaTitle', 'Crie Seu Próprio Mapa Natal')}
          </h2>
          <p className="text-muted-foreground mb-6">
            {t(
              'publicCharts.ctaDescription',
              'Descubra os segredos do seu mapa astrológico com análise profissional e interpretações IA.'
            )}
          </p>
          <Button size="lg" asChild>
            <Link to="/register">{t('publicCharts.ctaButton', 'Começar Grátis')}</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
