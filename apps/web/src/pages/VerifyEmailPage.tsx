/**
 * Email verification page
 */

import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Logo } from '../components/Logo';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type VerificationState = 'loading' | 'success' | 'error';

export function VerifyEmailPage() {
  const { t } = useTranslation();
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();

  const [state, setState] = useState<VerificationState>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const [userName, setUserName] = useState('');

  const verifyEmail = useCallback(
    async (verificationToken: string) => {
      try {
        setState('loading');

        const response = await fetch(`${API_URL}/api/v1/auth/verify-email/${verificationToken}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || t('auth.verifyEmail.error'));
        }

        const user = await response.json();
        setUserName(user.full_name || '');
        setState('success');

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } catch (error) {
        setState('error');
        if (error instanceof Error) {
          setErrorMessage(error.message);
        } else {
          setErrorMessage(t('auth.verifyEmail.error'));
        }
      }
    },
    [navigate, t]
  );

  useEffect(() => {
    if (!token) {
      setState('error');
      setErrorMessage(t('auth.verifyEmail.invalidToken'));
      return;
    }

    verifyEmail(token);
  }, [token, verifyEmail, t]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-4">
          <div className="flex justify-center">
            <Logo className="h-16 w-16" />
          </div>
          <div>
            <CardTitle className="text-2xl text-center">{t('auth.verifyEmail.title')}</CardTitle>
            <CardDescription className="text-center mt-2">
              {state === 'loading' && t('auth.verifyEmail.verifying')}
              {state === 'success' && t('auth.verifyEmail.success')}
              {state === 'error' &&
                t('auth.verifyEmail.failed', { defaultValue: 'Falha na verificação' })}
            </CardDescription>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {state === 'loading' && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <Loader2 className="h-12 w-12 animate-spin text-indigo-600" />
              <p className="text-sm text-muted-foreground">
                {t('auth.verifyEmail.wait', { defaultValue: 'Aguarde um momento...' })}
              </p>
            </div>
          )}

          {state === 'success' && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <CheckCircle2 className="h-16 w-16 text-green-600" />
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold">
                  {t('auth.verifyEmail.allSet', { defaultValue: 'Tudo pronto' })}
                  {userName && `, ${userName}`}!
                </h3>
                <p className="text-sm text-muted-foreground">
                  {t('auth.verifyEmail.successMessage', {
                    defaultValue:
                      'Seu email foi verificado com sucesso. Agora você pode acessar todos os recursos da plataforma.',
                  })}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t('auth.verifyEmail.redirecting', {
                    defaultValue: 'Você será redirecionado para a página de login em instantes...',
                  })}
                </p>
              </div>
            </div>
          )}

          {state === 'error' && (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <XCircle className="h-16 w-16 text-red-600" />
              <div className="text-center space-y-2">
                <h3 className="text-lg font-semibold">
                  {t('auth.verifyEmail.failed', { defaultValue: 'Verificação Falhou' })}
                </h3>
                <Alert variant="destructive" className="text-left">
                  <AlertDescription>{errorMessage}</AlertDescription>
                </Alert>
                <p className="text-sm text-muted-foreground mt-4">
                  {t('auth.verifyEmail.possibleCauses', { defaultValue: 'Possíveis causas:' })}
                </p>
                <ul className="text-sm text-muted-foreground text-left list-disc list-inside space-y-1">
                  <li>
                    {t('auth.verifyEmail.causeExpired', {
                      defaultValue: 'O link de verificação expirou (válido por 24 horas)',
                    })}
                  </li>
                  <li>
                    {t('auth.verifyEmail.causeUsed', {
                      defaultValue: 'O link já foi usado anteriormente',
                    })}
                  </li>
                  <li>
                    {t('auth.verifyEmail.causeInvalid', {
                      defaultValue: 'O link está incorreto ou corrompido',
                    })}
                  </li>
                </ul>
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex flex-col space-y-2">
          {state === 'success' && (
            <Button onClick={() => navigate('/login')} className="w-full">
              {t('auth.verifyEmail.goToDashboard')}
            </Button>
          )}

          {state === 'error' && (
            <div className="w-full space-y-2">
              <Button onClick={() => navigate('/login')} className="w-full">
                {t('auth.verifyEmail.backToLogin', { defaultValue: 'Voltar para Login' })}
              </Button>
              <p className="text-sm text-center text-muted-foreground">
                {t('auth.verifyEmail.needNewLink', { defaultValue: 'Precisa de um novo link?' })}{' '}
                <Link to="/login" className="text-indigo-600 hover:underline">
                  {t('auth.verifyEmail.loginAndResend', { defaultValue: 'Faça login' })}
                </Link>{' '}
                {t('auth.verifyEmail.andRequestResend', { defaultValue: 'e solicite o reenvio' })}
              </p>
            </div>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
