/**
 * Interpretation Language Notice component
 *
 * Displays a notice when AI interpretations are in a different language
 * than the user's current UI language. Provides a button to regenerate
 * interpretations in the current language.
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, RefreshCw, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface InterpretationLanguageNoticeProps {
  /** The language code of the current interpretations (e.g., 'pt-BR') */
  interpretationLanguage: string;
  /** Called when user wants to regenerate in current UI language */
  onRegenerate?: () => void;
  /** Whether regeneration is in progress */
  isRegenerating?: boolean;
  /** Called when notice is dismissed */
  onDismiss?: () => void;
  /** Whether to show the dismiss button */
  dismissible?: boolean;
}

/**
 * Get the display name for a language code
 */
function getLanguageDisplayName(languageCode: string): string {
  const languageNames: Record<string, string> = {
    'pt-BR': 'Português (Brasil)',
    'en-US': 'English (US)',
    pt: 'Português',
    en: 'English',
  };
  return languageNames[languageCode] || languageCode;
}

export function InterpretationLanguageNotice({
  interpretationLanguage,
  onRegenerate,
  isRegenerating = false,
  onDismiss,
  dismissible = true,
}: InterpretationLanguageNoticeProps) {
  const { t, i18n } = useTranslation();
  const [isDismissed, setIsDismissed] = useState(false);

  // Normalize language codes for comparison (pt-BR -> pt, en-US -> en)
  const normalizeLanguage = (lang: string) => lang.split('-')[0];
  const currentUiLang = normalizeLanguage(i18n.language);
  const interpretLang = normalizeLanguage(interpretationLanguage);

  // Don't show if languages match or dismissed
  if (currentUiLang === interpretLang || isDismissed) {
    return null;
  }

  const interpretLangDisplay = getLanguageDisplayName(interpretationLanguage);
  const currentLangDisplay = getLanguageDisplayName(i18n.language);

  function handleDismiss() {
    setIsDismissed(true);
    onDismiss?.();
  }

  return (
    <Alert className="relative border-blue-500 bg-blue-50 dark:bg-blue-950 dark:border-blue-800">
      <Globe className="h-4 w-4 text-blue-600 dark:text-blue-400" />
      <AlertDescription className="flex items-center justify-between gap-4 ml-2">
        <div className="flex-1">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            {t('components.interpretationLanguage.mismatchMessage', {
              interpretationLanguage: interpretLangDisplay,
              currentLanguage: currentLangDisplay,
              defaultValue: `These interpretations are in {{interpretationLanguage}}. Would you like to regenerate them in {{currentLanguage}}?`,
            })}
          </p>
          {onRegenerate && (
            <Button
              variant="link"
              size="sm"
              onClick={onRegenerate}
              disabled={isRegenerating}
              className="h-auto p-0 mt-1 text-blue-700 dark:text-blue-300 hover:text-blue-900 dark:hover:text-blue-100"
            >
              <RefreshCw
                className={`h-3 w-3 mr-1 ${isRegenerating ? 'animate-spin' : ''}`}
              />
              {isRegenerating
                ? t('components.interpretationLanguage.regenerating', {
                    defaultValue: 'Regenerating...',
                  })
                : t('components.interpretationLanguage.regenerateButton', {
                    language: currentLangDisplay,
                    defaultValue: 'Regenerate in {{language}}',
                  })}
            </Button>
          )}
        </div>
        {dismissible && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDismiss}
            className="h-8 w-8 p-0 text-blue-800 dark:text-blue-200 hover:bg-blue-100 dark:hover:bg-blue-900"
            aria-label={t('common.close', { defaultValue: 'Close' })}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </AlertDescription>
    </Alert>
  );
}
