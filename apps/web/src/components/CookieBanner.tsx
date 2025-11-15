/**
 * Cookie Banner - LGPD/GDPR compliant cookie consent banner
 * Appears on first visit, allows users to accept or customize cookies
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

interface CookiePreferences {
  essential: boolean; // Always true, cannot be disabled
  functional: boolean;
  analytics: boolean;
}

const COOKIE_CONSENT_KEY = 'astro_cookie_consent';

export function CookieBanner() {
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
    <div className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-card/95 backdrop-blur-sm border-t border-border shadow-lg">
      <div className="max-w-7xl mx-auto">
        {!showDetails ? (
          // Simple banner
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-foreground mb-1">
                🍪 Este site usa cookies
              </h3>
              <p className="text-xs text-muted-foreground">
                Usamos cookies essenciais, funcionais e analíticos para melhorar
                sua experiência. Consulte nossa{' '}
                <Link
                  to="/cookies"
                  className="text-primary hover:underline"
                  target="_blank"
                >
                  Política de Cookies
                </Link>{' '}
                para mais detalhes.
              </p>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setShowDetails(true)}
                className="px-4 py-2 text-xs font-medium bg-background border border-input rounded-md hover:bg-secondary transition-colors"
              >
                Personalizar
              </button>
              <button
                onClick={handleAcceptEssentialOnly}
                className="px-4 py-2 text-xs font-medium bg-background border border-input rounded-md hover:bg-secondary transition-colors"
              >
                Apenas Essenciais
              </button>
              <button
                onClick={handleAcceptAll}
                className="px-4 py-2 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:opacity-90 transition-opacity"
              >
                Aceitar Todos
              </button>
            </div>
          </div>
        ) : (
          // Detailed preferences
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-foreground">
                Preferências de Cookies
              </h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            </div>

            <div className="space-y-3 mb-4">
              {/* Essential Cookies */}
              <div className="flex items-start justify-between p-3 bg-muted/50 rounded-md">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h4 className="text-xs font-semibold text-foreground">
                      Cookies Essenciais
                    </h4>
                    <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary rounded">
                      Obrigatório
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Necessários para autenticação e funcionamento básico do site
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={true}
                  disabled
                  className="mt-1 h-4 w-4 rounded border-input opacity-50 cursor-not-allowed"
                />
              </div>

              {/* Functional Cookies */}
              <div className="flex items-start justify-between p-3 bg-background rounded-md border border-border">
                <div className="flex-1">
                  <h4 className="text-xs font-semibold text-foreground">
                    Cookies Funcionais
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    Lembrar preferências (tema, idioma, fuso horário)
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.functional}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      functional: e.target.checked,
                    })
                  }
                  className="mt-1 h-4 w-4 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Analytics Cookies */}
              <div className="flex items-start justify-between p-3 bg-background rounded-md border border-border">
                <div className="flex-1">
                  <h4 className="text-xs font-semibold text-foreground">
                    Cookies Analíticos
                  </h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    Google Analytics (anonimizado) - entender uso do site
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.analytics}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      analytics: e.target.checked,
                    })
                  }
                  className="mt-1 h-4 w-4 rounded border-input text-primary focus:ring-2 focus:ring-primary"
                />
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <button
                onClick={handleSavePreferences}
                className="flex-1 px-4 py-2 text-xs font-medium bg-primary text-primary-foreground rounded-md hover:opacity-90 transition-opacity"
              >
                Salvar Preferências
              </button>
              <button
                onClick={handleAcceptAll}
                className="flex-1 px-4 py-2 text-xs font-medium bg-background border border-input rounded-md hover:bg-secondary transition-colors"
              >
                Aceitar Todos
              </button>
            </div>

            <p className="mt-3 text-xs text-center text-muted-foreground">
              Você pode alterar suas preferências a qualquer momento em
              Configurações → Privacidade
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
