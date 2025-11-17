/**
 * Tests for astrological utilities
 */

import { describe, it, expect } from 'vitest';
import {
  PLANET_SYMBOLS,
  SIGN_SYMBOLS,
  ASPECT_SYMBOLS,
  ELEMENT_COLORS,
  SIGN_ELEMENTS,
  ZODIAC_SIGNS,
  formatDMS,
  getSignElement,
  getSignColor,
  longitudeToAngle,
  polarToCartesian,
  getPlanetSymbol,
  getSignSymbol,
  getAspectSymbol,
  getAspectColor,
  isMajorAspect,
  formatOrb,
  isAngularHouse,
  getHouseType,
} from './astro';

describe('Astrological Symbols', () => {
  it('should have all planet symbols', () => {
    expect(PLANET_SYMBOLS.Sun).toBe('☉');
    expect(PLANET_SYMBOLS.Moon).toBe('☽');
    expect(PLANET_SYMBOLS.Mercury).toBe('☿');
    expect(PLANET_SYMBOLS.Mars).toBe('♂');
    expect(PLANET_SYMBOLS['North Node']).toBe('☊');
  });

  it('should have all zodiac sign symbols', () => {
    expect(SIGN_SYMBOLS.Aries).toBe('♈');
    expect(SIGN_SYMBOLS.Taurus).toBe('♉');
    expect(SIGN_SYMBOLS.Pisces).toBe('♓');
  });

  it('should have all aspect symbols', () => {
    expect(ASPECT_SYMBOLS.Conjunction).toBe('☌');
    expect(ASPECT_SYMBOLS.Opposition).toBe('☍');
    expect(ASPECT_SYMBOLS.Trine).toBe('△');
  });
});

describe('formatDMS', () => {
  it('should format degrees, minutes, seconds correctly', () => {
    expect(formatDMS(15, 30, 45)).toBe("15°30'45\"");
    expect(formatDMS(0, 0, 0)).toBe("0°00'00\"");
    expect(formatDMS(29, 59, 59)).toBe("29°59'59\"");
  });

  it('should pad single-digit minutes and seconds', () => {
    expect(formatDMS(10, 5, 8)).toBe("10°05'08\"");
  });
});

describe('getSignElement', () => {
  it('should return correct elements for fire signs', () => {
    expect(getSignElement('Aries')).toBe('Fire');
    expect(getSignElement('Leo')).toBe('Fire');
    expect(getSignElement('Sagittarius')).toBe('Fire');
  });

  it('should return correct elements for earth signs', () => {
    expect(getSignElement('Taurus')).toBe('Earth');
    expect(getSignElement('Virgo')).toBe('Earth');
    expect(getSignElement('Capricorn')).toBe('Earth');
  });

  it('should return correct elements for air signs', () => {
    expect(getSignElement('Gemini')).toBe('Air');
    expect(getSignElement('Libra')).toBe('Air');
    expect(getSignElement('Aquarius')).toBe('Air');
  });

  it('should return correct elements for water signs', () => {
    expect(getSignElement('Cancer')).toBe('Water');
    expect(getSignElement('Scorpio')).toBe('Water');
    expect(getSignElement('Pisces')).toBe('Water');
  });

  it('should return Unknown for invalid signs', () => {
    expect(getSignElement('InvalidSign')).toBe('Unknown');
  });
});

describe('getSignColor', () => {
  it('should return correct colors based on elements', () => {
    expect(getSignColor('Aries')).toBe(ELEMENT_COLORS.Fire);
    expect(getSignColor('Taurus')).toBe(ELEMENT_COLORS.Earth);
    expect(getSignColor('Gemini')).toBe(ELEMENT_COLORS.Air);
    expect(getSignColor('Cancer')).toBe(ELEMENT_COLORS.Water);
  });

  it('should return default color for unknown signs', () => {
    expect(getSignColor('Unknown')).toBe('#6b7280');
  });
});

describe('longitudeToAngle', () => {
  it('should convert 0° (Aries) to 90° (top of chart)', () => {
    expect(longitudeToAngle(0)).toBe(90);
  });

  it('should convert 90° (Cancer) to 0° (left of chart)', () => {
    expect(longitudeToAngle(90)).toBe(0);
  });

  it('should convert 180° (Libra) to -90° (bottom of chart)', () => {
    expect(longitudeToAngle(180)).toBe(-90);
  });

  it('should convert 270° (Capricorn) to -180° (right of chart)', () => {
    expect(longitudeToAngle(270)).toBe(-180);
  });
});

