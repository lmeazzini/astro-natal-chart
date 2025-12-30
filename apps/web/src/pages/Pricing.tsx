/**
 * Pricing Page - Placeholder for subscription plans
 *
 * This is a placeholder page for the premium subscription system.
 * The actual payment integration will be implemented in a future issue.
 */

import { useEffect, useRef } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import { usePermissions } from '@/hooks/usePermissions';
import { amplitudeService } from '@/services/amplitude';
import { Check, Crown, Sparkles, Star, Zap, ArrowLeft } from 'lucide-react';

interface PlanFeature {
  text: string;
  included: boolean;
}

interface Plan {
  id: string;
  name: string;
  description: string;
  price: string;
  period: string;
  features: PlanFeature[];
  highlighted?: boolean;
  badge?: string;
  ctaText: string;
  disabled?: boolean;
}

export function PricingPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { isPremium, isAdmin, role } = usePermissions();
  const [searchParams] = useSearchParams();
  const hasTrackedPageView = useRef(false);

  // Track page view on mount (with ref guard to prevent StrictMode double-tracking)
  useEffect(() => {
    if (!hasTrackedPageView.current) {
      amplitudeService.track('pricing_page_viewed', {
        source: searchParams.get('source') || 'direct',
        user_tier: role || 'anonymous',
        ...(user?.id && { user_id: user.id }),
      });
      hasTrackedPageView.current = true;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Track once on mount only

  // Track plan button clicks (skip if button is disabled)
  const handlePlanClick = (planName: string, isDisabled?: boolean) => {
    if (isDisabled) return; // Don't track clicks on disabled buttons
    amplitudeService.track('pricing_plan_clicked', {
      plan_name: planName,
      current_tier: role || 'anonymous',
      billing_cycle: 'monthly',
      source: 'pricing_page',
      ...(user?.id && { user_id: user.id }),
    });
  };

  const plans: Plan[] = [
    {
      id: 'free',
      name: t('pricing.plans.free.name', { defaultValue: 'Gratuito' }),
      description: t('pricing.plans.free.description', {
        defaultValue: 'Para começar sua jornada astrológica',
      }),
      price: t('pricing.plans.free.price', { defaultValue: 'R$ 0' }),
      period: t('pricing.plans.free.period', { defaultValue: '/mês' }),
      features: [
        {
          text: t('pricing.features.natalCharts', { defaultValue: 'Mapas natais ilimitados' }),
          included: true,
        },
        {
          text: t('pricing.features.basicInterpretations', {
            defaultValue: 'Interpretações básicas',
          }),
          included: true,
        },
        {
          text: t('pricing.features.chartVisualization', {
            defaultValue: 'Visualização de mapa SVG',
          }),
          included: true,
        },
        {
          text: t('pricing.features.horary', { defaultValue: 'Astrologia Horária' }),
          included: false,
        },
        {
          text: t('pricing.features.profections', { defaultValue: 'Profecções' }),
          included: false,
        },
        { text: t('pricing.features.firdaria', { defaultValue: 'Firdária' }), included: false },
        {
          text: t('pricing.features.solarReturn', { defaultValue: 'Revolução Solar' }),
          included: false,
        },
        {
          text: t('pricing.features.prioritySupport', { defaultValue: 'Suporte prioritário' }),
          included: false,
        },
      ],
      ctaText: !user
        ? t('pricing.getStartedFree', { defaultValue: 'Começar Grátis' })
        : role === 'free'
          ? t('pricing.currentPlan', { defaultValue: 'Plano Atual' })
          : t('pricing.downgrade', { defaultValue: 'Fazer Downgrade' }),
      disabled: role === 'free',
    },
    {
      id: 'premium',
      name: t('pricing.plans.premium.name', { defaultValue: 'Premium' }),
      description: t('pricing.plans.premium.description', {
        defaultValue: 'Para astrólogos sérios que buscam profundidade',
      }),
      price: t('pricing.plans.premium.price', { defaultValue: 'R$ 29,90' }),
      period: t('pricing.plans.premium.period', { defaultValue: '/mês' }),
      features: [
        {
          text: t('pricing.features.natalCharts', { defaultValue: 'Mapas natais ilimitados' }),
          included: true,
        },
        {
          text: t('pricing.features.advancedInterpretations', {
            defaultValue: 'Interpretações avançadas com IA',
          }),
          included: true,
        },
        {
          text: t('pricing.features.chartVisualization', {
            defaultValue: 'Visualização de mapa SVG',
          }),
          included: true,
        },
        {
          text: t('pricing.features.horary', { defaultValue: 'Astrologia Horária' }),
          included: true,
        },
        { text: t('pricing.features.profections', { defaultValue: 'Profecções' }), included: true },
        { text: t('pricing.features.firdaria', { defaultValue: 'Firdária' }), included: true },
        {
          text: t('pricing.features.solarReturn', { defaultValue: 'Revolução Solar' }),
          included: true,
        },
        {
          text: t('pricing.features.prioritySupport', { defaultValue: 'Suporte prioritário' }),
          included: true,
        },
      ],
      highlighted: true,
      badge: t('pricing.recommended', { defaultValue: 'Recomendado' }),
      ctaText: isPremium
        ? t('pricing.currentPlan', { defaultValue: 'Plano Atual' })
        : t('pricing.subscribe', { defaultValue: 'Assinar Premium' }),
      disabled: isPremium,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/10 to-secondary/5">
      {/* Header */}
      <nav className="bg-card/80 backdrop-blur-sm border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-3">
            <LanguageSelector />
            <ThemeToggle />
            {user ? (
              <Button asChild variant="ghost" size="sm">
                <Link to="/dashboard">{t('nav.dashboard', { defaultValue: 'Dashboard' })}</Link>
              </Button>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm">
                  <Link to="/login">{t('landing.login', { defaultValue: 'Entrar' })}</Link>
                </Button>
                <Button asChild size="sm">
                  <Link to="/register">{t('landing.signup', { defaultValue: 'Criar Conta' })}</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Back Link */}
      <div className="max-w-7xl mx-auto px-4 pt-6">
        <Link
          to={user ? '/dashboard' : '/'}
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          {t('common.back', { defaultValue: 'Voltar' })}
        </Link>
      </div>

      {/* Hero Section */}
      <section className="py-12 lg:py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Crown className="h-4 w-4" />
            {t('pricing.badge', { defaultValue: 'Planos e Preços' })}
          </div>

          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            {t('pricing.title', { defaultValue: 'Escolha o plano ideal para você' })}
          </h2>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-12">
            {t('pricing.subtitle', {
              defaultValue:
                'Desbloqueie todo o potencial da astrologia tradicional com nossos planos Premium.',
            })}
          </p>

          {/* Current Plan Indicator */}
          {user && (
            <div className="mb-8 inline-flex items-center gap-2 bg-muted/50 px-4 py-2 rounded-lg">
              <Star className="h-4 w-4 text-primary" />
              <span className="text-sm text-muted-foreground">
                {t('pricing.yourPlan', { defaultValue: 'Seu plano atual:' })}
              </span>
              <Badge variant={isPremium ? 'default' : 'secondary'}>
                {isAdmin
                  ? 'Admin'
                  : isPremium
                    ? 'Premium'
                    : t('pricing.plans.free.name', { defaultValue: 'Gratuito' })}
              </Badge>
            </div>
          )}

          {/* Plans Grid */}
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {plans.map((plan) => (
              <Card
                key={plan.id}
                className={`relative ${
                  plan.highlighted ? 'border-primary shadow-lg shadow-primary/10' : 'border-border'
                }`}
              >
                {plan.badge && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-primary text-primary-foreground">
                      <Sparkles className="h-3 w-3 mr-1" />
                      {plan.badge}
                    </Badge>
                  </div>
                )}

                <CardHeader className="text-center pb-2">
                  <CardTitle className="flex items-center justify-center gap-2 text-2xl">
                    {plan.id === 'premium' && <Crown className="h-6 w-6 text-amber-500" />}
                    {plan.name}
                  </CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>

                <CardContent className="text-center">
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-foreground">{plan.price}</span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>

                  <ul className="space-y-3 text-left">
                    {plan.features.map((feature, index) => (
                      <li
                        key={index}
                        className={`flex items-center gap-2 text-sm ${
                          feature.included
                            ? 'text-foreground'
                            : 'text-muted-foreground line-through'
                        }`}
                      >
                        <Check
                          className={`h-4 w-4 flex-shrink-0 ${
                            feature.included ? 'text-green-500' : 'text-muted-foreground/50'
                          }`}
                        />
                        {feature.text}
                      </li>
                    ))}
                  </ul>
                </CardContent>

                <CardFooter>
                  {/* Non-authenticated users clicking free plan go to register */}
                  {!user && plan.id === 'free' ? (
                    <Button
                      asChild
                      className="w-full"
                      variant="outline"
                      onClick={() => handlePlanClick(plan.id, plan.disabled)}
                    >
                      <Link to="/register">
                        <Zap className="h-4 w-4 mr-2" />
                        {plan.ctaText}
                      </Link>
                    </Button>
                  ) : (
                    <Button
                      className={`w-full ${
                        plan.highlighted && !plan.disabled
                          ? 'bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white'
                          : ''
                      }`}
                      variant={plan.highlighted ? 'default' : 'outline'}
                      disabled={plan.disabled}
                      onClick={() => handlePlanClick(plan.id, plan.disabled)}
                    >
                      {plan.disabled ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          {plan.ctaText}
                        </>
                      ) : (
                        <>
                          <Zap className="h-4 w-4 mr-2" />
                          {plan.ctaText}
                        </>
                      )}
                    </Button>
                  )}
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Coming Soon Notice */}
          <div className="mt-12 p-6 bg-muted/30 rounded-xl max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              {t('pricing.comingSoon.title', { defaultValue: 'Em breve!' })}
            </h3>
            <p className="text-muted-foreground">
              {t('pricing.comingSoon.description', {
                defaultValue:
                  'O sistema de assinaturas está em desenvolvimento. Enquanto isso, aproveite as funcionalidades gratuitas e fique atento para novidades!',
              })}
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border bg-card/50">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>
            © {new Date().getFullYear()} Real Astrology.{' '}
            {t('footer.allRightsReserved', { defaultValue: 'Todos os direitos reservados.' })}
          </p>
        </div>
      </footer>
    </div>
  );
}
