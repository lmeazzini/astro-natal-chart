/**
 * Reset Password page - Confirm password reset with token
 */

import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useTranslation } from 'react-i18next';
import { passwordResetService } from '../services/passwordReset';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, CheckCircle2, ArrowLeft, Loader2 } from 'lucide-react';

type ResetPasswordValues = {
  password: string;
  confirmPassword: string;
};

export function ResetPasswordPage() {
  const { t } = useTranslation();

  // Zod schema inside component to access t()
  const resetPasswordSchema = z
    .object({
      password: z
        .string()
        .min(8, t('auth.register.passwordMinLength'))
        .regex(/[A-Z]/, t('validation.passwordUppercase', { defaultValue: 'Senha deve conter pelo menos uma letra maiúscula' }))
        .regex(/[a-z]/, t('validation.passwordLowercase', { defaultValue: 'Senha deve conter pelo menos uma letra minúscula' }))
        .regex(/[0-9]/, t('validation.passwordNumber', { defaultValue: 'Senha deve conter pelo menos um número' })),
      confirmPassword: z.string().min(1, t('validation.required')),
    })
    .refine((data) => data.password === data.confirmPassword, {
      message: t('validation.passwordMismatch'),
      path: ['confirmPassword'],
    });
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [successMessage, setSuccessMessage] = useState('');
  const [generalError, setGeneralError] = useState('');

  const form = useForm<ResetPasswordValues>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      password: '',
      confirmPassword: '',
    },
  });

  useEffect(() => {
    // Check if token exists
    if (!token) {
      setGeneralError(t('auth.resetPassword.invalidToken'));
    }
  }, [token, t]);

  async function onSubmit(values: ResetPasswordValues) {
    setGeneralError('');
    setSuccessMessage('');

    if (!token) {
      setGeneralError(t('auth.resetPassword.tokenNotFound', { defaultValue: 'Token de recuperação não encontrado' }));
      return;
    }

    try {
      const response = await passwordResetService.confirmReset(
        token,
        values.password
      );

      if (response.success) {
        setSuccessMessage(response.message);
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login');
        }, 3000);
      } else {
        setGeneralError(response.message);
      }
    } catch (error) {
      setGeneralError(
        error instanceof Error
          ? error.message
          : t('auth.resetPassword.error')
      );
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            {t('auth.resetPassword.title')}
          </h1>
          <p className="text-muted-foreground">
            {t('auth.resetPassword.subtitle')}
          </p>
        </div>

        {/* Form Card */}
        <Card>
          <CardHeader>
            <CardTitle>{t('auth.resetPassword.newPassword')}</CardTitle>
            <CardDescription>
              {t('auth.resetPassword.chooseStrong', { defaultValue: 'Escolha uma senha forte e segura' })}
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
                    {t('auth.resetPassword.redirecting', { defaultValue: 'Redirecionando para login em 3 segundos...' })}
                  </p>
                </AlertDescription>
              </Alert>
            )}

            {!successMessage && token && (
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                  <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('auth.resetPassword.newPassword')}</FormLabel>
                        <FormControl>
                          <Input
                            type="password"
                            placeholder="••••••••"
                            autoComplete="new-password"
                            autoFocus
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          {t('auth.resetPassword.passwordRequirements', { defaultValue: 'Mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números' })}
                        </FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="confirmPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t('auth.resetPassword.confirmPassword')}</FormLabel>
                        <FormControl>
                          <Input
                            type="password"
                            placeholder="••••••••"
                            autoComplete="new-password"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={form.formState.isSubmitting}
                  >
                    {form.formState.isSubmitting && (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    )}
                    {form.formState.isSubmitting ? t('common.loading') : t('auth.resetPassword.submit')}
                  </Button>
                </form>
              </Form>
            )}

            {/* Back to Login Link */}
            <div className="mt-6 text-center">
              <Button variant="link" asChild>
                <Link to="/login">
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  {t('auth.resetPassword.backToLogin', { defaultValue: 'Voltar para login' })}
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
