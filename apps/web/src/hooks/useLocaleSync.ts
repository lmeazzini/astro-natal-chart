/**
 * Hook to synchronize user's locale preference with i18n
 *
 * This hook ensures that when a user logs in, their saved locale preference
 * from the backend is applied to the i18n system and localStorage.
 */

import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';

interface User {
  locale?: string;
}

export function useLocaleSync(user: User | null) {
  const { i18n } = useTranslation();

  useEffect(() => {
    if (user?.locale && user.locale !== i18n.language) {
      // Sync i18n with user's saved locale preference
      i18n.changeLanguage(user.locale);
      localStorage.setItem('astro_language', user.locale);
    }
  }, [user?.locale, i18n]);
}
