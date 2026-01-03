/**
 * Pricing Page - Subscription plans with Stripe checkout
 */

import { useEffect, useRef, useState } from 'react';
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
import { Skeleton } from '@/components/ui/skeleton';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import { useCredits } from '@/contexts/CreditsContext';
import { amplitudeService } from '@/services/amplitude';
import {
  getStripeConfig,
  formatPriceBRL,
  redirectToCheckout,
  redirectToPortal,
  StripeConfig,
} from '@/services/stripe';
import {
  Check,
  Crown,
  Sparkles,
  Star,
  Zap,
  ArrowLeft,
  Loader2,
  Infinity,
  Settings,
} from 'lucide-react';

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
  credits: string;
  features: PlanFeature[];
  highlighted?: boolean;
  badge?: string;
  ctaText: string;
  disabled?: boolean;
  planType?: 'starter' | 'pro' | 'unlimited';
}

export function PricingPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { credits } = useCredits();
  const [searchParams] = useSearchParams();
  const hasTrackedPageView = useRef(false);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [stripeConfig, setStripeConfig] = useState<StripeConfig | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);

  const currentPlan = credits?.plan_type || 'free';
  const isPortuguese = i18n.language.startsWith('pt');

  // Fetch Stripe config on mount
  useEffect(() => {
    async function fetchConfig() {
      try {
        const config = await getStripeConfig();
        setStripeConfig(config);
      } catch (error) {
        console.error('Failed to fetch Stripe config:', error);
      } finally {
        setLoadingConfig(false);
      }
    }
    fetchConfig();
  }, []);

  // Track page view on mount (with ref guard to prevent StrictMode double-tracking)
  useEffect(() => {
    if (!hasTrackedPageView.current) {
      amplitudeService.track('pricing_page_viewed', {
        source: searchParams.get('source') || 'direct',
        current_plan: currentPlan,
        ...(user?.id && { user_id: user.id }),
      });
      hasTrackedPageView.current = true;
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Track once on mount only

  // Format price based on locale
  const formatPrice = (planId: string): string => {
    if (!stripeConfig?.plans[planId]) {
      // Fallback for free plan or if config not loaded
      if (planId === 'free') return isPortuguese ? 'R$ 0' : '$0';
      return '...';
    }
    const priceCents = stripeConfig.plans[planId].price_brl;
    if (isPortuguese) {
      return formatPriceBRL(priceCents);
    }
    // Convert BRL to approximate USD (simplified - in production use proper conversion)
    const usdCents = Math.round(priceCents / 5);
    return `$${(usdCents / 100).toFixed(2)}`;
  };

  // Get credits for a plan
  const getCredits = (planId: string): string => {
    if (planId === 'free') return t('pricing.plans.free.credits');
    if (!stripeConfig?.plans[planId]) return '...';
    const credits = stripeConfig.plans[planId].credits;
    if (credits === null) return t('pricing.unlimited');
    return `${credits} ${t('pricing.credits')}`;
  };

  // Handle plan selection
  const handlePlanClick = async (plan: Plan) => {
    if (plan.disabled || !plan.planType) return;

    amplitudeService.track('pricing_plan_clicked', {
      plan_name: plan.id,
      plan_type: plan.planType,
      current_plan: currentPlan,
      source: 'pricing_page',
      ...(user?.id && { user_id: user.id }),
    });

    if (!user) {
      // Not logged in - redirect to register
      window.location.href = `/register?plan=${plan.planType}`;
      return;
    }

    setLoadingPlan(plan.id);
    try {
      await redirectToCheckout(plan.planType);
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setLoadingPlan(null);
    }
  };

  // Handle manage subscription
  const handleManageSubscription = async () => {
    setLoadingPlan('manage');
    try {
      await redirectToPortal();
    } catch (error) {
      console.error('Failed to create portal session:', error);
      setLoadingPlan(null);
    }
  };

  const plans: Plan[] = [
    {
      id: 'free',
      name: t('pricing.plans.free.name'),
      description: t('pricing.plans.free.description'),
      price: formatPrice('free'),
      period: t('pricing.period'),
      credits: getCredits('free'),
      features: [
        { text: t('pricing.features.natalCharts'), included: true },
        { text: t('pricing.features.credits10'), included: true },
        { text: t('pricing.features.svgVisualization'), included: true },
        { text: t('pricing.features.basicInterpretations'), included: true },
        { text: t('pricing.features.advancedInterpretations'), included: false },
        { text: t('pricing.features.pdfReport'), included: false },
        { text: t('pricing.features.prioritySupport'), included: false },
      ],
      ctaText: currentPlan === 'free' ? t('pricing.currentPlan') : t('pricing.select'),
      disabled: currentPlan === 'free',
    },
    {
      id: 'starter',
      name: t('pricing.plans.starter.name'),
      description: t('pricing.plans.starter.description'),
      price: formatPrice('starter'),
      period: t('pricing.period'),
      credits: getCredits('starter'),
      features: [
        { text: t('pricing.features.natalCharts'), included: true },
        { text: t('pricing.features.credits50'), included: true },
        { text: t('pricing.features.svgVisualization'), included: true },
        { text: t('pricing.features.advancedInterpretations'), included: true },
        { text: t('pricing.features.solarReturn'), included: true },
        { text: t('pricing.features.pdfReport'), included: true },
        { text: t('pricing.features.emailSupport'), included: true },
      ],
      ctaText: currentPlan === 'starter' ? t('pricing.currentPlan') : t('pricing.subscribe'),
      disabled: currentPlan === 'starter',
      planType: 'starter',
    },
    {
      id: 'pro',
      name: t('pricing.plans.pro.name'),
      description: t('pricing.plans.pro.description'),
      price: formatPrice('pro'),
      period: t('pricing.period'),
      credits: getCredits('pro'),
      features: [
        { text: t('pricing.features.natalCharts'), included: true },
        { text: t('pricing.features.credits200'), included: true },
        { text: t('pricing.features.allStarterFeatures'), included: true },
        { text: t('pricing.features.saturnReturn'), included: true },
        { text: t('pricing.features.longevityAnalysis'), included: true },
        { text: t('pricing.features.profectionsSoon'), included: true },
        { text: t('pricing.features.prioritySupport'), included: true },
      ],
      highlighted: true,
      badge: t('pricing.recommended'),
      ctaText: currentPlan === 'pro' ? t('pricing.currentPlan') : t('pricing.subscribe'),
      disabled: currentPlan === 'pro',
      planType: 'pro',
    },
    {
      id: 'unlimited',
      name: t('pricing.plans.unlimited.name'),
      description: t('pricing.plans.unlimited.description'),
      price: formatPrice('unlimited'),
      period: t('pricing.period'),
      credits: getCredits('unlimited'),
      features: [
        { text: t('pricing.features.natalCharts'), included: true },
        { text: t('pricing.features.unlimitedCredits'), included: true },
        { text: t('pricing.features.allProFeatures'), included: true },
        { text: t('pricing.features.earlyAccess'), included: true },
        { text: t('pricing.features.vipSupport'), included: true },
        { text: t('pricing.features.discountedConsultations'), included: true },
        { text: t('pricing.features.exclusiveBadge'), included: true },
      ],
      badge: t('pricing.premium'),
      ctaText: currentPlan === 'unlimited' ? t('pricing.currentPlan') : t('pricing.subscribe'),
      disabled: currentPlan === 'unlimited',
      planType: 'unlimited',
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
      <section className="py-12 lg:py-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-6">
            <Crown className="h-4 w-4" />
            {t('pricing.badge', { defaultValue: 'Planos e Preços' })}
          </div>

          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            {t('pricing.title', { defaultValue: 'Escolha o plano ideal para você' })}
          </h2>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            {t('pricing.subtitle', {
              defaultValue:
                'Desbloqueie todo o potencial da astrologia tradicional com nossos planos.',
            })}
          </p>

          {/* Current Plan Indicator */}
          {user && (
            <div className="mb-8 inline-flex items-center gap-4 bg-muted/50 px-4 py-2 rounded-lg">
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-primary" />
                <span className="text-sm text-muted-foreground">{t('pricing.yourPlan')}</span>
                <Badge variant={currentPlan !== 'free' ? 'default' : 'secondary'}>
                  {t(`pricing.plans.${currentPlan}.name`)}
                </Badge>
              </div>
              {credits && currentPlan !== 'free' && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleManageSubscription}
                  disabled={loadingPlan === 'manage'}
                >
                  {loadingPlan === 'manage' ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Settings className="h-4 w-4 mr-2" />
                  )}
                  {t('pricing.manageSubscription')}
                </Button>
              )}
            </div>
          )}

          {/* Plans Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {loadingConfig
              ? // Loading skeletons
                Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i} className="flex flex-col">
                    <CardHeader className="text-center pb-2">
                      <Skeleton className="h-6 w-24 mx-auto mb-2" />
                      <Skeleton className="h-4 w-32 mx-auto" />
                    </CardHeader>
                    <CardContent className="text-center flex-1">
                      <Skeleton className="h-10 w-20 mx-auto mb-2" />
                      <Skeleton className="h-5 w-16 mx-auto mb-4" />
                      <div className="space-y-2">
                        {Array.from({ length: 5 }).map((_, j) => (
                          <Skeleton key={j} className="h-4 w-full" />
                        ))}
                      </div>
                    </CardContent>
                    <CardFooter className="pt-4">
                      <Skeleton className="h-10 w-full" />
                    </CardFooter>
                  </Card>
                ))
              : plans.map((plan) => (
                  <Card
                    key={plan.id}
                    className={`relative flex flex-col ${
                      plan.highlighted
                        ? 'border-primary shadow-lg shadow-primary/10'
                        : 'border-border'
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
                      <CardTitle className="flex items-center justify-center gap-2 text-xl">
                        {plan.id === 'unlimited' && <Crown className="h-5 w-5 text-amber-500" />}
                        {plan.name}
                      </CardTitle>
                      <CardDescription className="text-sm">{plan.description}</CardDescription>
                    </CardHeader>

                    <CardContent className="text-center flex-1">
                      <div className="mb-4">
                        <span className="text-3xl font-bold text-foreground">{plan.price}</span>
                        <span className="text-muted-foreground text-sm">{plan.period}</span>
                      </div>

                      <div className="mb-4 flex items-center justify-center gap-1 text-primary font-medium">
                        {plan.id === 'unlimited' ? (
                          <>
                            <Infinity className="h-4 w-4" />
                            <span>{t('pricing.unlimited')}</span>
                          </>
                        ) : (
                          <span>{plan.credits}</span>
                        )}
                      </div>

                      <ul className="space-y-2 text-left text-sm">
                        {plan.features.map((feature, index) => (
                          <li
                            key={index}
                            className={`flex items-start gap-2 ${
                              feature.included
                                ? 'text-foreground'
                                : 'text-muted-foreground line-through'
                            }`}
                          >
                            <Check
                              className={`h-4 w-4 flex-shrink-0 mt-0.5 ${
                                feature.included ? 'text-green-500' : 'text-muted-foreground/50'
                              }`}
                            />
                            {feature.text}
                          </li>
                        ))}
                      </ul>
                    </CardContent>

                    <CardFooter className="pt-4">
                      {plan.id === 'free' ? (
                        !user ? (
                          <Button asChild className="w-full" variant="outline">
                            <Link to="/register">
                              <Zap className="h-4 w-4 mr-2" />
                              {t('pricing.startFree')}
                            </Link>
                          </Button>
                        ) : (
                          <Button className="w-full" variant="outline" disabled>
                            <Check className="h-4 w-4 mr-2" />
                            {plan.ctaText}
                          </Button>
                        )
                      ) : (
                        <Button
                          className={`w-full ${
                            plan.highlighted && !plan.disabled
                              ? 'bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white'
                              : ''
                          }`}
                          variant={plan.highlighted ? 'default' : 'outline'}
                          disabled={plan.disabled || loadingPlan === plan.id}
                          onClick={() => handlePlanClick(plan)}
                        >
                          {loadingPlan === plan.id ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              {t('pricing.processing')}
                            </>
                          ) : plan.disabled ? (
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

          {/* FAQ / Info Section */}
          <div className="mt-12 p-6 bg-muted/30 rounded-xl max-w-3xl mx-auto text-left">
            <h3 className="text-lg font-semibold text-foreground mb-4 text-center">
              {t('pricing.faq.title')}
            </h3>
            <div className="space-y-4 text-sm">
              <div>
                <p className="font-medium text-foreground">{t('pricing.faq.whatAreCredits')}</p>
                <p className="text-muted-foreground">{t('pricing.faq.whatAreCreditsAnswer')}</p>
              </div>
              <div>
                <p className="font-medium text-foreground">
                  {t('pricing.faq.doCreditsAccumulate')}
                </p>
                <p className="text-muted-foreground">
                  {t('pricing.faq.doCreditsAccumulateAnswer')}
                </p>
              </div>
              <div>
                <p className="font-medium text-foreground">{t('pricing.faq.canICancel')}</p>
                <p className="text-muted-foreground">{t('pricing.faq.canICancelAnswer')}</p>
              </div>
            </div>
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
