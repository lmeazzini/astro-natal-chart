/**
 * User login page
 */

import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { oauthService, OAuthProvider } from '../services/oauth';
import { Logo } from '../components/Logo';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';

// Form validation schema
const loginFormSchema = z.object({
  email: z.string().min(1, 'Email é obrigatório').email('Email inválido'),
  password: z.string().min(1, 'Senha é obrigatória'),
});

type LoginFormValues = z.infer<typeof loginFormSchema>;

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);
  const [showPassword, setShowPassword] = useState(false);

  // Form setup with React Hook Form + Zod
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: {
      email: '',
      password: '',
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
      // Silently fail - OAuth is optional
      console.error('Failed to load OAuth providers:', error);
      setOauthProviders([]);
    }
  }

  function handleOAuthLogin(provider: string) {
    oauthService.initiateLogin(provider);
  }

  async function onSubmit(data: LoginFormValues) {
    setGeneralError('');
    setIsLoading(true);

    try {
      await login(data.email, data.password);
      navigate('/dashboard');
    } catch (error) {
      setGeneralError(
        error instanceof Error ? error.message : 'Erro ao fazer login'
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Left Panel - Celestial Branding */}
      <div className="hidden lg:flex flex-col justify-center items-center bg-gradient-to-br from-primary via-primary/90 to-secondary/80 text-primary-foreground p-12 relative overflow-hidden">
        {/* Decorative floating elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-20 w-32 h-32 rounded-full bg-white/10 animate-float" />
          <div className="absolute bottom-32 right-16 w-24 h-24 rounded-full bg-white/5 animate-float" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-10 w-16 h-16 rounded-full bg-white/5 animate-float" style={{ animationDelay: '2s' }} />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-md text-center animate-fade-in">
          <Link to="/" className="inline-block mb-8 hover:opacity-80 transition-opacity" aria-label="Voltar para Página Inicial">
            <Logo size="xl" />
          </Link>
          <h1 className="text-h1 text-white mb-astro-md">
            Bem-vindo de volta
          </h1>
          <p className="text-body text-white/90 mb-astro-xl">
            Entre para acessar seus mapas natais e continuar sua jornada astrológica com precisão e insights profundos.
          </p>
          <div className="inline-flex items-center gap-2 text-white/80 text-sm">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Cálculos astronômicos precisos • Swiss Ephemeris
          </div>
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex items-center justify-center p-8 lg:p-12 bg-background animate-slide-in-up">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <Link to="/" className="inline-block mb-6 hover:opacity-80 transition-opacity" aria-label="Voltar para Página Inicial">
              <Logo size="lg" />
            </Link>
          </div>

          {/* Form Card */}
          <Card className="border-0 shadow-lg">
          <CardHeader className="space-y-2">
            <CardTitle className="text-h2 text-center">Fazer Login</CardTitle>
            <CardDescription className="text-center text-base">
              Acesse sua conta e continue explorando
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

                {/* Password Field */}
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Senha</FormLabel>
                      <FormControl>
                        <div className="relative">
                          <Input
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            autoComplete="current-password"
                            className="pr-10"
                            {...field}
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                            onClick={() => setShowPassword(!showPassword)}
                            aria-label={showPassword ? "Ocultar senha" : "Mostrar senha"}
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4 text-muted-foreground" />
                            ) : (
                              <Eye className="h-4 w-4 text-muted-foreground" />
                            )}
                          </Button>
                        </div>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Forgot Password Link */}
                <div className="flex justify-end">
                  <Link
                    to="/forgot-password"
                    className="text-sm text-primary hover:underline"
                  >
                    Esqueceu a senha?
                  </Link>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? 'Entrando...' : 'Entrar'}
                </Button>
              </form>
            </Form>

            {/* OAuth Login Options */}
            {oauthProviders?.length > 0 && (
              <>
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <Separator />
                  </div>
                  <div className="relative flex justify-center text-sm font-medium">
                    <span className="bg-card px-4 text-muted-foreground">
                      ou continue com
                    </span>
                  </div>
                </div>

                <div className="grid gap-3">
                  {oauthProviders?.map((provider) => (
                    <Button
                      key={provider.name}
                      variant="outline"
                      size="lg"
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

          {/* Register Link */}
          <CardFooter className="flex-col space-y-4">
            <p className="w-full text-center text-sm text-muted-foreground">
              Não tem uma conta?{' '}
              <Link
                to="/register"
                className="text-primary hover:underline font-semibold"
              >
                Criar conta gratuita
              </Link>
            </p>
          </CardFooter>
        </Card>

        {/* Additional Info */}
        <p className="mt-8 text-center text-xs text-muted-foreground">
          Ao entrar, você concorda com nossos{' '}
          <Link to="/terms" className="text-primary hover:underline">
            Termos de Uso
          </Link>
          {' '}e{' '}
          <Link to="/privacy" className="text-primary hover:underline">
            Política de Privacidade
          </Link>
        </p>
      </div>
      </div>
    </div>
  );
}
