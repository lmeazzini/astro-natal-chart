import { MotionConfig } from 'framer-motion';
import { ReactNode } from 'react';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface MotionProviderProps {
  children: ReactNode;
}

/**
 * Provider that configures Framer Motion globally
 * Respects user's prefers-reduced-motion setting
 */
export function MotionProvider({ children }: MotionProviderProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <MotionConfig
      reducedMotion={prefersReducedMotion ? 'always' : 'never'}
      transition={
        prefersReducedMotion ? { duration: 0 } : { type: 'spring', damping: 20, stiffness: 100 }
      }
    >
      {children}
    </MotionConfig>
  );
}
