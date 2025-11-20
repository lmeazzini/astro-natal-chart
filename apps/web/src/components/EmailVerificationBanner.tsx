/**
 * Email verification banner - shown to users with unverified emails
 */

import { useState } from 'react';
import { AlertCircle, Mail, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface EmailVerificationBannerProps {
  /** Called when banner is dismissed */
  onDismiss?: () => void;
}

export function EmailVerificationBanner({ onDismiss }: EmailVerificationBannerProps) {
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [resendError, setResendError] = useState('');
  const [isDismissed, setIsDismissed] = useState(false);

  if (isDismissed) {
    return null;
  }

  async function handleResendEmail() {
    try {
      setIsResending(true);
      setResendError('');

      const token = localStorage.getItem('astro_access_token');
      if (!token) {
        throw new Error('Você precisa estar autenticado');
      }

      const response = await fetch(`${API_URL}/api/v1/auth/resend-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Falha ao reenviar email');
      }

      setResendSuccess(true);

      // Hide success message after 5 seconds
      setTimeout(() => {
        setResendSuccess(false);
      }, 5000);
    } catch (error) {
      if (error instanceof Error) {
        setResendError(error.message);
      } else {
        setResendError('Erro ao reenviar email. Tente novamente mais tarde.');
      }
    } finally {
      setIsResending(false);
    }
  }

  function handleDismiss() {
    setIsDismissed(true);
    onDismiss?.();
  }

  return (
    <Alert className="relative border-yellow-600 bg-yellow-50 dark:bg-yellow-950 dark:border-yellow-800">
      <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-500" />
      <AlertDescription className="flex items-center justify-between gap-4 ml-2">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-yellow-600 dark:text-yellow-500" />
            <span className="font-medium text-yellow-900 dark:text-yellow-100">
              Email não verificado
            </span>
          </div>
          <p className="text-sm text-yellow-800 dark:text-yellow-200 mt-1">
            Verifique seu email para ter acesso completo à plataforma.
            Não recebeu o email?{' '}
            <button
              onClick={handleResendEmail}
              disabled={isResending || resendSuccess}
              className="font-medium underline hover:no-underline disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isResending ? 'Enviando...' : resendSuccess ? 'Email enviado!' : 'Reenviar'}
            </button>
          </p>
          {resendError && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-1">
              {resendError}
            </p>
          )}
          {resendSuccess && (
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              Email de verificação enviado! Verifique sua caixa de entrada.
            </p>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDismiss}
          className="h-8 w-8 p-0 text-yellow-800 dark:text-yellow-200 hover:bg-yellow-100 dark:hover:bg-yellow-900"
          aria-label="Dispensar"
        >
          <X className="h-4 w-4" />
        </Button>
      </AlertDescription>
    </Alert>
  );
}
