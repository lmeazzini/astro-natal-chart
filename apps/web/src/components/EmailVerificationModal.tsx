/**
 * Email verification modal - shown when users try to access premium features
 * without verifying their email first.
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Mail, ShieldCheck, Sparkles, FileDown, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/services/api';

interface EmailVerificationModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Called when the modal should close */
  onOpenChange: (open: boolean) => void;
  /** The feature that triggered the modal (optional, for better UX) */
  featureName?: string;
}

export function EmailVerificationModal({
  open,
  onOpenChange,
  featureName,
}: EmailVerificationModalProps) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [isResending, setIsResending] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);
  const [resendError, setResendError] = useState('');

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
        setResendError(t('components.emailVerification.genericError', { defaultValue: 'Error resending email. Please try again later.' }));
      }
    } finally {
      setIsResending(false);
    }
  }

  // Get appropriate icon based on feature
  function getFeatureIcon() {
    if (featureName?.toLowerCase().includes('pdf')) {
      return <FileDown className="h-8 w-8 text-primary" />;
    }
    if (featureName?.toLowerCase().includes('interpretation') || featureName?.toLowerCase().includes('ai')) {
      return <Sparkles className="h-8 w-8 text-primary" />;
    }
    return <ShieldCheck className="h-8 w-8 text-primary" />;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="space-y-4">
          <div className="flex justify-center">
            <div className="rounded-full bg-primary/10 p-4">
              {getFeatureIcon()}
            </div>
          </div>
          <DialogTitle className="text-center">
            {t('components.emailVerificationModal.title', { defaultValue: 'Email verification required' })}
          </DialogTitle>
          <DialogDescription className="text-center">
            {featureName ? (
              t('components.emailVerificationModal.messageWithFeature', {
                defaultValue: 'To access {{feature}}, you need to verify your email first.',
                feature: featureName,
              })
            ) : (
              t('components.emailVerificationModal.message', {
                defaultValue: 'This feature requires email verification. Please verify your email to continue.',
              })
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4 py-4">
          {/* User's email */}
          <div className="flex items-center justify-center gap-2 rounded-lg bg-muted p-3">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">{user?.email}</span>
          </div>

          {/* Instructions */}
          <div className="space-y-2 text-sm text-muted-foreground">
            <p>
              {t('components.emailVerificationModal.instructions', {
                defaultValue: 'Check your inbox for the verification email and click the link to verify your account.',
              })}
            </p>
            <p>
              {t('components.emailVerificationModal.checkSpam', {
                defaultValue: "If you don't see it, check your spam folder.",
              })}
            </p>
          </div>

          {/* Success/Error messages */}
          {resendSuccess && (
            <p className="text-sm text-green-600 dark:text-green-400 text-center">
              {t('components.emailVerification.success', { defaultValue: 'Verification email sent! Check your inbox.' })}
            </p>
          )}
          {resendError && (
            <p className="text-sm text-red-600 dark:text-red-400 text-center">
              {resendError}
            </p>
          )}
        </div>

        <DialogFooter className="flex-col gap-2 sm:flex-col">
          <Button
            onClick={handleResendEmail}
            disabled={isResending || resendSuccess}
            className="w-full"
          >
            {isResending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                {t('components.emailVerification.sending', { defaultValue: 'Sending...' })}
              </>
            ) : resendSuccess ? (
              <>
                <Mail className="mr-2 h-4 w-4" />
                {t('components.emailVerification.sent', { defaultValue: 'Email sent!' })}
              </>
            ) : (
              <>
                <Mail className="mr-2 h-4 w-4" />
                {t('components.emailVerificationModal.resendButton', { defaultValue: 'Resend verification email' })}
              </>
            )}
          </Button>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="w-full"
          >
            {t('common.close', { defaultValue: 'Close' })}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
