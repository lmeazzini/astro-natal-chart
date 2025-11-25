/**
 * OAuth callback page - handles redirect from OAuth providers
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { oauthService } from '../services/oauth';
import { setToken, setRefreshToken } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle, Loader2 } from 'lucide-react';

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
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
        setError(
          t('pages.oauthCallback.tokensNotFound', {
            defaultValue: 'Falha na autenticação OAuth. Tokens não encontrados.',
          })
        );
        return;
      }

      // Store tokens
      setToken(tokens.access_token);
      setRefreshToken(tokens.refresh_token);

      // Fetch user data
      const response = await fetch('http://localhost:8000/api/v1/auth/me', {
        headers: {
          Authorization: `Bearer ${tokens.access_token}`,
        },
      });

      if (!response.ok) {
        throw new Error(
          t('pages.oauthCallback.userFetchFailed', {
            defaultValue: 'Falha ao buscar dados do usuário',
          })
        );
      }

      const userData = await response.json();
      setUser(userData);

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : t('pages.oauthCallback.genericError', {
              defaultValue: 'Erro ao processar autenticação OAuth',
            })
      );
    }
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>
              {t('pages.oauthCallback.errorTitle', { defaultValue: 'Erro de Autenticação' })}
            </AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button onClick={() => navigate('/login')} className="w-full mt-4">
            {t('pages.oauthCallback.backToLogin', { defaultValue: 'Voltar para Login' })}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
        <p className="text-muted-foreground">
          {t('pages.oauthCallback.processing', { defaultValue: 'Processando autenticação...' })}
        </p>
      </div>
    </div>
  );
}
