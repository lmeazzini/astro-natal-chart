/**
 * User registration page
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useAuth } from '../contexts/AuthContext';
import { oauthService, OAuthProvider } from '../services/oauth';
import { Logo } from '../components/Logo';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Separator } from '@/components/ui/separator';

// Complex password validation schema
const registerFormSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório').email('Email inválido'),
  fullName: z.string().min(3, 'Nome deve ter pelo menos 3 caracteres'),
  password: z.string()
    .min(8, 'Senha deve ter pelo menos 8 caracteres')
    .regex(/[A-Z]/, 'Senha deve conter pelo menos uma letra maiúscula')
    .regex(/[a-z]/, 'Senha deve conter pelo menos uma letra minúscula')
    .regex(/[0-9]/, 'Senha deve conter pelo menos um número')
    .regex(/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/, 'Senha deve conter pelo menos um caractere especial'),
  passwordConfirm: z.string().min(1, 'Confirmação de senha é obrigatória'),
  acceptedTerms: z.boolean().refine((val) => val === true, {
    message: 'Você deve aceitar os Termos de Uso e a Política de Privacidade',
  }),
}).refine((data) => data.password === data.passwordConfirm, {
  message: 'As senhas não coincidem',
  path: ['passwordConfirm'],
});

type RegisterFormValues = z.infer<typeof registerFormSchema>;

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);

  // Form setup with React Hook Form + Zod
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerFormSchema),
    defaultValues: {
      email: '',
      fullName: '',
      password: '',
      passwordConfirm: '',
      acceptedTerms: false,
    },
  });

  useEffect(() => {
    loadOAuthProviders();
  }, []);

  async function loadOAuthProviders() {
    try {
      const providers = await oauthService.getProviders();
      setOauthProviders(providers || []);
    } catch (error) {
      console.error('Failed to load OAuth providers:', error);
      setOauthProviders([]);
    }
  }

  function handleOAuthLogin(provider: string) {
    oauthService.initiateLogin(provider);
  }

  async function onSubmit(data: RegisterFormValues) {
    setGeneralError('');
    setIsLoading(true);

    try {
      await register(
        data.email,
        data.fullName,
        data.password,
        data.passwordConfirm,
        data.acceptedTerms
      );
      navigate('/dashboard');
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : 'Erro ao criar conta'
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10 px-4 py-8">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-block mb-6 hover:opacity-80 transition-opacity" aria-label="Voltar para Página Inicial">
            <Logo size="lg" />
          </Link>
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Criar Conta
          </h1>
          <p className="text-muted-foreground">
            Comece sua jornada astrológica
          </p>
        </div>

        {/* Form Card */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Cadastro</CardTitle>
            <CardDescription className="text-center">
              Preencha os dados para criar sua conta
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {generalError && (
              <Alert variant="destructive">
                <AlertDescription>{generalError}</AlertDescription>
              </Alert>
            )}

            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                {/* Email Field */}
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Email</FormLabel>
                      <FormControl>
                        <Input
                          type="email"
                          placeholder="seu@email.com"
                          autoComplete="email"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Full Name Field */}
                <FormField
                  control={form.control}
                  name="fullName"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome Completo</FormLabel>
                      <FormControl>
                        <Input
                          type="text"
                          placeholder="Seu Nome Completo"
                          autoComplete="name"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Password Field */}
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Senha</FormLabel>
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

                {/* Password Confirm Field */}
                <FormField
                  control={form.control}
                  name="passwordConfirm"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Confirmar Senha</FormLabel>
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

                {/* Terms Acceptance */}
                <FormField
                  control={form.control}
                  name="acceptedTerms"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel className="text-sm font-normal">
                          Li e concordo com os{' '}
                          <Link
                            to="/terms"
                            target="_blank"
                            className="text-primary hover:underline font-medium"
                          >
                            Termos de Uso
                          </Link>
                          {' '}e a{' '}
                          <Link
                            to="/privacy"
                            target="_blank"
                            className="text-primary hover:underline font-medium"
                          >
                            Política de Privacidade
                          </Link>
                        </FormLabel>
                        <FormMessage />
                      </div>
                    </FormItem>
                  )}
                />

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? 'Criando conta...' : 'Criar Conta'}
                </Button>
              </form>
            </Form>

            {/* OAuth Login Options */}
            {oauthProviders?.length > 0 && (
              <>
                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <Separator />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">
                      ou cadastre-se com
                    </span>
                  </div>
                </div>

                <div className="space-y-2">
                  {oauthProviders?.map((provider) => (
                    <Button
                      key={provider.name}
                      variant="outline"
                      className="w-full"
                      onClick={() => handleOAuthLogin(provider.name)}
                    >
                      {provider.name === 'google' && (
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                          <path
                            fill="currentColor"
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                          />
                          <path
                            fill="currentColor"
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                          />
                          <path
                            fill="currentColor"
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                          />
                          <path
                            fill="currentColor"
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                          />
                        </svg>
                      )}
                      {provider.name === 'github' && (
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                        </svg>
                      )}
                      {provider.name === 'facebook' && (
                        <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                        </svg>
                      )}
                      Continuar com {provider.display_name}
                    </Button>
                  ))}
                </div>
              </>
            )}
          </CardContent>

          {/* Login Link */}
          <CardFooter>
            <p className="w-full text-center text-sm text-muted-foreground">
              Já tem uma conta?{' '}
              <Link
                to="/login"
                className="text-primary hover:underline font-medium"
              >
                Fazer login
              </Link>
            </p>
          </CardFooter>
        </Card>

        {/* Password Requirements */}
        <Alert className="mt-6">
          <AlertDescription>
            <p className="font-medium mb-2">A senha deve conter:</p>
            <ul className="text-xs space-y-1 list-disc list-inside">
              <li>Pelo menos 8 caracteres</li>
              <li>Uma letra maiúscula</li>
              <li>Uma letra minúscula</li>
              <li>Um número</li>
              <li>Um caractere especial (!@#$%^&*...)</li>
            </ul>
          </AlertDescription>
        </Alert>
      </div>
    </div>
  );
}