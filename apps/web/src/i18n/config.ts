/**
 * i18next Configuration
 * Internationalization setup for pt-BR and en-US
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import ptBRTranslation from '../locales/pt-BR/translation.json';
import ptBRAstrology from '../locales/pt-BR/astrology.json';
import enUSTranslation from '../locales/en-US/translation.json';
import enUSAstrology from '../locales/en-US/astrology.json';

// Translation resources
const resources = {
  'pt-BR': {
    translation: ptBRTranslation,
    astrology: ptBRAstrology,
  },
  'en-US': {
    translation: enUSTranslation,
    astrology: enUSAstrology,
  },
};

i18n
  // Detect user language
  .use(LanguageDetector)
  // Pass i18n instance to react-i18next
  .use(initReactI18next)
  // Initialize i18next
  .init({
    resources,
    fallbackLng: 'pt-BR',
    defaultNS: 'translation',
    ns: ['translation', 'astrology'],

    // Language detection order
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'astro_language',
    },

    interpolation: {
      escapeValue: false, // React already escapes
    },

    // Enable debug in development
    debug: import.meta.env.DEV,
  });

export default i18n;
