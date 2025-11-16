/**
 * Logo component - displays the application logo
 *
 * A reusable component for displaying the Astro logo with different sizes.
 * Uses the transparent logo from public directory.
 */

interface LogoProps {
  /**
   * Size variant of the logo
   * - sm: 32px (small, for navbars)
   * - md: 64px (medium, for headers)
   * - lg: 128px (large, for landing pages)
   * - xl: 192px (extra large, for splash screens)
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Click handler
   */
  onClick?: () => void;
}

const sizeClasses = {
  sm: 'h-8 w-8',     // 32px
  md: 'h-16 w-16',   // 64px
  lg: 'h-32 w-32',   // 128px
  xl: 'h-48 w-48',   // 192px
};

export function Logo({ size = 'md', className = '', onClick }: LogoProps) {
  const sizeClass = sizeClasses[size];

  return (
    <img
      src="/logo.png"
      alt="Real Astrology - Astrologia Natal"
      className={`${sizeClass} ${className}`}
      onClick={onClick}
      loading="lazy"
    />
  );
}
