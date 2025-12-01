/**
 * Cookie Banner - LGPD/GDPR compliant cookie consent banner
 * Appears on first visit, allows users to accept or customize cookies
 */

import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { X } from 'lucide-react';

// shadcn/ui components
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';

interface CookiePreferences {
  essential: boolean; // Always true, cannot be disabled
  functional: boolean;
  analytics: boolean;
}

const COOKIE_CONSENT_KEY = 'astro_cookie_consent';

export function CookieBanner() {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    essential: true,
    functional: true,
    analytics: true,
  });

  useEffect(() => {
    // Check if user has already consented
    const existingConsent = localStorage.getItem(COOKIE_CONSENT_KEY);

    if (!existingConsent) {
      // Show banner after a small delay
      setTimeout(() => setIsVisible(true), 1000);
    } else {
      // Load existing preferences
      try {
        const stored = JSON.parse(existingConsent);
        setPreferences(stored.preferences);
        // Apply preferences (would integrate with analytics, etc.)
        applyPreferences(stored.preferences);
      } catch (e) {
        // Invalid JSON, show banner again
        setIsVisible(true);
      }
    }
  }, []);

  const applyPreferences = (prefs: CookiePreferences) => {
    // TODO: Integrate with Google Analytics
    if (prefs.analytics) {
      // Enable GA
      console.log('Analytics enabled');
    } else {
      // Disable GA
      console.log('Analytics disabled');
    }

    // TODO: Apply functional cookie preferences
    if (prefs.functional) {
      console.log('Functional cookies enabled');
    }
  };

  const handleAcceptAll = () => {
    const consent = {
      timestamp: new Date().toISOString(),
      preferences: {
        essential: true,
        functional: true,
        analytics: true,
      },
    };

    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
    applyPreferences(consent.preferences);
    setIsVisible(false);
  };

  const handleAcceptEssentialOnly = () => {
    const consent = {
      timestamp: new Date().toISOString(),
      preferences: {
        essential: true,
        functional: false,
        analytics: false,
      },
    };

    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
    applyPreferences(consent.preferences);
    setIsVisible(false);
  };

  const handleSavePreferences = () => {
    const consent = {
      timestamp: new Date().toISOString(),
      preferences,
    };

    localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(consent));
    applyPreferences(preferences);
    setIsVisible(false);
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4">
      <Card className="max-w-7xl mx-auto bg-card/95 backdrop-blur-sm">
        <CardContent className="pt-6">
          {!showDetails ? (
            // Simple banner
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-foreground mb-1">
                  🍪 {t('components.cookies.title', { defaultValue: 'Este site usa cookies' })}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {t('components.cookies.description', {
                    defaultValue:
                      'Usamos cookies essenciais, funcionais e analíticos para melhorar sua experiência. Consulte nossa',
                  })}{' '}
                  <Link to="/cookies" className="text-primary hover:underline" target="_blank">
                    {t('components.cookies.policyLink', { defaultValue: 'Política de Cookies' })}
                  </Link>{' '}
                  {t('components.cookies.forMoreDetails', { defaultValue: 'para mais detalhes.' })}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" onClick={() => setShowDetails(true)}>
                  {t('components.cookies.customize', { defaultValue: 'Personalizar' })}
                </Button>
                <Button variant="outline" size="sm" onClick={handleAcceptEssentialOnly}>
                  {t('components.cookies.essentialOnly', { defaultValue: 'Apenas Essenciais' })}
                </Button>
                <Button size="sm" onClick={handleAcceptAll}>
                  {t('components.cookies.acceptAll', { defaultValue: 'Aceitar Todos' })}
                </Button>
              </div>
            </div>
          ) : (
            // Detailed preferences
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-foreground">
                  {t('components.cookies.preferencesTitle', {
                    defaultValue: 'Preferências de Cookies',
                  })}
                </h3>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setShowDetails(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-3 mb-4">
                {/* Essential Cookies */}
                <div className="flex items-start justify-between p-3 bg-muted/50 rounded-md">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-xs font-semibold text-foreground">
                        {t('components.cookies.essential', { defaultValue: 'Cookies Essenciais' })}
                      </h4>
                      <Badge variant="secondary" className="h-5">
                        {t('components.cookies.required', { defaultValue: 'Obrigatório' })}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {t('components.cookies.essentialDesc', {
                        defaultValue:
                          'Necessários para autenticação e funcionamento básico do site',
                      })}
                    </p>
                  </div>
                  <Checkbox
                    checked={true}
                    disabled
                    className="mt-1 data-[state=checked]:opacity-50"
                  />
                </div>

                {/* Functional Cookies */}
                <div className="flex items-start justify-between p-3 bg-background rounded-md border border-border">
                  <div className="flex-1">
                    <h4 className="text-xs font-semibold text-foreground">
                      {t('components.cookies.functional', { defaultValue: 'Cookies Funcionais' })}
                    </h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {t('components.cookies.functionalDesc', {
                        defaultValue: 'Lembrar preferências (tema, idioma, fuso horário)',
                      })}
                    </p>
                  </div>
                  <Checkbox
                    checked={preferences.functional}
                    onCheckedChange={(checked) =>
                      setPreferences({
                        ...preferences,
                        functional: checked as boolean,
                      })
                    }
                    className="mt-1"
                  />
                </div>

                {/* Analytics Cookies */}
                <div className="flex items-start justify-between p-3 bg-background rounded-md border border-border">
                  <div className="flex-1">
                    <h4 className="text-xs font-semibold text-foreground">
                      {t('components.cookies.analytics', { defaultValue: 'Cookies Analíticos' })}
                    </h4>
                    <p className="text-xs text-muted-foreground mt-1">
                      {t('components.cookies.analyticsDesc', {
                        defaultValue: 'Google Analytics (anonimizado) - entender uso do site',
                      })}
                    </p>
                  </div>
                  <Checkbox
                    checked={preferences.analytics}
                    onCheckedChange={(checked) =>
                      setPreferences({
                        ...preferences,
                        analytics: checked as boolean,
                      })
                    }
                    className="mt-1"
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-2">
                <Button size="sm" className="flex-1" onClick={handleSavePreferences}>
                  {t('components.cookies.savePreferences', { defaultValue: 'Salvar Preferências' })}
                </Button>
                <Button size="sm" variant="outline" className="flex-1" onClick={handleAcceptAll}>
                  {t('components.cookies.acceptAll', { defaultValue: 'Aceitar Todos' })}
                </Button>
              </div>

              <p className="mt-3 text-xs text-center text-muted-foreground">
                {t('components.cookies.changePreferencesNote', {
                  defaultValue:
                    'Você pode alterar suas preferências a qualquer momento em Configurações → Privacidade',
                })}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
