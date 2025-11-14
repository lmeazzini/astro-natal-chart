/**
 * Astrological utilities: symbols, colors, and helper functions
 */

// Planet symbols (Unicode)
export const PLANET_SYMBOLS: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
  Uranus: '♅',
  Neptune: '♆',
  Pluto: '♇',
  'North Node': '☊',
};

// Zodiac sign symbols (Unicode)
export const SIGN_SYMBOLS: Record<string, string> = {
  Aries: '♈',
  Taurus: '♉',
  Gemini: '♊',
  Cancer: '♋',
  Leo: '♌',
  Virgo: '♍',
  Libra: '♎',
  Scorpio: '♏',
  Sagittarius: '♐',
  Capricorn: '♑',
  Aquarius: '♒',
  Pisces: '♓',
};

// Aspect symbols
export const ASPECT_SYMBOLS: Record<string, string> = {
  Conjunction: '☌',
  Opposition: '☍',
  Trine: '△',
  Square: '□',
  Sextile: '⚹',
  Quincunx: '⚻',
  Semisextile: '⚺',
  Semisquare: '∠',
  Sesquiquadrate: '⚼',
};

// Aspect colors (for visual distinction)
export const ASPECT_COLORS: Record<string, string> = {
  Conjunction: '#fbbf24', // yellow
  Opposition: '#ef4444', // red
  Trine: '#3b82f6', // blue
  Square: '#f97316', // orange
  Sextile: '#10b981', // green
  Quincunx: '#8b5cf6', // purple
  Semisextile: '#6b7280', // gray
  Semisquare: '#ec4899', // pink
  Sesquiquadrate: '#14b8a6', // teal
};

// Element colors
export const ELEMENT_COLORS: Record<string, string> = {
  Fire: '#ef4444', // red - Aries, Leo, Sagittarius
  Earth: '#10b981', // green - Taurus, Virgo, Capricorn
  Air: '#3b82f6', // blue - Gemini, Libra, Aquarius
  Water: '#8b5cf6', // purple - Cancer, Scorpio, Pisces
};

// Sign elements mapping
export const SIGN_ELEMENTS: Record<string, string> = {
  Aries: 'Fire',
  Taurus: 'Earth',
  Gemini: 'Air',
  Cancer: 'Water',
  Leo: 'Fire',
  Virgo: 'Earth',
  Libra: 'Air',
  Scorpio: 'Water',
  Sagittarius: 'Fire',
  Capricorn: 'Earth',
  Aquarius: 'Air',
  Pisces: 'Water',
};

// Zodiac signs in order (starting from Aries at 0°)
export const ZODIAC_SIGNS = [
  'Aries',
  'Taurus',
  'Gemini',
  'Cancer',
  'Leo',
  'Virgo',
  'Libra',
  'Scorpio',
  'Sagittarius',
  'Capricorn',
  'Aquarius',
  'Pisces',
];

/**
 * Format degree, minute, second as string
 */
export function formatDMS(degree: number, minute: number, second: number): string {
  return `${degree}°${minute.toString().padStart(2, '0')}'${second.toString().padStart(2, '0')}"`;
}

/**
 * Get sign element
 */
export function getSignElement(sign: string): string {
  return SIGN_ELEMENTS[sign] || 'Unknown';
}

/**
 * Get sign color based on element
 */
export function getSignColor(sign: string): string {
  const element = getSignElement(sign);
  return ELEMENT_COLORS[element] || '#6b7280';
}

/**
 * Convert ecliptic longitude (0-360) to SVG polar coordinates
 * In astrology, 0° = Aries (top), moving counter-clockwise
 * In SVG, we need to adjust: rotate -90° and flip direction
 */
export function longitudeToAngle(longitude: number): number {
  // Astrology: 0° Aries at top (12 o'clock), counter-clockwise
  // SVG: 0° at right (3 o'clock), clockwise
  // Transform: rotate -90° and negate to flip direction
  return 90 - longitude;
}

/**
 * Convert polar coordinates (angle, radius) to cartesian (x, y)
 * for SVG circle centered at (cx, cy)
 */
export function polarToCartesian(
  centerX: number,
  centerY: number,
  radius: number,
  angleInDegrees: number
): { x: number; y: number } {
  const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
  return {
    x: centerX + radius * Math.cos(angleInRadians),
    y: centerY + radius * Math.sin(angleInRadians),
  };
}

/**
 * Get planet symbol with fallback
 */
export function getPlanetSymbol(planetName: string): string {
  return PLANET_SYMBOLS[planetName] || planetName.charAt(0);
}

/**
 * Get sign symbol with fallback
 */
export function getSignSymbol(signName: string): string {
  return SIGN_SYMBOLS[signName] || signName.slice(0, 3);
}

/**
 * Get aspect symbol with fallback
 */
export function getAspectSymbol(aspectName: string): string {
  return ASPECT_SYMBOLS[aspectName] || '';
}

/**
 * Get aspect color
 */
export function getAspectColor(aspectName: string): string {
  return ASPECT_COLORS[aspectName] || '#6b7280';
}

/**
 * Determine if aspect is major (conjunction, opposition, trine, square, sextile)
 */
export function isMajorAspect(aspectName: string): boolean {
  return ['Conjunction', 'Opposition', 'Trine', 'Square', 'Sextile'].includes(
    aspectName
  );
}

/**
 * Format orb value with + or - sign
 */
export function formatOrb(orb: number): string {
  return `${orb.toFixed(2)}°`;
}

/**
 * Get house quadrant (angular houses are 1, 4, 7, 10)
 */
export function isAngularHouse(houseNumber: number): boolean {
  return [1, 4, 7, 10].includes(houseNumber);
}

/**
 * Get house type
 */
export function getHouseType(houseNumber: number): string {
  if ([1, 4, 7, 10].includes(houseNumber)) return 'Angular';
  if ([2, 5, 8, 11].includes(houseNumber)) return 'Succedent';
  if ([3, 6, 9, 12].includes(houseNumber)) return 'Cadent';
  return 'Unknown';
}
