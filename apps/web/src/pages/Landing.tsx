/**
 * Landing Page - B2C Conversion-focused homepage
 * Issue #159 - Professional B2C copywriting with AIDA/PAS formulas
 *
 * Structure:
 * 1. Hero (AIDA: Attention + Interest)
 * 2. Pain Points (PAS: Problem + Agitate)
 * 3. Solution (PAS: Solution)
 * 4. Benefits (not features)
 * 5. Why Traditional Astrology
 * 6. Social Proof (Testimonials)
 * 7. How It Works
 * 8. FAQ (Objections)
 * 9. Final CTA
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from '@/components/ui/accordion';
import {
  Sparkles,
  Heart,
  Target,
  Zap,
  Compass,
  Star,
  Quote,
  UserPlus,
  Calendar,
  Eye,
  ArrowRight,
  Check,
  Shield,
  CreditCard,
  Clock,
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
            aria-label={t('landing.homeLabel', { defaultValue: 'Home' })}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-3">
            <LanguageSelector />
            <ThemeToggle />
            <Button asChild variant="ghost" size="sm">
              <Link to="/login">{t('landing.login', { defaultValue: 'Entrar' })}</Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/register">{t('landing.signup', { defaultValue: 'Criar Conta' })}</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* ============================================================ */}
      {/* HERO SECTION - AIDA: Attention + Interest */}
      {/* ============================================================ */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 relative">
          <div className="text-center max-w-4xl mx-auto">
            {/* Social Proof Badge */}
            <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-8">
              <Star className="h-4 w-4 fill-primary" />
              {t('landing.hero.socialProof', { defaultValue: 'Mais de 1.000 mapas criados' })}
              <span className="text-muted-foreground">|</span>
              <span>{t('landing.hero.traditional', { defaultValue: 'Astrologia Tradicional' })}</span>
            </div>

            {/* Main Headline - Emotional, stops the scroll */}
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 font-display leading-tight">
              {t('landing.hero.title', { defaultValue: 'Descubra Quem Você Realmente É' })}
            </h2>

            {/* Subheadline - Generates curiosity */}
            <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed max-w-3xl mx-auto">
              {t('landing.hero.subtitle', {
                defaultValue: 'O Real Astrology usa técnicas milenares de astrologia tradicional para criar um mapa natal preciso e interpretações profundas sobre sua personalidade, talentos e caminho de vida.'
              })}
            </p>

            {/* Primary CTA */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
              <Button asChild size="lg" className="group text-lg px-8">
                <Link to="/register">
                  {t('landing.hero.cta', { defaultValue: 'Criar Meu Mapa Grátis' })}
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
            </div>

            {/* Friction Reducers */}
            <div className="flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
              <span className="flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-primary" />
                {t('landing.hero.noCreditCard', { defaultValue: 'Sem cartão de crédito' })}
              </span>
              <span className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-primary" />
                {t('landing.hero.dataSecure', { defaultValue: 'Seus dados seguros (LGPD)' })}
              </span>
              <span className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-primary" />
                {t('landing.hero.twoMinutes', { defaultValue: 'Leva 2 minutos' })}
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* PAIN POINTS SECTION - PAS: Problem + Agitate */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24 bg-card/50">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.pain.title', { defaultValue: 'Você Já Se Sentiu Assim?' })}
            </h3>
          </div>

          {/* Pain Points Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
            {[
              { key: 'purpose', text: t('landing.pain.purpose', { defaultValue: '"Não sei qual é meu propósito de vida"' }) },
              { key: 'talents', text: t('landing.pain.talents', { defaultValue: '"Sinto que tenho talentos que não consigo expressar"' }) },
              { key: 'decisions', text: t('landing.pain.decisions', { defaultValue: '"Tomo decisões e depois me arrependo"' }) },
              { key: 'patterns', text: t('landing.pain.patterns', { defaultValue: '"Não entendo por que repito os mesmos padrões"' }) },
              { key: 'horoscopes', text: t('landing.pain.horoscopes', { defaultValue: '"Horóscopos genéricos nunca fazem sentido pra mim"' }) },
              { key: 'selfknowledge', text: t('landing.pain.selfknowledge', { defaultValue: '"Quero me conhecer melhor, mas não sei como"' }) },
            ].map((pain) => (
              <div
                key={pain.key}
                className="flex items-center gap-3 p-4 bg-muted/50 rounded-lg border border-border/50"
              >
                <span className="text-2xl">😔</span>
                <span className="text-muted-foreground italic">{pain.text}</span>
              </div>
            ))}
          </div>

          {/* Transition/Empathy */}
          <div className="text-center">
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {t('landing.pain.transition', {
                defaultValue: 'Você não está sozinho. A maioria das pessoas passa a vida inteira sem realmente se conhecer. Mas não precisa ser assim.'
              })}
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* SOLUTION SECTION - PAS: Solution */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <Badge variant="secondary" className="mb-4">
              {t('landing.solution.badge', { defaultValue: 'A Solução' })}
            </Badge>
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-6 font-display">
              {t('landing.solution.title', { defaultValue: 'Real Astrology: Autoconhecimento Profundo Através da Astrologia Tradicional' })}
            </h3>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto mb-4">
              {t('landing.solution.description1', {
                defaultValue: 'Diferente de horóscopos genéricos baseados apenas no signo solar, o Real Astrology cria seu mapa natal completo usando as mesmas técnicas que astrólogos usam há mais de 2.000 anos.'
              })}
            </p>
            <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
              {t('landing.solution.description2', {
                defaultValue: 'Seu mapa é único como sua impressão digital — calculado para o momento e local exatos do seu nascimento.'
              })}
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* BENEFITS SECTION - What You'll Discover (not features!) */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24 bg-muted/20">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.benefits.title', { defaultValue: 'O Que Você Vai Descobrir' })}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Benefit 1: Your Essence */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Star className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.essence.title', { defaultValue: 'Sua Essência' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.essence.description', {
                    defaultValue: 'Entenda sua personalidade profunda, além do signo solar. Descubra por que você é do jeito que é.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Benefit 2: Hidden Talents */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.talents.title', { defaultValue: 'Seus Talentos Ocultos' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.talents.description', {
                    defaultValue: 'Identifique habilidades naturais que você talvez nem saiba que tem — e como desenvolvê-las.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Benefit 3: Relationship Patterns */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Heart className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.relationships.title', { defaultValue: 'Seus Padrões em Relacionamentos' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.relationships.description', {
                    defaultValue: 'Compreenda como você ama, o que busca em parceiros e como melhorar suas conexões.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Benefit 4: Your Purpose */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Target className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.purpose.title', { defaultValue: 'Seu Propósito' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.purpose.description', {
                    defaultValue: 'Encontre pistas sobre sua vocação e o caminho que traz mais realização para sua vida.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Benefit 5: Your Challenges */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.challenges.title', { defaultValue: 'Seus Desafios' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.challenges.description', {
                    defaultValue: 'Conheça seus pontos de crescimento e transforme obstáculos em oportunidades.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>

            {/* Benefit 6: Your Current Moment */}
            <Card className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                  <Compass className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{t('landing.benefits.moment.title', { defaultValue: 'Seu Momento Atual' })}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {t('landing.benefits.moment.description', {
                    defaultValue: 'Entenda as influências planetárias atuais e como elas estão impactando sua vida agora.'
                  })}
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* WHY TRADITIONAL ASTROLOGY */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.traditional.title', { defaultValue: 'Por Que "Real" Astrology?' })}
            </h3>
          </div>

          <div className="prose prose-lg dark:prose-invert max-w-none text-center mb-8">
            <p className="text-muted-foreground">
              {t('landing.traditional.intro', {
                defaultValue: 'A astrologia que você vê em revistas e apps populares é uma versão simplificada criada no século XX.'
              })}
            </p>
            <p className="text-muted-foreground">
              {t('landing.traditional.description', {
                defaultValue: 'O Real Astrology resgata a astrologia tradicional — as mesmas técnicas usadas por civilizações antigas, refinadas por séculos de observação.'
              })}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            {[
              {
                title: t('landing.traditional.dignities.title', { defaultValue: 'Dignidades Essenciais' }),
                description: t('landing.traditional.dignities.description', { defaultValue: 'A força real de cada planeta no seu mapa' })
              },
              {
                title: t('landing.traditional.sect.title', { defaultValue: 'Sect (Diurno/Noturno)' }),
                description: t('landing.traditional.sect.description', { defaultValue: 'Seu mapa é de dia ou de noite? Isso muda tudo' })
              },
              {
                title: t('landing.traditional.arabicParts.title', { defaultValue: 'Partes Árabes' }),
                description: t('landing.traditional.arabicParts.description', { defaultValue: 'Pontos sensíveis que revelam áreas específicas da vida' })
              },
              {
                title: t('landing.traditional.temperament.title', { defaultValue: 'Temperamento' }),
                description: t('landing.traditional.temperament.description', { defaultValue: 'Seu equilíbrio dos 4 elementos segundo a tradição' })
              },
            ].map((item, index) => (
              <div key={index} className="flex items-start gap-3 p-4 bg-card rounded-lg border border-border">
                <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-foreground">{item.title}</p>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center">
            <p className="text-muted-foreground font-medium">
              {t('landing.traditional.conclusion', { defaultValue: 'Não é achismo. É astronomia + tradição + interpretação profunda.' })}
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* SOCIAL PROOF - Testimonials */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24 bg-card/50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.testimonials.title', { defaultValue: 'O Que Nossos Usuários Dizem' })}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Testimonial 1 */}
            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <Quote className="h-8 w-8 text-primary/30 mb-4" />
                <p className="text-muted-foreground mb-6 italic">
                  {t('landing.testimonials.t1.quote', {
                    defaultValue: '"Eu sempre achei que era \'só\' uma canceriana sensível demais. Quando vi meu mapa completo, entendi que tenho Lua em Escorpião e Marte na Casa 1. Finalmente fez sentido por que sou tão intensa!"'
                  })}
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <span className="text-primary font-semibold">M</span>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{t('landing.testimonials.t1.name', { defaultValue: 'Marina, 28 anos' })}</p>
                    <p className="text-sm text-muted-foreground">{t('landing.testimonials.t1.location', { defaultValue: 'São Paulo' })}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Testimonial 2 */}
            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <Quote className="h-8 w-8 text-primary/30 mb-4" />
                <p className="text-muted-foreground mb-6 italic">
                  {t('landing.testimonials.t2.quote', {
                    defaultValue: '"Fiz meu mapa em vários sites, mas nunca tinha visto análise de Sect e Dignidades. O Real Astrology me mostrou que Saturno no meu mapa é muito mais positivo do que eu pensava. Mudou minha perspectiva."'
                  })}
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <span className="text-primary font-semibold">C</span>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{t('landing.testimonials.t2.name', { defaultValue: 'Carlos, 35 anos' })}</p>
                    <p className="text-sm text-muted-foreground">{t('landing.testimonials.t2.location', { defaultValue: 'Belo Horizonte' })}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Testimonial 3 */}
            <Card className="border-0 shadow-lg">
              <CardContent className="pt-6">
                <Quote className="h-8 w-8 text-primary/30 mb-4" />
                <p className="text-muted-foreground mb-6 italic">
                  {t('landing.testimonials.t3.quote', {
                    defaultValue: '"As interpretações com IA são incríveis. Parece que alguém que me conhece há anos escreveu sobre mim. Recomendo para quem quer se conhecer de verdade."'
                  })}
                </p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                    <span className="text-primary font-semibold">J</span>
                  </div>
                  <div>
                    <p className="font-semibold text-foreground">{t('landing.testimonials.t3.name', { defaultValue: 'Juliana, 42 anos' })}</p>
                    <p className="text-sm text-muted-foreground">{t('landing.testimonials.t3.location', { defaultValue: 'Porto Alegre' })}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* HOW IT WORKS */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24">
        <div className="max-w-5xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.howItWorks.title', { defaultValue: 'Criar Seu Mapa É Simples' })}
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Step 1 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <UserPlus className="h-8 w-8 text-primary" />
                <span className="absolute -top-2 -right-2 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">1</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">
                {t('landing.howItWorks.step1.title', { defaultValue: 'Cadastre-se Grátis' })}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t('landing.howItWorks.step1.description', { defaultValue: 'Leva menos de 1 minuto' })}
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <Calendar className="h-8 w-8 text-primary" />
                <span className="absolute -top-2 -right-2 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">2</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">
                {t('landing.howItWorks.step2.title', { defaultValue: 'Insira Seus Dados' })}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t('landing.howItWorks.step2.description', { defaultValue: 'Data, hora e local de nascimento' })}
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <Sparkles className="h-8 w-8 text-primary" />
                <span className="absolute -top-2 -right-2 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">3</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">
                {t('landing.howItWorks.step3.title', { defaultValue: 'Receba Seu Mapa' })}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t('landing.howItWorks.step3.description', { defaultValue: 'Visualização profissional + interpretações' })}
              </p>
            </div>

            {/* Step 4 */}
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 relative">
                <Eye className="h-8 w-8 text-primary" />
                <span className="absolute -top-2 -right-2 w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center font-bold text-sm">4</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">
                {t('landing.howItWorks.step4.title', { defaultValue: 'Explore e Descubra' })}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t('landing.howItWorks.step4.description', { defaultValue: 'Navegue e descubra cada aspecto de si mesmo' })}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/* FAQ - Objections */}
      {/* ============================================================ */}
      <section className="py-16 lg:py-24 bg-muted/20">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-foreground mb-4 font-display">
              {t('landing.faq.title', { defaultValue: 'Perguntas Frequentes' })}
            </h3>
          </div>

          <Accordion type="single" collapsible className="w-full space-y-4">
            <AccordionItem value="item-1" className="bg-card border border-border rounded-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('landing.faq.q1.question', { defaultValue: 'Precisa saber a hora exata de nascimento?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('landing.faq.q1.answer', {
                  defaultValue: 'A hora é importante para calcular o Ascendente e as Casas. Se não souber, você pode consultar sua certidão de nascimento ou usar uma hora aproximada (o mapa será menos preciso nessas áreas).'
                })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-2" className="bg-card border border-border rounded-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('landing.faq.q2.question', { defaultValue: 'Qual a diferença para outros sites de mapa astral?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('landing.faq.q2.answer', {
                  defaultValue: 'O Real Astrology usa astrologia tradicional com técnicas como Dignidades Essenciais, Sect e Partes Árabes — que a maioria dos sites modernos ignora. Além disso, nossas interpretações são geradas por IA treinada em textos clássicos de astrologia.'
                })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-3" className="bg-card border border-border rounded-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('landing.faq.q3.question', { defaultValue: 'É realmente grátis?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('landing.faq.q3.answer', {
                  defaultValue: 'Sim! O mapa completo e interpretações básicas são gratuitos. Funcionalidades premium (como relatórios em PDF e análises avançadas) podem ter custo adicional no futuro, mas o essencial será sempre grátis.'
                })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-4" className="bg-card border border-border rounded-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('landing.faq.q4.question', { defaultValue: 'Meus dados estão seguros?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('landing.faq.q4.answer', {
                  defaultValue: 'Absolutamente. Seguimos a LGPD e nunca compartilhamos seus dados com terceiros. Você pode excluir sua conta a qualquer momento e todos os seus dados serão removidos.'
                })}
              </AccordionContent>
            </AccordionItem>

            <AccordionItem value="item-5" className="bg-card border border-border rounded-lg px-6">
              <AccordionTrigger className="text-left hover:no-underline">
                {t('landing.faq.q5.question', { defaultValue: 'As interpretações com IA substituem um astrólogo?' })}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {t('landing.faq.q5.answer', {
                  defaultValue: 'As interpretações são um excelente ponto de partida para autoconhecimento, mas não substituem a análise de um astrólogo profissional para questões específicas ou complexas. Use como ferramenta de estudo e reflexão.'
                })}
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </section>

      {/* ============================================================ */}
      {/* FINAL CTA */}
      {/* ============================================================ */}
      <section className="py-20 lg:py-32">
        <div className="max-w-4xl mx-auto px-4">
          <Card className="border-0 shadow-2xl bg-gradient-to-br from-primary/10 via-primary/5 to-secondary/10 overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-secondary/5 pointer-events-none" />
            <CardContent className="p-12 text-center relative">
              <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4 font-display">
                {t('landing.finalCta.title', { defaultValue: 'Pronto Para Se Conhecer de Verdade?' })}
              </h3>
              <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                {t('landing.finalCta.subtitle', {
                  defaultValue: 'Seu mapa natal está esperando. É gratuito, leva 2 minutos e pode mudar a forma como você se vê para sempre.'
                })}
              </p>
              <Button asChild size="lg" className="text-lg px-8 group">
                <Link to="/register">
                  {t('landing.finalCta.button', { defaultValue: 'Criar Meu Mapa Agora — É Grátis' })}
                  <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <div className="flex flex-wrap justify-center gap-6 mt-8 text-sm text-muted-foreground">
                <span className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" />
                  {t('landing.finalCta.benefit1', { defaultValue: 'Sem cartão de crédito' })}
                </span>
                <span className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" />
                  {t('landing.finalCta.benefit2', { defaultValue: 'Seus dados seguros (LGPD)' })}
                </span>
                <span className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-primary" />
                  {t('landing.finalCta.benefit3', { defaultValue: 'Cancele quando quiser' })}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* ============================================================ */}
      {/* FOOTER */}
      {/* ============================================================ */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <img src="/logo.png" alt="Real Astrology" className="h-6 w-6" />
                <span className="font-bold text-foreground">Real Astrology</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {t('landing.footer.tagline', { defaultValue: 'Astrologia Tradicional Para o Mundo Moderno' })}
              </p>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('landing.footer.legal', { defaultValue: 'Legal' })}</h4>
              <div className="space-y-2">
                <Link to="/terms" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('landing.footer.terms', { defaultValue: 'Termos de Uso' })}
                </Link>
                <Link to="/privacy" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('landing.footer.privacy', { defaultValue: 'Política de Privacidade' })}
                </Link>
                <Link to="/cookies" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('landing.footer.cookies', { defaultValue: 'Política de Cookies' })}
                </Link>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-foreground mb-4">{t('landing.footer.access', { defaultValue: 'Acesso' })}</h4>
              <div className="space-y-2">
                <Link to="/login" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('landing.footer.login', { defaultValue: 'Entrar' })}
                </Link>
                <Link to="/register" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  {t('landing.footer.register', { defaultValue: 'Criar Conta' })}
                </Link>
                <Link to="/dashboard" className="block text-sm text-muted-foreground hover:text-primary transition-colors">
                  Dashboard
                </Link>
              </div>
            </div>
          </div>
          <div className="pt-8 border-t border-border text-center">
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} Real Astrology. {t('landing.footer.madeWith', { defaultValue: 'Feito com ♄ e ♃ no Brasil.' })}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
