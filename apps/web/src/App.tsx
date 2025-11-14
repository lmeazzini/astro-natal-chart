import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { LoginPage } from './pages/Login';
import { RegisterPage } from './pages/Register';
import { ChartsPage } from './pages/Charts';
import { NewChartPage } from './pages/NewChart';
import { ChartDetailPage } from './pages/ChartDetail';
import { OAuthCallbackPage } from './pages/OAuthCallback';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/charts" element={<ChartsPage />} />
          <Route path="/charts/new" element={<NewChartPage />} />
          <Route path="/charts/:id" element={<ChartDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-background to-secondary/10 flex items-center justify-center px-4">
      <div className="text-center max-w-4xl">
        <h1 className="text-6xl font-bold text-foreground mb-4">Astro</h1>
        <p className="text-xl text-muted-foreground mb-8">
          Sistema de Mapas Natais com Astrologia Tradicional
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/login"
            className="inline-block bg-primary text-primary-foreground px-8 py-3 rounded-lg hover:opacity-90 transition font-medium"
          >
            Entrar
          </Link>
          <Link
            to="/register"
            className="inline-block bg-background text-foreground px-8 py-3 rounded-lg border-2 border-border hover:bg-secondary transition font-medium"
          >
            Criar Conta
          </Link>
        </div>
        <div className="mt-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 text-sm text-muted-foreground">
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="text-2xl mb-2">✨</div>
            <p className="font-medium text-foreground">Cálculos Precisos</p>
            <p className="text-xs mt-1">Swiss Ephemeris JPL DE431</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="text-2xl mb-2">📊</div>
            <p className="font-medium text-foreground">Visualização Gráfica</p>
            <p className="text-xs mt-1">Mapas natais profissionais</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="text-2xl mb-2">📄</div>
            <p className="font-medium text-foreground">Exportação PDF</p>
            <p className="text-xs mt-1">Templates LaTeX personalizados</p>
          </div>
          <div className="p-4 bg-card border border-border rounded-lg">
            <div className="text-2xl mb-2">🔒</div>
            <p className="font-medium text-foreground">Segurança</p>
            <p className="text-xs mt-1">Conforme LGPD/GDPR</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function DashboardPage() {
  const { user, logout, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">Carregando...</p>
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
          <h1 className="text-2xl font-bold text-foreground">Astro</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user.full_name}
            </span>
            <button
              onClick={logout}
              className="text-sm text-primary hover:underline"
            >
              Sair
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">Dashboard</h2>
          <p className="text-muted-foreground">
            Bem-vindo de volta, {user.full_name}!
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 bg-card border border-border rounded-lg">
            <h3 className="font-semibold text-foreground mb-2">Meus Mapas</h3>
            <p className="text-3xl font-bold text-primary">0</p>
            <p className="text-sm text-muted-foreground mt-2">
              Nenhum mapa criado ainda
            </p>
          </div>

          <div className="p-6 bg-card border border-border rounded-lg">
            <h3 className="font-semibold text-foreground mb-2">Conta</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Email: {user.email}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Status: {user.email_verified ? 'Verificado' : 'Não verificado'}
            </p>
          </div>

          <div className="p-6 bg-card border border-border rounded-lg">
            <h3 className="font-semibold text-foreground mb-2">Configurações</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Idioma: {user.locale}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              Fuso: {user.timezone || 'Não configurado'}
            </p>
          </div>
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 bg-card border border-border rounded-lg">
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Criar Mapa Natal
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Calcule seu mapa natal ou de outra pessoa com precisão usando dados
              astronômicos do Swiss Ephemeris.
            </p>
            <Link
              to="/charts/new"
              className="inline-block w-full text-center py-3 px-4 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition font-medium"
            >
              + Novo Mapa Natal
            </Link>
          </div>

          <div className="p-6 bg-card border border-border rounded-lg">
            <h3 className="text-xl font-semibold text-foreground mb-4">
              Meus Mapas
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Acesse todos os seus mapas natais salvos, visualize detalhes e faça
              análises astrológicas.
            </p>
            <Link
              to="/charts"
              className="inline-block w-full text-center py-3 px-4 bg-secondary text-secondary-foreground rounded-md hover:opacity-90 transition font-medium"
            >
              Ver Meus Mapas
            </Link>
          </div>
        </div>

        <div className="mt-8 p-6 bg-card border border-border rounded-lg">
          <h3 className="text-xl font-semibold text-foreground mb-4">
            Próximas Funcionalidades
          </h3>
          <ul className="space-y-3">
            <li className="flex items-start gap-3">
              <span className="text-primary">→</span>
              <span className="text-muted-foreground">
                Análise textual de dignidades essenciais
              </span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-primary">→</span>
              <span className="text-muted-foreground">
                Exportação de mapas em PDF com LaTeX
              </span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-primary">→</span>
              <span className="text-muted-foreground">
                Trânsitos e progressões planetárias
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;
