/**
 * User registration page
 */

import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

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
