import { useEffect, useState } from 'react';

/**
 * Hook to detect if the user prefers reduced motion
 * Respects accessibility preferences for users who are sensitive to motion
 */
export function useReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    // Check if window is available (for SSR compatibility)
    if (typeof window === 'undefined') return;

    // Create media query for prefers-reduced-motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Set initial value
    setPrefersReducedMotion(mediaQuery.matches);

    // Create event handler
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Listen for changes
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // Fallback for older browsers
      mediaQuery.addListener(handleChange);
    }

    // Cleanup
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        // Fallback for older browsers
        mediaQuery.removeListener(handleChange);
      }
    };
  }, []);

  return prefersReducedMotion;
}

/**
 * Hook to get motion-safe animation variants
 * Returns reduced motion variants when user prefers reduced motion
 */
export function useMotionSafeVariants<T extends Record<string, unknown>>(
  variants: T,
  reducedVariants?: T
): T {
  const prefersReducedMotion = useReducedMotion();

  if (prefersReducedMotion) {
    if (reducedVariants) {
      return reducedVariants;
    }
    // Return a casted version for compatibility
    return {
      hidden: { opacity: 0 },
      visible: { opacity: 1, transition: { duration: 0 } },
      exit: { opacity: 0, transition: { duration: 0 } },
    } as unknown as T;
  }

  return variants;
}