import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { amplitudeService } from '@/services/amplitude';

/**
 * Hook to track page views with Amplitude Analytics
 *
 * Usage:
 * ```typescript
 * useAmplitudePageView('Login Page', { source: 'direct' });
 * ```
 *
 * @param pageTitle - Human-readable page title
 * @param additionalProperties - Optional additional properties to track
 */
export function useAmplitudePageView(
  pageTitle: string,
  additionalProperties?: Record<string, string | number | boolean | string[]>
) {
  const location = useLocation();

  useEffect(() => {
    amplitudeService.track('page_viewed', {
      page_path: location.pathname,
      page_title: pageTitle,
      ...additionalProperties,
    });
  }, [location.pathname, pageTitle, additionalProperties]);
}
