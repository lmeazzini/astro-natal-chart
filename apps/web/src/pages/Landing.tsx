/**
 * Landing Page - Premium conversion-focused homepage
 * Issue #56 - Transform HomePage into Premium Landing Page with Astro Essence
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from '@/components/ui/accordion';
import {
  UserPlus,
  Calendar,
  Calculator,
  Eye,
  Star,
  Palette,
  Brain,
  Smartphone,
  Shield,
  Infinity,
  FileText,
  Moon,
  Book,
  Satellite,
  Sparkles,
  Lock,
  FileCheck,
  Database,
  ClipboardCheck,
  ArrowRight,
  Check,
} from 'lucide-react';

export function LandingPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label={t('pages.landing.homeLabel', { defaultValue: 'Página Inicial' })}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="sm">
              <Link to="/login">{t('pages.landing.login', { defaultValue: 'Entrar' })}</Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/register">{t('pages.landing.createAccount', { defaultValue: 'Criar Conta' })}</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 relative">
          <div className="text-center max-w-4xl mx-auto animate-fade-in">
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 font-display leading-tight">
              {t('pages.landing.heroTitle', { defaultValue: 'Desvende os Mistérios do Seu Mapa Natal com Precisão Astronômica' })}
            </h2>
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-3xl mx-auto">
              {t('pages.landing.heroSubtitle1', { defaultValue: 'Cálculos precisos com' })}{' '}
              <span className="text-primary font-semibold">Swiss Ephemeris</span>,{' '}
              {t('pages.landing.heroSubtitle2', { defaultValue: 'visualizações profissionais em HD e interpretações personalizadas com' })}{' '}
              <span className="text-primary font-semibold">{t('pages.landing.ai', { defaultValue: 'Inteligência Artificial' })}</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button asChild size="lg" className="group">
                <Link to="/register">
                  {t('pages.landing.createFreeAccount', { defaultValue: 'Criar Minha Conta Grátis' })}
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button asChild variant="secondary" size="lg">
                <Link to="/charts/new">
                  {t('pages.landing.viewExampleChart', { defaultValue: 'Ver Exemplo de Mapa' })}
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Why Astro Section - Educational Content */}
      <section className="py-16 lg:py-24 bg-card/30">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.whyAstro.title', { defaultValue: 'Por que Astro?' })}
            </h3>
            <p className="text-muted-foreground text-lg max-w-3xl mx-auto">
              {t('pages.landing.whyAstro.subtitle', { defaultValue: 'Nossa plataforma combina o melhor da Astrologia Tradicional com precisão astronômica de ponta, oferecendo cálculos confiáveis e interpretações autênticas.' })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
            {/* Feature 1: Traditional Astrology */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Book className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl mb-3">{t('pages.landing.whyAstro.traditional.title', { defaultValue: 'Astrologia Tradicional' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  {t('pages.landing.whyAstro.traditional.description', { defaultValue: 'Utilizamos técnicas clássicas da Astrologia Helenística e Medieval:' })}
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.traditional.dignities', { defaultValue: 'Dignidades Essenciais' })}</strong>: {t('pages.landing.whyAstro.traditional.dignitiesDesc', { defaultValue: 'Domicílio, Exaltação, Triplicidade' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.traditional.sect', { defaultValue: 'Análise de Seita' })}</strong>: {t('pages.landing.whyAstro.traditional.sectDesc', { defaultValue: 'Planetas diurnos e noturnos' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.traditional.temperament', { defaultValue: 'Temperamento' })}</strong>: {t('pages.landing.whyAstro.traditional.temperamentDesc', { defaultValue: 'Análise dos 4 elementos e qualidades' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.traditional.lordOfNativity', { defaultValue: 'Senhor da Natividade' })}</strong>: {t('pages.landing.whyAstro.traditional.lordOfNativityDesc', { defaultValue: 'Identificação do planeta regente' })}</span>
                  </li>
                </ul>
                <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                  <p className="text-xs text-muted-foreground italic">
                    <strong>{t('pages.landing.whyAstro.traditional.differentialLabel', { defaultValue: 'Diferencial' })}:</strong> {t('pages.landing.whyAstro.traditional.differential', { defaultValue: 'Ao contrário da astrologia moderna psicológica, focamos em técnicas preditivas e objetivas validadas por séculos de prática.' })}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Feature 2: Swiss Ephemeris Precision */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Satellite className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl mb-3">{t('pages.landing.whyAstro.precision.title', { defaultValue: 'Precisão Swiss Ephemeris' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  {t('pages.landing.whyAstro.precision.description', { defaultValue: 'Utilizamos o Swiss Ephemeris com efemérides JPL DE431 da NASA:' })}
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.precision.arcsecond', { defaultValue: '< 1 arcsecond de erro' })}</strong>: {t('pages.landing.whyAstro.precision.arcsecondDesc', { defaultValue: 'Precisão astronômica profissional' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.precision.nasa', { defaultValue: 'Validação NASA/JPL' })}</strong>: {t('pages.landing.whyAstro.precision.nasaDesc', { defaultValue: 'Mesmas efemérides de missões espaciais' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.precision.coverage', { defaultValue: 'Cobertura de 13.000 anos' })}</strong>: {t('pages.landing.whyAstro.precision.coverageDesc', { defaultValue: 'Cálculos históricos e futuros confiáveis' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.precision.relativistic', { defaultValue: 'Ajustes relativísticos' })}</strong>: {t('pages.landing.whyAstro.precision.relativisticDesc', { defaultValue: 'Inclui correções de Relatividade Geral' })}</span>
                  </li>
                </ul>
                <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                  <p className="text-xs text-muted-foreground italic">
                    <strong>{t('pages.landing.whyAstro.precision.whyMatters', { defaultValue: 'Por que importa?' })}</strong> {t('pages.landing.whyAstro.precision.whyMattersDesc', { defaultValue: 'Diferenças de minutos na hora de nascimento podem alterar casas e aspectos. Nossa precisão garante cálculos confiáveis mesmo para horários aproximados.' })}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Feature 3: Open Source & Transparency */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <FileCheck className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl mb-3">{t('pages.landing.whyAstro.openSource.title', { defaultValue: 'Código Aberto & Transparência' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  {t('pages.landing.whyAstro.openSource.description', { defaultValue: 'Projeto open source com metodologia transparente e verificável:' })}
                </p>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.openSource.auditable', { defaultValue: 'Código auditável' })}</strong>: {t('pages.landing.whyAstro.openSource.auditableDesc', { defaultValue: 'Qualquer um pode verificar nossos cálculos' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.openSource.documented', { defaultValue: 'Metodologia documentada' })}</strong>: {t('pages.landing.whyAstro.openSource.documentedDesc', { defaultValue: 'Explicamos cada técnica utilizada' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.openSource.noBlackbox', { defaultValue: 'Sem "caixas-pretas"' })}</strong>: {t('pages.landing.whyAstro.openSource.noBlackboxDesc', { defaultValue: 'Algoritmos claros e científicos' })}</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Check className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span><strong>{t('pages.landing.whyAstro.openSource.community', { defaultValue: 'Comunidade ativa' })}</strong>: {t('pages.landing.whyAstro.openSource.communityDesc', { defaultValue: 'Contribuições de astrólogos e desenvolvedores' })}</span>
                  </li>
                </ul>
                <div className="mt-4 p-3 bg-muted/50 rounded-lg">
                  <p className="text-xs text-muted-foreground italic">
                    <strong>{t('pages.landing.whyAstro.openSource.commitment', { defaultValue: 'Nosso compromisso' })}:</strong> {t('pages.landing.whyAstro.openSource.commitmentDesc', { defaultValue: 'Nenhum algoritmo secreto ou "fórmula mágica". Tudo é baseado em textos clássicos e cálculos astronômicos verificáveis.' })}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="text-center">
            <Button asChild variant="outline" size="lg">
              <Link to="/about/methodology">
                {t('pages.landing.whyAstro.learnMore', { defaultValue: 'Saiba Mais Sobre Nossa Metodologia' })}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-16 lg:py-24 bg-muted/20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.howItWorks.title', { defaultValue: 'Como Funciona' })}
            </h3>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('pages.landing.howItWorks.subtitle', { defaultValue: 'Em poucos minutos você terá seu mapa natal completo com análise profissional' })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Step 1 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-slide-in-up">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <UserPlus className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('pages.landing.howItWorks.step1.title', { defaultValue: 'Cadastro Rápido' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  {t('pages.landing.howItWorks.step1.description', { defaultValue: 'Crie sua conta gratuitamente em menos de 1 minuto. Apenas email e senha, sem complicações.' })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Step 2 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-slide-in-up" style={{ animationDelay: '100ms' }}>
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Calendar className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('pages.landing.howItWorks.step2.title', { defaultValue: 'Dados de Nascimento' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  {t('pages.landing.howItWorks.step2.description', { defaultValue: 'Informe data, hora e local de nascimento. Nosso sistema encontra as coordenadas automaticamente.' })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Step 3 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-slide-in-up" style={{ animationDelay: '200ms' }}>
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Calculator className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('pages.landing.howItWorks.step3.title', { defaultValue: 'Cálculo Preciso' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  {t('pages.landing.howItWorks.step3.description', { defaultValue: 'Em segundos, calculamos posições planetárias, casas e aspectos com precisão astronômica.' })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Step 4 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 animate-slide-in-up" style={{ animationDelay: '300ms' }}>
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Eye className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('pages.landing.howItWorks.step4.title', { defaultValue: 'Visualize e Interprete' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  {t('pages.landing.howItWorks.step4.description', { defaultValue: 'Acesse seu mapa natal completo com gráficos profissionais e interpretações detalhadas.' })}
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Differentials Section */}
      <section className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.differentials.title', { defaultValue: 'Por Que Escolher o Real Astrology?' })}
            </h3>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('pages.landing.differentials.subtitle', { defaultValue: 'A combinação perfeita entre tradição milenar e tecnologia de ponta' })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Differential 1 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Star className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.precision.title', { defaultValue: 'Precisão Astronômica' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">Swiss Ephemeris</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.precision.description', { defaultValue: 'Utilizamos Swiss Ephemeris JPL DE431 com precisão inferior a 0.001° de erro. A mesma biblioteca usada por astronomos e agências espaciais.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 2 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Palette className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.visualization.title', { defaultValue: 'Visualização Profissional' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">HD Quality</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.visualization.description', { defaultValue: 'Mapas natais em alta definição com todos os elementos: planetas, casas, aspectos, graus e símbolos tradicionais.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 3 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Brain className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.ai.title', { defaultValue: 'Interpretações com IA' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">GPT-4</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.ai.description', { defaultValue: 'Análises personalizadas geradas por Inteligência Artificial treinada em textos clássicos de astrologia tradicional.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 4 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Smartphone className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.multiplatform.title', { defaultValue: 'Multi-Plataforma' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">Responsive</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.multiplatform.description', { defaultValue: 'Acesse de qualquer dispositivo - desktop, tablet ou smartphone. Interface adaptável e otimizada para todas as telas.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 5 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Shield className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.security.title', { defaultValue: '100% Seguro' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">Encrypted</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.security.description', { defaultValue: 'Criptografia de ponta a ponta, conformidade com LGPD/GDPR. Seus dados pessoais protegidos com tecnologia SSL/TLS.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 6 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Infinity className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.unlimited.title', { defaultValue: 'Mapas Ilimitados' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">Free Forever</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.unlimited.description', { defaultValue: 'Crie quantos mapas natais quiser, completamente grátis. Sem limites, sem taxas ocultas, sem pegadinhas.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 7 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <FileText className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.pdf.title', { defaultValue: 'Exportação PDF' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">LaTeX</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.pdf.description', { defaultValue: 'Relatórios profissionais em PDF de alta qualidade gerados com LaTeX. Perfeitos para impressão e compartilhamento.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>

            {/* Differential 8 */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 bg-primary/10 rounded-astro-sm flex items-center justify-center flex-shrink-0">
                    <Moon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-lg mb-2">{t('pages.landing.differentials.darkMode.title', { defaultValue: 'Dark Mode' })}</CardTitle>
                    <Badge variant="secondary" className="mb-3">Auto-detect</Badge>
                    <CardDescription>
                      {t('pages.landing.differentials.darkMode.description', { defaultValue: 'Interface adaptável com modo escuro automático. Perfeito para uso noturno, respeitando suas preferências de sistema.' })}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Authority Proof Section */}
      <section className="py-16 lg:py-24 bg-muted/20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.authority.title', { defaultValue: 'Baseado em Ciência e Tradição' })}
            </h3>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('pages.landing.authority.subtitle', { defaultValue: 'Combinamos métodos milenares com a tecnologia mais avançada disponível' })}
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Authority 1: Traditional Astrology */}
            <Card className="border-0 shadow-xl">
              <CardHeader>
                <div className="w-14 h-14 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Book className="h-7 w-7 text-primary" />
                </div>
                <CardTitle className="text-2xl mb-2">{t('pages.landing.authority.traditional.title', { defaultValue: 'Astrologia Tradicional & Helênica' })}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  {t('pages.landing.authority.traditional.description', { defaultValue: 'Seguimos métodos tradicionais com mais de 2.000 anos de história, baseados nos ensinamentos dos mestres clássicos.' })}
                </p>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-foreground">{t('pages.landing.authority.traditional.elementsTitle', { defaultValue: 'Elementos Considerados:' })}</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.traditional.houseSystems', { defaultValue: 'Sistemas de casas (Placidus, Koch, Whole Sign)' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.traditional.dignities', { defaultValue: 'Dignidades essenciais e acidentais' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.traditional.aspects', { defaultValue: 'Aspectos clássicos e orbes tradicionais' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.traditional.nodes', { defaultValue: 'Nodos lunares e partes arábicas' })}
                    </li>
                  </ul>
                </div>
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-muted-foreground">
                    <strong>{t('pages.landing.authority.traditional.authorityLabel', { defaultValue: 'Autoridade' })}:</strong> {t('pages.landing.authority.traditional.authorityDesc', { defaultValue: 'Baseado nas obras de Ptolomeu (Tetrabiblos), Vettius Valens (Antologia) e Abu Ma\'shar (Liber Introductorius)' })}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Authority 2: Astronomical Precision */}
            <Card className="border-0 shadow-xl">
              <CardHeader>
                <div className="w-14 h-14 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Satellite className="h-7 w-7 text-primary" />
                </div>
                <CardTitle className="text-2xl mb-2">{t('pages.landing.authority.precision.title', { defaultValue: 'Precisão Astronômica' })}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  {t('pages.landing.authority.precision.description', { defaultValue: 'Utilizamos o Swiss Ephemeris, a mesma biblioteca usada por astrônomos profissionais e agências espaciais em todo o mundo.' })}
                </p>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-foreground">{t('pages.landing.authority.precision.specsTitle', { defaultValue: 'Especificações Técnicas:' })}</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.precision.jpl', { defaultValue: 'Efemérides JPL DE431 (NASA/JPL)' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.precision.accuracy', { defaultValue: 'Precisão superior a 0.001° (1 arcsecond)' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.precision.validated', { defaultValue: 'Cálculos validados cientificamente' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.precision.coverage', { defaultValue: 'Cobertura temporal de 13.000 anos' })}
                    </li>
                  </ul>
                </div>
                <div className="pt-4 border-t border-border">
                  <Badge variant="outline" className="bg-primary/5">
                    <Satellite className="h-3 w-3 mr-1" />
                    Powered by Swiss Ephemeris
                  </Badge>
                </div>
              </CardContent>
            </Card>

            {/* Authority 3: AI Technology */}
            <Card className="border-0 shadow-xl">
              <CardHeader>
                <div className="w-14 h-14 bg-primary/10 rounded-astro-md flex items-center justify-center mb-4">
                  <Sparkles className="h-7 w-7 text-primary" />
                </div>
                <CardTitle className="text-2xl mb-2">{t('pages.landing.authority.ai.title', { defaultValue: 'Inteligência Artificial' })}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-muted-foreground">
                  {t('pages.landing.authority.ai.description', { defaultValue: 'Interpretações personalizadas geradas por IA de última geração, treinada extensivamente em textos clássicos de astrologia.' })}
                </p>
                <div className="space-y-2">
                  <p className="text-sm font-semibold text-foreground">{t('pages.landing.authority.ai.techTitle', { defaultValue: 'Tecnologia:' })}</p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.ai.gpt', { defaultValue: 'GPT-4 com prompts especializados' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.ai.knowledge', { defaultValue: 'Base de conhecimento de textos helênicos' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.ai.context', { defaultValue: 'Contexto de astrologia medieval e tradicional' })}
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      {t('pages.landing.authority.ai.analysis', { defaultValue: 'Análise de dignidades e disposições' })}
                    </li>
                  </ul>
                </div>
                <div className="pt-4 border-t border-border">
                  <p className="text-xs text-muted-foreground italic">
                    <strong>{t('pages.landing.authority.ai.importantLabel', { defaultValue: 'Importante' })}:</strong> {t('pages.landing.authority.ai.importantDesc', { defaultValue: 'A IA complementa, mas não substitui, a análise de um astrólogo profissional. Use como ponto de partida para seu estudo.' })}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Security & Compliance Section */}
      <section className="py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.security.title', { defaultValue: 'Sua Privacidade é Nossa Prioridade' })}
            </h3>
            <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
              {t('pages.landing.security.subtitle', { defaultValue: 'Proteção total dos seus dados com conformidade às leis internacionais de privacidade' })}
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
              <div className="flex flex-col items-center gap-3 p-6 bg-card rounded-astro-lg border border-border shadow-md">
                <Shield className="h-12 w-12 text-primary" />
                <Badge variant="secondary" className="text-xs">LGPD Compliant</Badge>
              </div>
              <div className="flex flex-col items-center gap-3 p-6 bg-card rounded-astro-lg border border-border shadow-md">
                <Database className="h-12 w-12 text-primary" />
                <Badge variant="secondary" className="text-xs">GDPR Compliant</Badge>
              </div>
              <div className="flex flex-col items-center gap-3 p-6 bg-card rounded-astro-lg border border-border shadow-md">
                <Lock className="h-12 w-12 text-primary" />
                <Badge variant="secondary" className="text-xs">SSL/TLS Encrypted</Badge>
              </div>
              <div className="flex flex-col items-center gap-3 p-6 bg-card rounded-astro-lg border border-border shadow-md">
                <FileCheck className="h-12 w-12 text-primary" />
                <Badge variant="secondary" className="text-xs">{t('pages.landing.security.auditLog', { defaultValue: 'Complete Audit Log' })}</Badge>
              </div>
            </div>

            <Card className="border-0 shadow-xl">
              <CardContent className="pt-8">
                <div className="space-y-4 text-muted-foreground">
                  <p>
                    {t('pages.landing.security.encryption', { defaultValue: 'Todos os seus dados são protegidos com criptografia SSL/TLS de ponta a ponta durante transmissão e armazenamento. Utilizamos os mais altos padrões de segurança da indústria.' })}
                  </p>
                  <p>
                    {t('pages.landing.security.auditLogs', { defaultValue: 'Mantemos logs completos de auditoria para garantir transparência total sobre o acesso e uso dos seus dados pessoais, conforme exigido pela LGPD e GDPR.' })}
                  </p>
                  <p>
                    {t('pages.landing.security.control', { defaultValue: 'Você tem controle total sobre seus dados: acesso, correção, exclusão e portabilidade garantidos por lei. Seus dados de nascimento nunca são compartilhados com terceiros.' })}
                  </p>
                </div>
                <div className="flex flex-col sm:flex-row gap-4 mt-8 pt-6 border-t border-border">
                  <Button asChild variant="outline" size="sm">
                    <Link to="/privacy">
                      <FileCheck className="mr-2 h-4 w-4" />
                      {t('pages.landing.security.privacyPolicy', { defaultValue: 'Política de Privacidade' })}
                    </Link>
                  </Button>
                  <Button asChild variant="outline" size="sm">
                    <Link to="/terms">
                      <ClipboardCheck className="mr-2 h-4 w-4" />
                      {t('pages.landing.security.termsOfUse', { defaultValue: 'Termos de Uso' })}
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 lg:py-24 bg-muted/20">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('pages.landing.faq.title', { defaultValue: 'Perguntas Frequentes' })}
            </h3>
            <p className="text-muted-foreground text-lg">
              {t('pages.landing.faq.subtitle', { defaultValue: 'Tire suas dúvidas sobre o Real Astrology' })}
            </p>
          </div>

          <Accordion type="single" collapsible className="w-full space-y-4">
            <AccordionItem value="item-1" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q1', { defaultValue: 'O que é um mapa natal?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a1', { defaultValue: 'Um mapa natal (ou carta astral) é uma representação gráfica das posições dos planetas, signos e casas astrológicas no momento exato do seu nascimento. Ele revela potenciais, características pessoais e tendências de vida baseadas na astrologia tradicional.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q2', { defaultValue: 'Preciso saber a hora exata do meu nascimento?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a2', { defaultValue: 'Sim, a hora exata é fundamental para cálculos precisos, especialmente para determinar o Ascendente e as posições das casas astrológicas. Uma diferença de apenas 4 minutos pode alterar o Ascendente. Se não souber, consulte sua certidão de nascimento ou registro hospitalar.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q3', { defaultValue: 'Como vocês calculam o mapa natal?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a3', { defaultValue: 'Utilizamos o Swiss Ephemeris com efemérides JPL DE431 da NASA, garantindo precisão astronômica superior a 0.001°. Nossos algoritmos calculam posições planetárias, casas astrológicas (múltiplos sistemas), aspectos entre planetas e pontos sensíveis como nodos lunares e partes arábicas.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q4', { defaultValue: 'Meus dados estão seguros?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a4', { defaultValue: 'Sim! Utilizamos criptografia SSL/TLS de ponta a ponta, armazenamento seguro e somos 100% conformes com LGPD e GDPR. Seus dados nunca são compartilhados com terceiros. Você tem controle total: pode acessar, corrigir ou excluir seus dados a qualquer momento.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-5" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q5', { defaultValue: 'Posso criar mapas natais para outras pessoas?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a5', { defaultValue: 'Sim! Você pode criar quantos mapas natais quiser - de amigos, familiares, clientes (se for astrólogo profissional), figuras históricas, etc. Não há limite de mapas criados. Apenas informe os dados de nascimento corretos.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-6" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q6', { defaultValue: 'O serviço é realmente gratuito?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a6', { defaultValue: 'Sim, completamente gratuito! Você pode criar mapas natais ilimitados, visualizar gráficos profissionais, acessar interpretações com IA e exportar PDFs sem pagar nada. Não há taxas ocultas, períodos de teste ou limitações. É grátis para sempre.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-7" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q7', { defaultValue: 'As interpretações com IA substituem um astrólogo profissional?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a7', { defaultValue: 'Não. As interpretações geradas por IA são um excelente ponto de partida para estudar seu mapa, mas não substituem a análise aprofundada de um astrólogo profissional qualificado. Use nossa IA como ferramenta de aprendizado e autoconhecimento, mas considere consultar um especialista para análises complexas ou questões específicas.' })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-8" className="bg-card border border-border rounded-astro-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('pages.landing.faq.q8', { defaultValue: 'Como funciona o Dark Mode?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('pages.landing.faq.a8', { defaultValue: 'O Dark Mode pode ser ativado manualmente através do botão de tema na interface, ou configurado para seguir automaticamente as preferências do seu sistema operacional. Ideal para uso noturno, reduz fadiga ocular e economiza bateria em dispositivos com telas OLED.' })}
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 lg:py-32">
        <div className="max-w-4xl mx-auto px-4">
          <Card className="border-0 shadow-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-secondary/10 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
            <CardContent className="p-12 text-center relative">
              <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4 font-display">
                {t('pages.landing.cta.title', { defaultValue: 'Pronto para Descobrir Seu Destino?' })}
              </h3>
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                {t('pages.landing.cta.subtitle', { defaultValue: 'Cadastre-se gratuitamente em menos de 1 minuto e comece a explorar os mistérios do seu mapa natal com precisão astronômica' })}
              </p>
              <Button asChild size="lg" className="text-lg px-8 group">
                <Link to="/register">
                  {t('pages.landing.cta.button', { defaultValue: 'Começar Agora - É Grátis' })}
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <p className="text-sm text-muted-foreground mt-6">
                {t('pages.landing.cta.benefits', { defaultValue: '✓ Sem cartão de crédito    ✓ Sem limite de mapas    ✓ Grátis para sempre' })}
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/logo.png" alt="Real Astrology" className="h-6 w-6" />
                <span className="font-bold text-foreground">Real Astrology</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {t('pages.landing.footer.description', { defaultValue: 'Sistema de mapas natais com precisão astronômica e astrologia tradicional.' })}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('pages.landing.footer.legal', { defaultValue: 'Legal' })}</h4>
              <div className="space-y-2">
                <Link to="/terms" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('pages.landing.footer.terms', { defaultValue: 'Termos de Uso' })}
                </Link>
                <Link to="/privacy" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('pages.landing.footer.privacy', { defaultValue: 'Política de Privacidade' })}
                </Link>
                <Link to="/cookies" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('pages.landing.footer.cookies', { defaultValue: 'Política de Cookies' })}
                </Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('pages.landing.footer.access', { defaultValue: 'Acesso' })}</h4>
              <div className="space-y-2">
                <Link to="/login" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('pages.landing.footer.login', { defaultValue: 'Entrar' })}
                </Link>
                <Link to="/register" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('pages.landing.footer.register', { defaultValue: 'Criar Conta' })}
                </Link>
                <Link to="/dashboard" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  Dashboard
                </Link>
              </div>
            </div>
          </div>
          <div className="pt-8 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Real Astrology. {t('pages.landing.footer.copyright', { defaultValue: 'Todos os direitos reservados.' })}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
