/**
 * AstroIcon Component
 *
 * Renders astrological icons (planets, signs, aspects, houses) from SVG files.
 * Icons are located in /public/icons/astrology/
 */

import { cn } from '@/utils/cn';

export type AstroIconCategory = 'planets' | 'signs' | 'aspects' | 'houses';

// Planet icons
export type PlanetIcon =
  | 'sun'
  | 'moon'
  | 'mercury'
  | 'venus'
  | 'mars'
  | 'jupiter'
  | 'saturn'
  | 'uranus'
  | 'neptune'
  | 'pluto'
  | 'north-node'
  | 'south-node'
  | 'chiron';

// Zodiac sign icons
export type SignIcon =
  | 'aries'
  | 'taurus'
  | 'gemini'
  | 'cancer'
  | 'leo'
  | 'virgo'
  | 'libra'
  | 'scorpio'
  | 'sagittarius'
  | 'capricorn'
  | 'aquarius'
  | 'pisces';

// Aspect icons
export type AspectIcon =
  | 'conjunction'
  | 'opposition'
  | 'trine'
  | 'square'
  | 'sextile'
  | 'quincunx'
  | 'semisextile'
  | 'semisquare'
  | 'sesquiquadrate';

// House icons
export type HouseIcon = 'ascendant' | 'midheaven' | 'descendant' | 'imum-coeli';

// Union of all icon names
export type AstroIconName = PlanetIcon | SignIcon | AspectIcon | HouseIcon;

interface AstroIconProps {
  /** The name of the icon */
  name: AstroIconName;
  /** The category of the icon (auto-detected if not provided) */
  category?: AstroIconCategory;
  /** Size in pixels (default: 24) */
  size?: number;
  /** Additional CSS classes */
  className?: string;
  /** Accessible label for the icon */
  label?: string;
}

// Maps for auto-detecting category from icon name
const planetIcons: PlanetIcon[] = [
  'sun',
  'moon',
  'mercury',
  'venus',
  'mars',
  'jupiter',
  'saturn',
  'uranus',
  'neptune',
  'pluto',
  'north-node',
  'south-node',
  'chiron',
];

const signIcons: SignIcon[] = [
  'aries',
  'taurus',
  'gemini',
  'cancer',
  'leo',
  'virgo',
  'libra',
  'scorpio',
  'sagittarius',
  'capricorn',
  'aquarius',
  'pisces',
];

const aspectIcons: AspectIcon[] = [
  'conjunction',
  'opposition',
  'trine',
  'square',
  'sextile',
  'quincunx',
  'semisextile',
  'semisquare',
  'sesquiquadrate',
];

const houseIcons: HouseIcon[] = ['ascendant', 'midheaven', 'descendant', 'imum-coeli'];

/**
 * Auto-detect the category based on icon name
 */
function detectCategory(name: AstroIconName): AstroIconCategory {
  if (planetIcons.includes(name as PlanetIcon)) return 'planets';
  if (signIcons.includes(name as SignIcon)) return 'signs';
  if (aspectIcons.includes(name as AspectIcon)) return 'aspects';
  if (houseIcons.includes(name as HouseIcon)) return 'houses';
  // Default to planets if not found
  return 'planets';
}

/**
 * AstroIcon Component
 *
 * @example
 * // Planet icon
 * <AstroIcon name="sun" />
 *
 * @example
 * // Zodiac sign with custom size
 * <AstroIcon name="aries" size={32} />
 *
 * @example
 * // Aspect with custom color via className
 * <AstroIcon name="trine" className="text-green-500" />
 *
 * @example
 * // With explicit category
 * <AstroIcon name="ascendant" category="houses" />
 */
export function AstroIcon({ name, category, size = 24, className, label }: AstroIconProps) {
  const resolvedCategory = category || detectCategory(name);
  const iconPath = `/icons/astrology/${resolvedCategory}/${name}.svg`;

  return (
    <img
      src={iconPath}
      alt={label || name}
      width={size}
      height={size}
      className={cn('inline-block', className)}
      style={{
        // This CSS filter trick makes black SVGs inherit currentColor
        // Works because our SVGs use stroke="currentColor"
        filter: 'var(--icon-filter, none)',
      }}
      loading="lazy"
    />
  );
}

/**
 * Helper to get all icons of a specific category
 */
// eslint-disable-next-line react-refresh/only-export-components
export function getIconsByCategory(category: AstroIconCategory): AstroIconName[] {
  switch (category) {
    case 'planets':
      return planetIcons;
    case 'signs':
      return signIcons;
    case 'aspects':
      return aspectIcons;
    case 'houses':
      return houseIcons;
    default:
      return [];
  }
}

/**
 * All available icon names
 */
// eslint-disable-next-line react-refresh/only-export-components
export const allAstroIcons: AstroIconName[] = [
  ...planetIcons,
  ...signIcons,
  ...aspectIcons,
  ...houseIcons,
];

export default AstroIcon;
