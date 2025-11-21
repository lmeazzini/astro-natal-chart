/**
 * Chart Detail Page - complete birth chart visualization
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { chartsService, BirthChart } from '../services/charts';
import { interpretationsService, ChartInterpretations } from '../services/interpretations';
import { generateChartPDF, getPDFStatus, downloadChartPDF } from '../services/pdf';
import type { PDFStatus } from '../types/pdf';
import { ChartWheelAstro } from '../components/ChartWheelAstro';
import { PlanetList } from '../components/PlanetList';
import { HouseTable } from '../components/HouseTable';
import { AspectGrid } from '../components/AspectGrid';
import { LunarPhase } from '../components/LunarPhase';
import { SolarPhase } from '../components/SolarPhase';
import { LordOfNativity } from '../components/LordOfNativity';
import { TemperamentDisplay } from '../components/TemperamentDisplay';
import { ArabicPartsTable } from '../components/ArabicPartsTable';
import { InfoTooltip } from '../components/InfoTooltip';
import { getSignSymbol } from '../utils/astro';
import { formatBirthDateTime } from '@/utils/datetime';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BigThreeBadge } from '@/components/ui/big-three-badge';
import { Trash2, ArrowLeft, Sparkles, FileDown, Loader2 } from 'lucide-react';

const TOKEN_KEY = 'astro_access_token';

export function ChartDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [chart, setChart] = useState<BirthChart | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [interpretations, setInterpretations] = useState<ChartInterpretations | null>(null);

  // PDF export state
  const [pdfStatus, setPdfStatus] = useState<PDFStatus>('idle');
  // @ts-expect-error - TODO: Display error message in UI
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [pdfError, setPdfError] = useState<string | null>(null);

  useEffect(() => {
    loadChart();
    loadInterpretations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Polling effect for processing charts
  useEffect(() => {
    if (!chart || chart.status !== 'processing') {
      return; // Only poll if chart is processing
    }

    const pollInterval = setInterval(async () => {
      try {
        const token = localStorage.getItem(TOKEN_KEY);
        if (!token || !id) return;

        const status = await chartsService.getStatus(id, token);

        if (status.status === 'completed' || status.status === 'failed') {
          // Reload full chart data when done
          const chartData = await chartsService.getById(id, token);
          setChart(chartData);
          clearInterval(pollInterval);
        } else {
          // Update progress
          setChart((prev) => prev ? { ...prev, progress: status.progress } : null);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [chart, id]);

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

  async function loadInterpretations() {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token || !id) return;

      const data = await interpretationsService.getByChartId(id, token);
      setInterpretations(data);
    } catch (err) {
      // Silently fail - interpretations are optional
      console.error('Failed to load interpretations:', err);
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

  async function handleExportPDF() {
    if (!id || !chart) return;

    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      navigate('/login');
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
            setPdfError(status.message || 'Erro ao gerar PDF');
          }
          // If status is 'generating', continue polling
        } catch (err) {
          clearInterval(pollInterval);
          setPdfStatus('failed');
          setPdfError(err instanceof Error ? err.message : 'Erro ao verificar status do PDF');
        }
      }, 2000); // Poll every 2 seconds

      // Timeout after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (pdfStatus === 'generating') {
          setPdfStatus('failed');
          setPdfError('Tempo limite excedido ao gerar PDF');
        }
      }, 300000); // 5 minutes

    } catch (err) {
      setPdfStatus('failed');
      setPdfError(err instanceof Error ? err.message : 'Erro ao iniciar geração de PDF');
    }
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
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-shimmer mb-astro-md">
            <Sparkles className="h-12 w-12 text-primary" />
          </div>
          <p className="text-body text-muted-foreground">Carregando mapa natal...</p>
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
          <h2 className="text-headline-3 font-display mb-astro-sm">Gerando seu Mapa Natal...</h2>
          <p className="text-body text-muted-foreground mb-astro-md">
            Estamos calculando as posições planetárias e gerando interpretações astrológicas.
          </p>
          <div className="w-full bg-muted rounded-full h-2 mb-astro-sm">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${chart.progress}%` }}
            />
          </div>
          <p className="text-caption text-muted-foreground">
            {chart.progress}% completo
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
            Erro ao Gerar Mapa
          </h2>
          <p className="text-body text-muted-foreground mb-astro-md">
            {chart.error_message || 'Ocorreu um erro ao processar seu mapa natal.'}
          </p>
          <Button onClick={() => navigate('/charts')}>Voltar aos Mapas</Button>
        </div>
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5 flex items-center justify-center px-4">
        <div className="max-w-md w-full animate-fade-in">
          <div className="bg-destructive/10 border border-destructive/20 rounded-astro-lg p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              Erro
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              {error || 'Mapa natal não encontrado'}
            </p>
            <Button asChild className="w-full">
              <Link to="/charts">
                Voltar para Meus Mapas
              </Link>
            </Button>
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
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link
                to="/dashboard"
                className="hover:opacity-80 transition-all duration-200 flex-shrink-0"
                aria-label="Voltar ao Dashboard"
              >
                <img
                  src="/logo.png"
                  alt="Real Astrology"
                  className="h-8 w-8"
                />
              </Link>
              <div>
                <h1 className="text-h3 font-display text-foreground">
                  {chart.person_name}
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  {formatBirthDateTime(chart.birth_datetime, chart.birth_timezone || 'UTC', true)} • {chart.city}
                  {chart.country && `, ${chart.country}`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
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
                    Gerando PDF...
                  </>
                ) : pdfStatus === 'ready' ? (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    PDF Baixado!
                  </>
                ) : pdfStatus === 'failed' ? (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    Tentar Novamente
                  </>
                ) : (
                  <>
                    <FileDown className="mr-2 h-4 w-4" />
                    Exportar PDF
                  </>
                )}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleDelete}
                className="text-destructive hover:text-destructive hover:bg-destructive/10"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Excluir
              </Button>
              <Button asChild variant="secondary" size="sm">
                <Link to="/charts">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Voltar
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
              <p className="text-sm text-muted-foreground mb-2 font-medium">Ascendente</p>
              <p className="text-h3 font-display text-foreground flex items-center gap-2">
                {getSignSymbol(ascSign)} {ascSign} {ascDegree}°
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">Sistema de Casas</p>
              <p className="text-h3 font-display text-foreground capitalize">
                {chart.house_system}
              </p>
            </CardContent>
          </Card>
          <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardContent className="pt-6">
              <p className="text-sm text-muted-foreground mb-2 font-medium">Tipo de Zodíaco</p>
              <p className="text-h3 font-display text-foreground capitalize">
                {chart.zodiac_type}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="visual" className="w-full">
          <TabsList className="w-full justify-start mb-6">
            <TabsTrigger value="visual">Visualização</TabsTrigger>
            <TabsTrigger value="planets">
              Planetas ({chart.chart_data?.planets.length || 0})
            </TabsTrigger>
            <TabsTrigger value="houses">Casas (12)</TabsTrigger>
            <TabsTrigger value="aspects">
              Aspectos ({chart.chart_data?.aspects.length || 0})
            </TabsTrigger>
            <TabsTrigger value="arabic-parts">
              Partes Árabes (4)
            </TabsTrigger>
          </TabsList>

          {/* Tab Content: Visual */}
          <TabsContent value="visual" className="mt-0">
            {chart.chart_data && (
            <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="text-h3 font-display">Mapa Natal</CardTitle>
                <CardDescription>Visualização completa do seu céu de nascimento</CardDescription>
              </CardHeader>
              <CardContent className="space-y-8">
                {/* Big Three Summary */}
                <div>
                  <h3 className="text-h4 font-display mb-4">Essência Astrológica</h3>
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
                    <span className="text-3xl" title="Sol">
                      ☉
                    </span>
                    <div>
                      <div className="flex items-center gap-1">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide">
                          Sua essência
                        </p>
                        <InfoTooltip
                          content="O Sol representa sua identidade central, propósito de vida e vitalidade. É o núcleo da sua personalidade consciente."
                          side="top"
                        />
                      </div>
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
                      <div className="flex items-center gap-1">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide">
                          Suas emoções
                        </p>
                        <InfoTooltip
                          content="A Lua representa suas emoções, necessidades instintivas e reações inconscientes. Revela como você se sente seguro e confortável."
                          side="top"
                        />
                      </div>
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
                      <div className="flex items-center gap-1">
                        <p className="text-xs text-muted-foreground uppercase tracking-wide">
                          Sua aparência
                        </p>
                        <InfoTooltip
                          content="O Ascendente é o signo que estava nascendo no horizonte leste no momento do seu nascimento. Representa sua máscara social e primeira impressão."
                          side="top"
                        />
                      </div>
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

              {/* Lunar and Solar Phases */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {chart.chart_data.lunar_phase && (
                  <LunarPhase lunarPhase={chart.chart_data.lunar_phase} />
                )}
                {chart.chart_data.solar_phase && (
                  <SolarPhase solarPhase={chart.chart_data.solar_phase} />
                )}
              </div>

              {/* Lord of Nativity */}
              {chart.chart_data.lord_of_nativity && (
                <div>
                  <LordOfNativity lordOfNativity={chart.chart_data.lord_of_nativity} />
                </div>
              )}

              {/* Temperament */}
              {chart.chart_data.temperament && (
                <div>
                  <TemperamentDisplay temperament={chart.chart_data.temperament} />
                </div>
              )}

              {/* Chart Wheel - Professional visualization with AstroChart */}
              <div>
                <h3 className="text-h4 font-display mb-4">Roda do Mapa Natal</h3>
                <ChartWheelAstro chartData={chart.chart_data} />
              </div>
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
                    Posições Planetárias
                    <InfoTooltip
                      content="Posições exatas dos planetas calculadas com Swiss Ephemeris (precisão < 1 arcsecond). Inclui longitude, latitude, velocidade e estado retrógrado."
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <PlanetList
                    planets={chart.chart_data.planets}
                    showOnlyClassical={true}
                    interpretations={interpretations?.planets}
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
                    Casas Astrológicas
                    <InfoTooltip
                      content={`As 12 casas dividem o céu em setores que representam áreas da vida. Sistema utilizado: ${chart.house_system}. Cada casa tem uma cúspide (início) e um regente planetário.`}
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <HouseTable
                    houses={chart.chart_data.houses}
                    interpretations={interpretations?.houses}
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
                    Aspectos Planetários
                    <InfoTooltip
                      content="Aspectos são ângulos geométricos entre planetas que revelam como eles interagem. Detectamos aspectos maiores (conjunção, oposição, trígono, quadratura, sextil) e menores (quincunx, semisextil, etc.) com orbes configuráveis."
                      side="right"
                    />
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AspectGrid
                    aspects={chart.chart_data.aspects}
                    interpretations={interpretations?.aspects}
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
                    Partes Árabes (Lotes)
                    <InfoTooltip
                      content="Partes Árabes (ou Lotes) são pontos calculados matematicamente a partir de posições planetárias. Revelam temas específicos da vida segundo a tradição helenística."
                      side="right"
                    />
                  </CardTitle>
                  <CardDescription>
                    Pontos sensitivos da tradição astrológica helenística
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ArabicPartsTable parts={chart.chart_data.arabic_parts} />

                  {/* Seção Educacional */}
                  <div className="mt-8 p-6 bg-muted/50 rounded-lg space-y-4">
                    <h4 className="text-lg font-semibold text-foreground flex items-center gap-2">
                      📚 Sobre as Partes Árabes
                    </h4>

                    <div className="space-y-3 text-sm text-muted-foreground">
                      <p>
                        <strong className="text-foreground">O que são:</strong> As Partes Árabes (também chamadas de "Lotes"
                        na tradição helenística) são pontos calculados matematicamente a partir da posição de planetas e ângulos.
                        Funcionam como "planetas virtuais", revelando temas específicos da vida.
                      </p>

                      <p>
                        <strong className="text-foreground">Fórmula geral:</strong> Parte = Ascendente + Planeta1 - Planeta2 (todos em graus de 0-360).
                        As fórmulas diferem entre mapas diurnos (☀️ Sol acima do horizonte) e noturnos (🌙 Sol abaixo do horizonte).
                      </p>

                      <p>
                        <strong className="text-foreground">Importância:</strong> A casa onde cai uma Parte e os aspectos que ela recebe
                        de planetas natais são significativos. O Lote da Fortuna é especialmente importante - astrólogos medievais
                        o tratavam com a mesma importância que o Ascendente.
                      </p>

                      <p>
                        <strong className="text-foreground">Origem:</strong> Desenvolvidas na astrologia helenística (Grécia/Roma, 100 a.C. - 600 d.C.)
                        e expandidas por astrólogos árabes medievais (700-1400 d.C.). Existem centenas de Partes catalogadas,
                        mas as 4 apresentadas aqui são as mais fundamentais.
                      </p>

                      <div className="pt-4 border-t border-border">
                        <p className="text-xs italic">
                          <strong>Nota técnica:</strong> O seu mapa é {chart.chart_data.sect === 'diurnal' ? 'diurno' : 'noturno'}
                          ({chart.chart_data.sect === 'diurnal' ? 'Sol acima do horizonte' : 'Sol abaixo do horizonte'}),
                          portanto as fórmulas utilizadas seguem as regras de seita da tradição helenística.
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-0 shadow-lg bg-card/90 backdrop-blur-sm">
                <CardContent className="pt-6 text-center text-muted-foreground">
                  <p>Partes Árabes não disponíveis para este mapa.</p>
                  <p className="text-sm mt-2">
                    As Partes serão calculadas automaticamente em mapas criados ou atualizados após esta funcionalidade.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Notes */}
        {chart.notes && (
          <Card className="mt-6 border-0 shadow-lg bg-card/90 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="text-h4 font-display">Anotações</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-body text-muted-foreground whitespace-pre-wrap">
                {chart.notes}
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
