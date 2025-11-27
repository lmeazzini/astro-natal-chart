/**
 * Forgot Password page - Request password reset
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { passwordResetService } from '../services/passwordReset';
import { amplitudeService } from '../services/amplitude';
import { useAmplitudePageView } from '../hooks/useAmplitudePageView';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2, ArrowLeft, Loader2 } from 'lucide-react';

type ForgotPasswordValues = {
  email: string;
};

export function ForgotPasswordPage() {
  const { t } = useTranslation();

  // Track page view
  useAmplitudePageView('Forgot Password Page');

  // Zod schema inside component to access t()
  const forgotPasswordSchema = z.object({
    email: z.string().min(1, t('validation.required')).email(t('validation.email')),
  });
  const [successMessage, setSuccessMessage] = useState('');
  const [generalError, setGeneralError] = useState('');

  const form = useForm<ForgotPasswordValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: '',
    },
  });

  async function onSubmit(values: ForgotPasswordValues) {
    setGeneralError('');
    setSuccessMessage('');

    // Track password reset request
    amplitudeService.track('password_reset_requested', {
      source: 'forgot_password_page',
    });

    try {
      const response = await passwordResetService.requestReset(values.email);

      if (response.success) {
        // Track success (email sent)
        amplitudeService.track('password_reset_email_sent', {
          source: 'forgot_password_page',
        });

        setSuccessMessage(response.message);
        form.reset();
      } else {
        // Track failure
        amplitudeService.track('password_reset_failed', {
          error_type: 'request_failed',
          source: 'forgot_password_page',
        });

        setGeneralError(response.message);
      }
    } catch (error) {
      // Track error
      amplitudeService.track('password_reset_failed', {
        error_type: error instanceof Error ? error.name : 'unknown_error',
        source: 'forgot_password_page',
      });

      setGeneralError(error instanceof Error ? error.message : t('auth.forgotPassword.error'));
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            {t('auth.forgotPassword.title')}
          </h1>
          <p className="text-muted-foreground">{t('auth.forgotPassword.subtitle')}</p>
        </div>

        {/* Form Card */}
        <Card>
          <CardHeader>
            <CardTitle>{t('auth.forgotPassword.title')}</CardTitle>
            <CardDescription>
              {t('auth.forgotPassword.description', {
                defaultValue: 'Enviaremos um link de recuperação para seu email',
              })}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {generalError && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{generalError}</AlertDescription>
              </Alert>
            )}

            {successMessage && (
              <Alert className="mb-6 border-green-500/20 bg-green-500/10">
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertDescription className="text-green-700 dark:text-green-400">
                  {successMessage}
                  <p className="mt-2 text-xs text-muted-foreground">
                    {t('auth.forgotPassword.checkInbox', {
                      defaultValue: 'Verifique sua caixa de entrada e spam.',
                    })}
                  </p>
                </AlertDescription>
              </Alert>
            )}

            {!successMessage && (
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('auth.forgotPassword.email')}</FormLabel>
                        <FormControl>
                          <Input
                            type="email"
                            placeholder={t('auth.forgotPassword.email')}
                            autoComplete="email"
                            autoFocus
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
                    {form.formState.isSubmitting && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    {form.formState.isSubmitting
                      ? t('common.loading')
                      : t('auth.forgotPassword.submit')}
                  </Button>
                </form>
              </Form>
            )}

            {/* Back to Login Link */}
            <div className="mt-6 text-center">
              <Button variant="link" asChild>
                <Link to="/login">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t('auth.forgotPassword.backToLogin')}
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
