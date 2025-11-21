import * as React from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { MotionProvider } from './providers/MotionProvider';
import { LoginPage } from './pages/Login';
import { RegisterPage } from './pages/Register';
import { ChartsPage } from './pages/Charts';
import { NewChartPage } from './pages/NewChart';
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
import { CookieBanner } from './components/CookieBanner';
import { EmailVerificationBanner } from './components/EmailVerificationBanner';
import { ThemeProvider } from './components/theme-provider';
import { ThemeToggle } from './components/ThemeToggle';

// shadcn/ui components (used by DashboardPage)
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

function App() {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <MotionProvider>
        <AuthProvider>
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
          {/* Legal Pages */}
          <Route path="/terms" element={<TermsPage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/cookies" element={<CookiesPage />} />
          <Route path="/consent" element={<ConsentPage />} />
          {/* About Pages */}
          <Route path="/about/methodology" element={<MethodologyPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <CookieBanner />
          </BrowserRouter>
        </AuthProvider>
      </MotionProvider>
    </ThemeProvider>
  );
}

function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const [chartCount, setChartCount] = React.useState<number>(0);
  const [loadingCharts, setLoadingCharts] = React.useState(true);

  React.useEffect(() => {
    if (user) {
      loadChartCount();
    }
  }, [user]);

  async function loadChartCount() {
    try {
      const token = localStorage.getItem('astro_access_token');
      if (!token) return;

      const response = await fetch('http://localhost:8000/api/v1/charts/?page=1&page_size=1', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setChartCount(data.total || 0);
      }
    } catch (error) {
      console.error('Error loading chart count:', error);
    } finally {
      setLoadingCharts(false);
    }
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
            aria-label="Voltar ao Dashboard"
          >
            <img
              src="/logo.png"
              alt="Real Astrology"
              className="h-8 w-8"
            />
            <h1 className="text-2xl font-bold text-foreground">Real Astrology</h1>
          </Link>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button variant="ghost" size="sm" asChild>
              <Link to="/profile">
                Perfil
              </Link>
            </Button>
            <span className="text-sm text-muted-foreground">
              {user.full_name}
            </span>
            <Button variant="ghost" size="sm" onClick={logout}>
              Sair
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
          <h2 className="text-3xl font-bold text-foreground mb-2">Dashboard</h2>
          <p className="text-muted-foreground">
            Bem-vindo de volta, {user.full_name}!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Meus Mapas</CardTitle>
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
                    {chartCount === 0 ? 'Nenhum mapa criado ainda' : chartCount === 1 ? '1 mapa salvo' : `${chartCount} mapas salvos`}
                  </p>
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Conta</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="text-sm font-medium">{user.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Status</p>
                {user.email_verified ? (
                  <Badge variant="default">Verificado</Badge>
                ) : (
                  <Badge variant="secondary">Não verificado</Badge>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configurações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div>
                <p className="text-sm text-muted-foreground">Idioma</p>
                <p className="text-sm font-medium">{user.locale}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Fuso Horário</p>
                <p className="text-sm font-medium">{user.timezone || 'Não configurado'}</p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Criar Mapa Natal</CardTitle>
              <CardDescription>
                Calcule seu mapa natal ou de outra pessoa com precisão usando dados
                astronômicos do Swiss Ephemeris.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" asChild>
                <Link to="/charts/new">
                  + Novo Mapa Natal
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Meus Mapas</CardTitle>
              <CardDescription>
                Acesse todos os seus mapas natais salvos, visualize detalhes e faça
                análises astrológicas.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="secondary" className="w-full" asChild>
                <Link to="/charts">
                  Ver Meus Mapas
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Funcionalidades Implementadas</CardTitle>
            <CardDescription>
              Recursos recentemente adicionados à plataforma
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">🌙</span>
              <div className="flex-1">
                <p className="font-medium">Modo Escuro</p>
                <p className="text-sm text-muted-foreground">
                  Dark mode completo para melhor experiência noturna
                </p>
              </div>
              <Badge variant="default">Implementado</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">⚡</span>
              <div className="flex-1">
                <p className="font-medium">Processamento Assíncrono com Celery</p>
                <p className="text-sm text-muted-foreground">
                  Geração de mapas em background sem travar a interface (1-2 minutos)
                </p>
              </div>
              <Badge variant="default">Implementado</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">🤖</span>
              <div className="flex-1">
                <p className="font-medium">Interpretações com IA (GPT-4o-mini)</p>
                <p className="text-sm text-muted-foreground">
                  Análises personalizadas de planetas, casas e aspectos usando OpenAI
                </p>
              </div>
              <Badge variant="default">Implementado</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">📊</span>
              <div className="flex-1">
                <p className="font-medium">Progresso Incremental de Geração</p>
                <p className="text-sm text-muted-foreground">
                  Acompanhe em tempo real cada etapa do cálculo (10%, 20%, 30%... 100%)
                </p>
              </div>
              <Badge variant="default">Implementado</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Em Desenvolvimento</CardTitle>
            <CardDescription>
              Funcionalidades planejadas para as próximas versões
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">🔬</span>
              <div className="flex-1">
                <p className="font-medium">Cálculo de Temperamento Automatizado</p>
                <p className="text-sm text-muted-foreground">
                  Sistema automatizado dos 4 temperamentos baseado em 5 fatores da astrologia tradicional
                </p>
              </div>
              <Badge variant="outline">Em breve</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">📄</span>
              <div className="flex-1">
                <p className="font-medium">Exportação PDF</p>
                <p className="text-sm text-muted-foreground">
                  Gere relatórios completos em PDF com LaTeX para impressão profissional
                </p>
              </div>
              <Badge variant="outline">Em breve</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">🔐</span>
              <div className="flex-1">
                <p className="font-medium">Endpoints LGPD/GDPR</p>
                <p className="text-sm text-muted-foreground">
                  Acesso, exportação, retificação e exclusão de dados pessoais
                </p>
              </div>
              <Badge variant="outline">Planejado</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">💳</span>
              <div className="flex-1">
                <p className="font-medium">Sistema de Pagamento</p>
                <p className="text-sm text-muted-foreground">
                  Planos premium com relatórios avançados e análises detalhadas
                </p>
              </div>
              <Badge variant="outline">Planejado</Badge>
            </div>

            <div className="flex items-start gap-3">
              <span className="text-primary text-xl">📚</span>
              <div className="flex-1">
                <p className="font-medium">Conteúdo Educacional</p>
                <p className="text-sm text-muted-foreground">
                  Explicações sobre astrologia tradicional e precisão dos cálculos
                </p>
              </div>
              <Badge variant="outline">Planejado</Badge>
            </div>

            <div className="mt-6 pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                Veja todas as funcionalidades planejadas no nosso{' '}
                <a
                  href="https://github.com/lmeazzini/astro-natal-chart/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary hover:underline"
                >
                  roadmap público →
                </a>
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default App;