describe('polarToCartesian', () => {
  it('should convert polar coordinates to cartesian', () => {
    const result = polarToCartesian(0, 0, 100, 0);
    expect(result.x).toBeCloseTo(100, 1);
    expect(result.y).toBeCloseTo(0, 1);
  });

  it('should handle 90 degree angle', () => {
    const result = polarToCartesian(0, 0, 100, 90);
    expect(result.x).toBeCloseTo(0, 1);
    expect(result.y).toBeCloseTo(100, 1);
  });

  it('should handle negative angles', () => {
    const result = polarToCartesian(0, 0, 100, -90);
    expect(result.x).toBeCloseTo(0, 1);
    expect(result.y).toBeCloseTo(-100, 1);
  });

  it('should handle center offset', () => {
    const result = polarToCartesian(50, 50, 100, 0);
    expect(result.x).toBeCloseTo(150, 1);
    expect(result.y).toBeCloseTo(50, 1);
  });
});

describe('Symbol Getters with Fallback', () => {
  it('getPlanetSymbol should return symbol or fallback', () => {
    expect(getPlanetSymbol('Sun')).toBe('☉');
    expect(getPlanetSymbol('UnknownPlanet')).toBe('U');
  });

  it('getSignSymbol should return symbol or fallback', () => {
    expect(getSignSymbol('Aries')).toBe('♈');
    expect(getSignSymbol('UnknownSign')).toBe('Unk');
  });

  it('getAspectSymbol should return symbol or empty string', () => {
    expect(getAspectSymbol('Trine')).toBe('△');
    expect(getAspectSymbol('Unknown')).toBe('');
  });
});

describe('getAspectColor', () => {
  it('should return correct colors for aspects', () => {
    expect(getAspectColor('Conjunction')).toBe('#fbbf24');
    expect(getAspectColor('Opposition')).toBe('#ef4444');
    expect(getAspectColor('Trine')).toBe('#3b82f6');
  });

  it('should return default color for unknown aspects', () => {
    expect(getAspectColor('Unknown')).toBe('#6b7280');
  });
});

describe('isMajorAspect', () => {
  it('should identify major aspects', () => {
    expect(isMajorAspect('Conjunction')).toBe(true);
    expect(isMajorAspect('Opposition')).toBe(true);
    expect(isMajorAspect('Trine')).toBe(true);
    expect(isMajorAspect('Square')).toBe(true);
    expect(isMajorAspect('Sextile')).toBe(true);
  });

  it('should identify minor aspects', () => {
    expect(isMajorAspect('Quincunx')).toBe(false);
    expect(isMajorAspect('Semisextile')).toBe(false);
    expect(isMajorAspect('Semisquare')).toBe(false);
  });
});

describe('formatOrb', () => {
  it('should format orb values with degree symbol', () => {
    expect(formatOrb(2.5)).toBe('2.50°');
    expect(formatOrb(0.12)).toBe('0.12°');
    expect(formatOrb(8)).toBe('8.00°');
  });

  it('should handle negative orbs', () => {
    expect(formatOrb(-1.5)).toBe('-1.50°');
  });
});

describe('House Functions', () => {
  it('isAngularHouse should identify angular houses', () => {
    expect(isAngularHouse(1)).toBe(true);
    expect(isAngularHouse(4)).toBe(true);
    expect(isAngularHouse(7)).toBe(true);
    expect(isAngularHouse(10)).toBe(true);
    expect(isAngularHouse(2)).toBe(false);
    expect(isAngularHouse(5)).toBe(false);
  });

  it('getHouseType should return correct type', () => {
    expect(getHouseType(1)).toBe('Angular');
    expect(getHouseType(4)).toBe('Angular');
    expect(getHouseType(2)).toBe('Succedent');
    expect(getHouseType(5)).toBe('Succedent');
    expect(getHouseType(3)).toBe('Cadent');
    expect(getHouseType(6)).toBe('Cadent');
    expect(getHouseType(13)).toBe('Unknown');
  });
});

describe('Constants Arrays', () => {
  it('ZODIAC_SIGNS should have 12 signs in order', () => {
    expect(ZODIAC_SIGNS).toHaveLength(12);
    expect(ZODIAC_SIGNS[0]).toBe('Aries');
    expect(ZODIAC_SIGNS[11]).toBe('Pisces');
  });

  it('SIGN_ELEMENTS should have all 12 signs', () => {
    expect(Object.keys(SIGN_ELEMENTS)).toHaveLength(12);
  });
});
