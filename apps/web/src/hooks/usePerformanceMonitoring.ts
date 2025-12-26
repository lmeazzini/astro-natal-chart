/**
 * Performance monitoring hook for tracking slow page loads.
 * Uses the Navigation Timing API to detect when page loads exceed a threshold.
 */

import { useEffect, useRef } from 'react';
import { amplitudeService } from '@/services/amplitude';

const DEFAULT_THRESHOLD_MS = 3000; // 3 seconds

interface PerformanceMonitoringOptions {
  /** Custom threshold in milliseconds (default: 3000) */
  threshold?: number;
  /** Whether to track the event even if below threshold (for analytics) */
  trackAll?: boolean;
}

/**
 * Hook to monitor page load performance and track slow loads to Amplitude.
 *
 * @param pageName - Identifier for the page being monitored
 * @param options - Optional configuration
 *
 * @example
 * ```tsx
 * function Dashboard() {
 *   usePerformanceMonitoring('dashboard');
 *   return <div>...</div>;
 * }
 * ```
 */
export function usePerformanceMonitoring(
  pageName: string,
  options: PerformanceMonitoringOptions = {}
) {
  const { threshold = DEFAULT_THRESHOLD_MS, trackAll = false } = options;
  const hasTracked = useRef(false);

  useEffect(() => {
    // Only track once per mount
    if (hasTracked.current) return;

    const checkPerformance = () => {
      try {
        const entries = performance.getEntriesByType('navigation');
        if (entries.length === 0) return;

        const navigation = entries[0] as PerformanceNavigationTiming;

        // Wait for loadEventEnd to be set
        if (navigation.loadEventEnd === 0) {
          // Retry after a short delay
          setTimeout(checkPerformance, 100);
          return;
        }

        const loadTime = navigation.loadEventEnd - navigation.startTime;

        // Only track if load time exceeds threshold (or trackAll is true)
        if (loadTime > threshold || trackAll) {
          amplitudeService.track('slow_performance_detected', {
            page_path: window.location.pathname,
            load_time_ms: Math.round(loadTime),
            threshold_ms: threshold,
            resource_type: 'page',
            source: pageName,
          });
        }

        hasTracked.current = true;
      } catch {
        // Performance API might not be available in all browsers
        // Silently fail
      }
    };

    // Check performance after the page has fully loaded
    if (document.readyState === 'complete') {
      // Use setTimeout to ensure loadEventEnd is populated
      setTimeout(checkPerformance, 0);
    } else {
      const handleLoad = () => {
        setTimeout(checkPerformance, 0);
      };
      window.addEventListener('load', handleLoad);
      return () => window.removeEventListener('load', handleLoad);
    }
  }, [pageName, threshold, trackAll]);
}
