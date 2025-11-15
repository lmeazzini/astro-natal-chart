/**
 * OAuth callback page - handles redirect from OAuth providers
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { oauthService } from '../services/oauth';
import { useAuth } from '../contexts/AuthContext';

const TOKEN_KEY = 'astro_access_token';
const REFRESH_TOKEN_KEY = 'astro_refresh_token';

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const { setUser } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    handleOAuthCallback();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleOAuthCallback() {
    try {
      // Parse tokens from URL
      const tokens = oauthService.parseCallbackParams();

      if (!tokens || !tokens.access_token || !tokens.refresh_token) {
        setError('Falha na autenticação OAuth. Tokens não encontrados.');
        return;
      }

      // Store tokens
      localStorage.setItem(TOKEN_KEY, tokens.access_token);
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);

      // Fetch user data
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${tokens.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Falha ao buscar dados do usuário');
      }

      const userData = await response.json();
      setUser(userData);

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar autenticação OAuth');
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-destructive mb-2">
              Erro de Autenticação
            </h2>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <button
              onClick={() => navigate('/login')}
              className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md hover:opacity-90 transition"
            >
              Voltar para Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-muted-foreground">Processando autenticação...</p>
      </div>
    </div>
  );
}
