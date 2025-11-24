/**
 * Email verification banner - shown to users with unverified emails.
 * Reminds users to verify their email for premium features like AI interpretations.
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AlertCircle, Mail, X, Sparkles } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/services/api';

interface EmailVerificationBannerProps {
  /** Called when banner is dismissed */
  onDismiss?: () => void;
  /** Whether to show the premium features hint */
  showPremiumHint?: boolean;
}

export function EmailVerificationBanner({ onDismiss, showPremiumHint = true }: EmailVerificationBannerProps) {
  const { t } = useTranslation();
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

      await apiClient.post('/api/v1/auth/resend-verification');

      setResendSuccess(true);

      // Hide success message after 5 seconds
      setTimeout(() => {
        setResendSuccess(false);
      }, 5000);
    } catch (error) {
      if (error instanceof Error) {
        setResendError(error.message);
      } else {
        setResendError(t('components.emailVerification.genericError', { defaultValue: 'Erro ao reenviar email. Tente novamente mais tarde.' }));
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
              {t('components.emailVerification.title', { defaultValue: 'Email não verificado' })}
            </span>
          </div>
          <p className="text-sm text-yellow-800 dark:text-yellow-200 mt-1">
            {t('components.emailVerification.message', { defaultValue: 'Verifique seu email para ter acesso completo à plataforma.' })}{' '}
            {t('components.emailVerification.didntReceive', { defaultValue: 'Não recebeu o email?' })}{' '}
            <button
              onClick={handleResendEmail}
              disabled={isResending || resendSuccess}
              className="font-medium underline hover:no-underline disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isResending ? t('components.emailVerification.sending', { defaultValue: 'Enviando...' }) : resendSuccess ? t('components.emailVerification.sent', { defaultValue: 'Email enviado!' }) : t('components.emailVerification.resend', { defaultValue: 'Reenviar' })}
            </button>
          </p>
          {showPremiumHint && (
            <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-2 flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              {t('components.emailVerificationBanner.premiumHint', { defaultValue: 'Desbloqueie interpretações com IA e exportação em PDF' })}
            </p>
          )}
          {resendError && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-1">
              {resendError}
            </p>
          )}
          {resendSuccess && (
            <p className="text-sm text-green-600 dark:text-green-400 mt-1">
              {t('components.emailVerification.success', { defaultValue: 'Email de verificação enviado! Verifique sua caixa de entrada.' })}
            </p>
          )}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDismiss}
          className="h-8 w-8 p-0 text-yellow-800 dark:text-yellow-200 hover:bg-yellow-100 dark:hover:bg-yellow-900"
          aria-label={t('components.emailVerification.dismiss', { defaultValue: 'Dispensar' })}
        >
          <X className="h-4 w-4" />
        </Button>
      </AlertDescription>
    </Alert>
  );
}
