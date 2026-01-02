import * as React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { CreditsProvider } from './contexts/CreditsContext';
import { MotionProvider } from './providers/MotionProvider';
import { LoginPage } from './pages/Login';
import { RegisterPage } from './pages/Register';
import { ChartsPage } from './pages/Charts';
import { NewChartPage } from './pages/NewChart';
import { EditChartPage } from './pages/EditChart';
import { ChartDetailPage } from './pages/ChartDetail';
import { OAuthCallbackPage } from './pages/OAuthCallback';
import { ForgotPasswordPage } from './pages/ForgotPassword';
import { ResetPasswordPage } from './pages/ResetPassword';
import { VerifyEmailPage } from './pages/VerifyEmailPage';
import { ProfilePage } from './pages/Profile';
import { TermsPage } from './pages/Terms';
import { PrivacyPage } from './pages/Privacy';
import { CookiesPage } from './pages/Cookies';
import { ConsentPage } from './pages/Consent';
import { LandingPage } from './pages/Landing';
import { MethodologyPage } from './pages/Methodology';
import { PublicChartsPage } from './pages/PublicCharts';
import { PublicChartDetailPage } from './pages/PublicChartDetail';
import { RagDocumentsPage } from './pages/RagDocuments';
import { PricingPage } from './pages/Pricing';
import { BlogPage } from './pages/Blog';
import { BlogPostPage } from './pages/BlogPost';
import { SubscriptionSuccessPage } from './pages/SubscriptionSuccess';
import { CookieBanner } from './components/CookieBanner';
import { EmailVerificationBanner } from './components/EmailVerificationBanner';
import { FeatureList } from './components/FeatureList';
import { ThemeProvider } from './components/theme-provider';
import { NavActions } from './components/NavActions';
import { chartsService } from './services/charts';
import { amplitudeService } from './services/amplitude';

// shadcn/ui components (used by DashboardPage)
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

function App() {
  return (
    <HelmetProvider>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
        <MotionProvider>
          <AuthProvider>
            <CreditsProvider>
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<LandingPage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                  <Route path="/reset-password" element={<ResetPasswordPage />} />
                  <Route path="/verify-email/:token" element={<VerifyEmailPage />} />
                  <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/profile" element={<ProfilePage />} />
                  <Route path="/charts" element={<ChartsPage />} />
                  <Route path="/charts/new" element={<NewChartPage />} />
                  <Route path="/charts/:id" element={<ChartDetailPage />} />
                  <Route path="/charts/:id/edit" element={<EditChartPage />} />
                  {/* Legal Pages */}
                  <Route path="/terms" element={<TermsPage />} />
                  <Route path="/privacy" element={<PrivacyPage />} />
                  <Route path="/cookies" element={<CookiesPage />} />
                  <Route path="/consent" element={<ConsentPage />} />
                  {/* About Pages */}
                  <Route path="/about/methodology" element={<MethodologyPage />} />
                  {/* Public Charts */}
                  <Route path="/public-charts" element={<PublicChartsPage />} />
                  <Route path="/public-charts/:slug" element={<PublicChartDetailPage />} />
                  {/* RAG Knowledge Base */}
                  <Route path="/rag-documents" element={<RagDocumentsPage />} />
                  {/* Pricing */}
                  <Route path="/pricing" element={<PricingPage />} />
                  <Route path="/subscription/success" element={<SubscriptionSuccessPage />} />
                  {/* Blog */}
                  <Route path="/blog" element={<BlogPage />} />
                  <Route path="/blog/:slug" element={<BlogPostPage />} />
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
                <CookieBanner />
              </BrowserRouter>
            </CreditsProvider>
          </AuthProvider>
        </MotionProvider>
      </ThemeProvider>
    </HelmetProvider>
  );
}

