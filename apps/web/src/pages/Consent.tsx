/**
 * Consent page - User accepts Terms, Privacy and Cookies policies
 * Used during registration or when policies are updated
 */

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface ConsentProps {
  onAccept?: () => void;
  requiredConsents?: ('terms' | 'privacy' | 'cookies')[];
}

export function ConsentPage({ onAccept, requiredConsents = ['terms', 'privacy', 'cookies'] }: ConsentProps = {}) {
  const navigate = useNavigate();

  const [consents, setConsents] = useState({
    terms: false,
    privacy: false,
    cookies: false,
  });

  const [error, setError] = useState('');

  const handleCheckboxChange = (type: 'terms' | 'privacy' | 'cookies', checked: boolean) => {
    setConsents((prev) => ({
      ...prev,
      [type]: checked,
    }));
    setError('');
  };

  const handleAccept = () => {
    // Validate all required consents are checked
    const missingConsents = requiredConsents.filter((type) => !consents[type]);

    if (missingConsents.length > 0) {
      setError('Você deve aceitar todos os termos obrigatórios para continuar');
      return;
    }

    // Store consent in localStorage (will be sent to backend on registration)
    localStorage.setItem(
      'astro_pending_consent',
      JSON.stringify({
        terms: consents.terms,
        privacy: consents.privacy,
        cookies: consents.cookies,
        timestamp: new Date().toISOString(),
      })
    );

    if (onAccept) {
      onAccept();
    } else {
      // Default: navigate to register page
      navigate('/register');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-background to-secondary/10 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Consentimento e Privacidade
          </h1>
          <p className="text-muted-foreground">
            Para usar o Real Astrology, você precisa aceitar nossos termos e
            políticas
          </p>
        </div>

        {/* Consent Form */}
        <Card>
          <CardHeader>
            <CardTitle>Termos de Consentimento</CardTitle>
            <CardDescription>
              Por favor, leia e aceite os documentos abaixo para continuar
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert variant="destructive" className="mb-6">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-6">
              {/* Terms of Service */}
              {requiredConsents.includes('terms') && (
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="terms"
                    checked={consents.terms}
                    onCheckedChange={(checked) => handleCheckboxChange('terms', checked as boolean)}
                  />
                  <label htmlFor="terms" className="flex-1 text-sm cursor-pointer">
                    <span className="font-medium text-foreground">
                      Eu li e aceito os{' '}
                      <Link
                        to="/terms"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        Termos de Uso
                      </Link>{' '}
                      <span className="text-destructive">*</span>
                    </span>
                    <p className="mt-1 text-muted-foreground">
                      Concordo com as regras de uso da plataforma, incluindo
                      responsabilidades e limitações de serviço.
                    </p>
                  </label>
                </div>
              )}

              {/* Privacy Policy */}
              {requiredConsents.includes('privacy') && (
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="privacy"
                    checked={consents.privacy}
                    onCheckedChange={(checked) => handleCheckboxChange('privacy', checked as boolean)}
                  />
                  <label htmlFor="privacy" className="flex-1 text-sm cursor-pointer">
                    <span className="font-medium text-foreground">
                      Eu li e aceito a{' '}
                      <Link
                        to="/privacy"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        Política de Privacidade
                      </Link>{' '}
                      <span className="text-destructive">*</span>
                    </span>
                    <p className="mt-1 text-muted-foreground">
                      Autorizo o processamento dos meus dados pessoais conforme
                      LGPD/GDPR, incluindo dados de nascimento para cálculo de
                      mapas natais.
                    </p>
                  </label>
                </div>
              )}

              {/* Cookie Policy */}
              {requiredConsents.includes('cookies') && (
                <div className="flex items-start gap-3">
                  <Checkbox
                    id="cookies"
                    checked={consents.cookies}
                    onCheckedChange={(checked) => handleCheckboxChange('cookies', checked as boolean)}
                  />
                  <label htmlFor="cookies" className="flex-1 text-sm cursor-pointer">
                    <span className="font-medium text-foreground">
                      Eu li e aceito a{' '}
                      <Link
                        to="/cookies"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary hover:underline"
                      >
                        Política de Cookies
                      </Link>{' '}
                      <span className="text-destructive">*</span>
                    </span>
                    <p className="mt-1 text-muted-foreground">
                      Concordo com o uso de cookies essenciais, funcionais e
                      analíticos para melhorar minha experiência.
                    </p>
                  </label>
                </div>
              )}
            </div>

            {/* Info Box */}
            <Alert className="mt-6 border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
              <AlertDescription>
                <h3 className="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  Seus Direitos LGPD/GDPR:
                </h3>
                <ul className="text-xs text-blue-800 dark:text-blue-200 space-y-1">
                  <li>✓ Acessar e exportar todos os seus dados</li>
                  <li>✓ Corrigir informações incorretas</li>
                  <li>✓ Solicitar exclusão da conta (direito ao esquecimento)</li>
                  <li>✓ Revogar consentimento a qualquer momento</li>
                </ul>
                <p className="mt-2 text-xs text-blue-700 dark:text-blue-300">
                  Todas essas opções estarão disponíveis em Configurações →
                  Privacidade
                </p>
              </AlertDescription>
            </Alert>

            {/* Required notice */}
            <p className="mt-6 text-xs text-muted-foreground text-center">
              <span className="text-destructive">*</span> Campos obrigatórios
            </p>

            {/* Buttons */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => navigate(-1)}
              >
                Voltar
              </Button>
              <Button
                className="flex-1"
                onClick={handleAccept}
              >
                Aceitar e Continuar
              </Button>
            </div>

            {/* Contact */}
            <div className="mt-6 text-center text-xs text-muted-foreground">
              Dúvidas?{' '}
              <a
                href="mailto:dpo@astro-app.com"
                className="text-primary hover:underline"
              >
                dpo@astro-app.com
              </a>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
