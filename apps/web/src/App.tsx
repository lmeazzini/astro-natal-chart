import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

// Placeholder components (will be implemented later)
function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">Astro</h1>
        <p className="text-xl text-gray-700 mb-8">
          Sistema de Mapas Natais com Astrologia Tradicional
        </p>
        <div className="space-x-4">
          <a
            href="/login"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Entrar
          </a>
          <a
            href="/register"
            className="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition"
          >
            Criar Conta
          </a>
        </div>
        <div className="mt-12 text-sm text-gray-600">
          <p>✨ Cálculos precisos com Swiss Ephemeris</p>
          <p>📊 Visualização gráfica profissional</p>
          <p>📄 Exportação em PDF com LaTeX</p>
          <p>🔒 Segurança e privacidade (LGPD)</p>
        </div>
      </div>
    </div>
  );
}

function LoginPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-3xl font-bold text-center mb-6">Login</h2>
        <p className="text-center text-gray-600">Em desenvolvimento...</p>
      </div>
    </div>
  );
}

function RegisterPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-3xl font-bold text-center mb-6">Criar Conta</h2>
        <p className="text-center text-gray-600">Em desenvolvimento...</p>
      </div>
    </div>
  );
}

function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4">
        <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
        <p className="text-gray-600">Em desenvolvimento...</p>
      </div>
    </div>
  );
}

export default App;
