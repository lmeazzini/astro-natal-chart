/**
 * Shared navigation actions component for authenticated pages
 * Includes: Admin link (if admin), Blog link, Language selector, Theme toggle
 */

import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { LanguageSelector } from '@/components/LanguageSelector';
import { ThemeToggle } from '@/components/ThemeToggle';
import { usePermissions } from '@/hooks/usePermissions';

interface NavActionsProps {
  /** Additional class names for the container */
  className?: string;
  /** Whether to show the blog link (default: true) */
  showBlogLink?: boolean;
}

export function NavActions({ className = '', showBlogLink = true }: NavActionsProps) {
  const { t } = useTranslation();
  const { isAdmin } = usePermissions();

  return (
    <div className={`flex items-center gap-4 ${className}`}>
      {showBlogLink && (
        <Button variant="ghost" size="sm" asChild className="hidden md:inline-flex">
          <Link to="/blog">{t('landing.nav.blog')}</Link>
        </Button>
      )}
      {isAdmin && (
        <Button variant="ghost" size="sm" asChild className="hidden md:inline-flex gap-1">
          <Link to="/admin">
            <Shield className="h-4 w-4" />
            {t('nav.admin', { defaultValue: 'Admin' })}
          </Link>
        </Button>
      )}
      <LanguageSelector />
      <ThemeToggle />
    </div>
  );
}
