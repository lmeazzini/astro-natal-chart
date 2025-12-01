import { Variants } from 'framer-motion';

/**
 * Global animation configurations for consistent motion across the app
 */

// Duration presets (in seconds)
export const duration = {
  instant: 0,
  fast: 0.1,
  normal: 0.2,
  slow: 0.3,
  slower: 0.5,
  slowest: 0.8,
} as const;

// Easing functions for smooth motion
export const ease = {
  // Standard Material Design easing
  standard: [0.4, 0, 0.2, 1],
  // Decelerated easing (fast start, slow end) - good for entering elements
  decelerate: [0, 0, 0.2, 1],
  // Accelerated easing (slow start, fast end) - good for exiting elements
  accelerate: [0.4, 0, 1, 1],
  // Sharp easing for quick actions
  sharp: [0.4, 0, 0.6, 1],
  // Smooth easing for gentle animations
  smooth: [0.25, 0.1, 0.25, 1],
  // Bounce effect for playful interactions
  bounce: [0.68, -0.55, 0.265, 1.55],
} as const;

// Spring animations for more natural motion
export const spring = {
  // Gentle spring for smooth transitions
  gentle: { type: 'spring', damping: 20, stiffness: 100 },
  // Default spring for most interactions
  default: { type: 'spring', damping: 15, stiffness: 150 },
  // Bouncy spring for playful elements
  bouncy: { type: 'spring', damping: 10, stiffness: 300 },
  // Stiff spring for quick, precise movements
  stiff: { type: 'spring', damping: 20, stiffness: 400 },
  // Wobbly spring for elastic effects
  wobbly: { type: 'spring', damping: 8, stiffness: 200 },
} as const;

// Common animation variants
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: duration.normal, ease: ease.standard },
  },
  exit: {
    opacity: 0,
    transition: { duration: duration.fast, ease: ease.standard },
  },
};

export const fadeInUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.normal, ease: ease.decelerate },
  },
  exit: {
    opacity: 0,
    y: -10,
    transition: { duration: duration.fast, ease: ease.accelerate },
  },
};

export const fadeInDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.normal, ease: ease.decelerate },
  },
  exit: {
    opacity: 0,
    y: 10,
    transition: { duration: duration.fast, ease: ease.accelerate },
  },
};

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: spring.gentle,
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: duration.fast, ease: ease.accelerate },
  },
};

export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: spring.default,
  },
  exit: {
    opacity: 0,
    x: -30,
    transition: { duration: duration.fast, ease: ease.accelerate },
  },
};

export const slideInRight: Variants = {
  hidden: { opacity: 0, x: 50 },
  visible: {
    opacity: 1,
    x: 0,
    transition: spring.default,
  },
  exit: {
    opacity: 0,
    x: 30,
    transition: { duration: duration.fast, ease: ease.accelerate },
  },
};

// Stagger animations for lists
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      staggerChildren: 0.02,
      staggerDirection: -1,
    },
  },
};

export const staggerItem: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.normal, ease: ease.standard },
  },
  exit: {
    opacity: 0,
    y: -5,
    transition: { duration: duration.fast, ease: ease.standard },
  },
};

// Tab animation variants
export const tabContent: Variants = {
  hidden: { opacity: 0, x: -10 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: duration.normal, ease: ease.standard },
  },
  exit: {
    opacity: 0,
    x: 10,
    transition: { duration: duration.fast, ease: ease.standard },
  },
};

// Skeleton loading animation
export const skeletonPulse = {
  animate: {
    opacity: [0.5, 1, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Hover and tap animations for interactive elements
export const buttonHover = {
  scale: 1.02,
  transition: { duration: duration.fast, ease: ease.standard },
};

export const buttonTap = {
  scale: 0.98,
  transition: { duration: duration.instant },
};

// Card hover effect
export const cardHover = {
  y: -4,
  transition: spring.gentle,
};

// Floating animation for decorative elements
export const floating: Variants = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// Rotation animation for loading spinners
export const rotate360: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// Check for reduced motion preference
export const prefersReducedMotion = (): boolean => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

// Get motion-safe animation variant
export const motionSafe = <T extends Variants>(
  variant: T,
  reducedVariant?: Variants
): T | Variants => {
  if (prefersReducedMotion()) {
    return (
      reducedVariant || {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 0 } },
        exit: { opacity: 0, transition: { duration: 0 } },
      }
    );
  }
  return variant;
};

// Animation delay utility
export const withDelay = (delay: number, transition: { [key: string]: unknown }) => ({
  ...transition,
  delay,
});

// Stagger delay calculator
export const staggerDelay = (index: number, baseDelay = 0.05) => index * baseDelay;