function DashboardPage() {
  const { t } = useTranslation();
  const { user, logout, isLoading } = useAuth();
  const [chartCount, setChartCount] = React.useState<number>(0);
  const [loadingCharts, setLoadingCharts] = React.useState(true);
  const hasTrackedPageView = React.useRef(false);

  // Track dashboard page view
  React.useEffect(() => {
    if (user && !hasTrackedPageView.current) {
      hasTrackedPageView.current = true;
      amplitudeService.track('dashboard_viewed', {
        source: 'dashboard_page',
      });
    }
  }, [user]);

  React.useEffect(() => {
    if (user) {
      loadChartCount();
    }
  }, [user]);

  async function loadChartCount() {
    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      const response = await chartsService.list(token, 1, 1);
      setChartCount(response.total || 0);
    } catch (error) {
      console.error('Error loading chart count:', error);
    } finally {
      setLoadingCharts(false);
    }
  }

  function trackFeatureCardClick(featureName: string) {
    amplitudeService.track('feature_card_clicked', {
      feature_name: featureName,
      source: 'dashboard_page',
    });
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Skeleton className="h-8 w-32 mx-auto mb-2" />
          <Skeleton className="h-4 w-24 mx-auto" />
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <Link
            to="/dashboard"
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
            aria-label={t('common.back')}
          >
            <img src="/logo.png" alt="Real Astrology" className="h-8 w-8" />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-4">
            <NavActions />
            <Button variant="ghost" size="sm" asChild>
              <Link to="/profile">{t('nav.profile')}</Link>
            </Button>
            <span className="text-sm text-muted-foreground">{user.full_name}</span>
            <Button variant="ghost" size="sm" onClick={logout}>
              {t('nav.logout')}
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4">
        {!user.email_verified && (
          <div className="mb-6">
            <EmailVerificationBanner />
          </div>
        )}

        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">{t('dashboardPage.title')}</h2>
          <p className="text-muted-foreground">
            {t('dashboardPage.welcome', { name: user.full_name })}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Row 1: Stats */}
          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.myCharts')}</CardTitle>
            </CardHeader>
            <CardContent>
              {loadingCharts ? (
                <>
                  <Skeleton className="h-9 w-20 mb-2" />
                  <Skeleton className="h-4 w-32" />
                </>
              ) : (
                <>
                  <p className="text-3xl font-bold text-primary">{chartCount}</p>
                  <p className="text-sm text-muted-foreground mt-2">
                    {chartCount === 0
                      ? t('dashboardPage.noChartsYet')
                      : chartCount === 1
                        ? t('dashboardPage.oneChartSaved')
                        : t('dashboardPage.chartsCount', { count: chartCount })}
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.account')}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">{t('dashboardPage.email')}</p>
                <p className="text-sm font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t('dashboardPage.status')}</p>
                {user.email_verified ? (
                  <Badge variant="default">{t('dashboardPage.verified')}</Badge>
                ) : (
                  <Badge variant="secondary">{t('dashboardPage.notVerified')}</Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.createChart')}</CardTitle>
              <CardDescription>{t('dashboardPage.createChartDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" asChild>
                <Link to="/charts/new" onClick={() => trackFeatureCardClick('create_chart')}>
                  {t('dashboardPage.newChartButton')}
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Row 2: Navigation */}
          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.myChartsCard')}</CardTitle>
              <CardDescription>{t('dashboardPage.myChartsDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="secondary" className="w-full" asChild>
                <Link to="/charts" onClick={() => trackFeatureCardClick('my_charts')}>
                  {t('dashboardPage.viewMyCharts')}
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.famousChartsCard')}</CardTitle>
              <CardDescription>{t('dashboardPage.famousChartsDescription')}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" asChild>
                <Link to="/public-charts" onClick={() => trackFeatureCardClick('famous_charts')}>
                  {t('dashboardPage.viewFamousCharts')}
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t('dashboardPage.ragKnowledgeBase', 'RAG Knowledge Base')}</CardTitle>
              <CardDescription>
                {t(
                  'dashboardPage.ragKnowledgeBaseDescription',
                  'Documents used for AI-enhanced interpretations'
                )}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" asChild>
                <Link to="/rag-documents" onClick={() => trackFeatureCardClick('rag_documents')}>
                  {t('dashboardPage.viewRagDocuments', 'View Documents')}
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Dynamic Feature List from GitHub */}
        <div className="mt-8">
          <FeatureList />
        </div>
      </div>
    </div>
  );
}

export default App;
