/**
 * User registration page
 */

import { useState, FormEvent, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { oauthService, OAuthProvider } from '../services/oauth';

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [formData, setFormData] = useState({
    email: '',
    fullName: '',
    password: '',
    passwordConfirm: '',
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [generalError, setGeneralError] = useState('');
  const [oauthProviders, setOauthProviders] = useState<OAuthProvider[]>([]);

  useEffect(() => {
    loadOAuthProviders();
  }, []);

  async function loadOAuthProviders() {
    try {
      const providers = await oauthService.getProviders();
      setOauthProviders(providers);
    } catch (error) {
      console.error('Failed to load OAuth providers:', error);
    }
  }

  function handleOAuthLogin(provider: string) {
    oauthService.initiateLogin(provider);
  }

  function validateForm(): boolean {
    const newErrors: Record<string, string> = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    // Full name validation
    if (!formData.fullName) {
      newErrors.fullName = 'Nome completo é obrigatório';
    } else if (formData.fullName.length < 3) {
      newErrors.fullName = 'Nome deve ter pelo menos 3 caracteres';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Senha deve ter pelo menos 8 caracteres';
    } else {
      if (!/[A-Z]/.test(formData.password)) {
        newErrors.password = 'Senha deve conter pelo menos uma letra maiúscula';
      } else if (!/[a-z]/.test(formData.password)) {
        newErrors.password = 'Senha deve conter pelo menos uma letra minúscula';
      } else if (!/[0-9]/.test(formData.password)) {
        newErrors.password = 'Senha deve conter pelo menos um número';
      } else if (!/[!@#$%^&*()_+\-=[\]{}|;:,.<>?]/.test(formData.password)) {
        newErrors.password = 'Senha deve conter pelo menos um caractere especial';
      }
    }

    // Password confirmation validation
    if (!formData.passwordConfirm) {
      newErrors.passwordConfirm = 'Confirmação de senha é obrigatória';
    } else if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = 'As senhas não coincidem';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await register(
        formData.email,
        formData.fullName,
        formData.password,
        formData.passwordConfirm
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/10 via-background to-secondary/10 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Criar Conta
          </h1>
          <p className="text-muted-foreground">
            Comece sua jornada astrológica
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-card border border-border rounded-lg shadow-lg p-8">
          {generalError && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-md">
              <p className="text-sm text-destructive">{generalError}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-foreground mb-2"
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className={`w-full px-4 py-2 bg-background border ${
                  errors.email ? 'border-destructive' : 'border-input'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                placeholder="seu@email.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-destructive">{errors.email}</p>
              )}
            </div>

            {/* Full Name Field */}
            <div>
              <label
                htmlFor="fullName"
                className="block text-sm font-medium text-foreground mb-2"
              >
                Nome Completo
              </label>
              <input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) =>
                  setFormData({ ...formData, fullName: e.target.value })
                }
                className={`w-full px-4 py-2 bg-background border ${
                  errors.fullName ? 'border-destructive' : 'border-input'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                placeholder="Seu Nome Completo"
              />
              {errors.fullName && (
                <p className="mt-1 text-sm text-destructive">
                  {errors.fullName}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-foreground mb-2"
              >
                Senha
              </label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className={`w-full px-4 py-2 bg-background border ${
                  errors.password ? 'border-destructive' : 'border-input'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-destructive">
                  {errors.password}
                </p>
              )}
            </div>

            {/* Password Confirm Field */}
            <div>
              <label
                htmlFor="passwordConfirm"
                className="block text-sm font-medium text-foreground mb-2"
              >
                Confirmar Senha
              </label>
              <input
                id="passwordConfirm"
                type="password"
                value={formData.passwordConfirm}
                onChange={(e) =>
                  setFormData({ ...formData, passwordConfirm: e.target.value })
                }
                className={`w-full px-4 py-2 bg-background border ${
                  errors.passwordConfirm
                    ? 'border-destructive'
                    : 'border-input'
                } rounded-md focus:outline-none focus:ring-2 focus:ring-primary`}
                placeholder="••••••••"
              />
              {errors.passwordConfirm && (
                <p className="mt-1 text-sm text-destructive">
                  {errors.passwordConfirm}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 bg-primary text-primary-foreground font-medium rounded-md hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              {isLoading ? 'Criando conta...' : 'Criar Conta'}
            </button>
          </form>

          {/* OAuth Login Options */}
          {oauthProviders.length > 0 && (
            <>
              <div className="my-6 flex items-center">
                <div className="flex-1 border-t border-border"></div>
                <span className="px-4 text-sm text-muted-foreground">ou cadastre-se com</span>
                <div className="flex-1 border-t border-border"></div>
              </div>

              <div className="space-y-3">
                {oauthProviders.map((provider) => (
                  <button
                    key={provider.name}
                    onClick={() => handleOAuthLogin(provider.name)}
                    className="w-full py-2.5 px-4 bg-background border border-input rounded-md hover:bg-secondary transition-colors flex items-center justify-center gap-2 text-sm font-medium text-foreground"
                  >
                    {provider.name === 'google' && (
                      <svg className="w-5 h-5" viewBox="0 0 24 24">
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
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
                      </svg>
                    )}
                    {provider.name === 'facebook' && (
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                      </svg>
                    )}
                    Continuar com {provider.display_name}
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              Já tem uma conta?{' '}
              <Link
                to="/login"
                className="text-primary hover:underline font-medium"
              >
                Fazer login
              </Link>
            </p>
          </div>
        </div>

        {/* Password Requirements */}
        <div className="mt-6 p-4 bg-muted/50 rounded-md">
          <p className="text-xs text-muted-foreground font-medium mb-2">
            A senha deve conter:
          </p>
          <ul className="text-xs text-muted-foreground space-y-1 list-disc list-inside">
            <li>Pelo menos 8 caracteres</li>
            <li>Uma letra maiúscula</li>
            <li>Uma letra minúscula</li>
            <li>Um número</li>
            <li>Um caractere especial (!@#$%^&*...)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
