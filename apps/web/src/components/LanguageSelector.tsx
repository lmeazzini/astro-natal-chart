/**
 * Language Selector Component
 * Allows users to switch between pt-BR and en-US
 */

import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAuth } from '@/contexts/AuthContext';

const LANGUAGES = [
  { code: 'pt-BR', name: 'Português (BR)', flag: '🇧🇷' },
  { code: 'en-US', name: 'English (US)', flag: '🇺🇸' },
];

export function LanguageSelector() {
  const { i18n } = useTranslation();
  const { user, setUser } = useAuth();

  const handleLanguageChange = async (languageCode: string) => {
    await i18n.changeLanguage(languageCode);

    // Store preference in localStorage
    localStorage.setItem('astro_language', languageCode);

    // If user is authenticated, update backend preference and context
    const token = localStorage.getItem('astro_access_token');
    if (token && user) {
      try {
        await fetch(`${import.meta.env.VITE_API_URL}/api/v1/users/me`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ locale: languageCode }),
        });

        // Update user context to keep in sync
        setUser({ ...user, locale: languageCode });
      } catch (error) {
        console.error('Failed to update language preference:', error);
      }
    }
  };

  return (
    <Select value={i18n.language} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-[180px]">
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4" />
          <SelectValue />
        </div>
      </SelectTrigger>
      <SelectContent>
        {LANGUAGES.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            <div className="flex items-center gap-2">
              <span>{lang.flag}</span>
              <span>{lang.name}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
