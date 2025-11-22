/**
 * Hook for translating astrological terms (signs, planets, aspects)
 * Uses the 'astrology' namespace from i18n
 */

import { useTranslation } from 'react-i18next';

/**
 * Hook that provides translation functions for astrological terms
 */
export function useAstroTranslation() {
  const { t } = useTranslation('astrology');

  /**
   * Translate a zodiac sign name
   * @param sign - English sign name (e.g., "Aries", "Taurus")
   * @returns Translated sign name
   */
  const translateSign = (sign: string): string => {
    return t(`signs.${sign}`, { defaultValue: sign });
  };

  /**
   * Translate a planet name
   * @param planet - English planet name (e.g., "Sun", "Moon")
   * @returns Translated planet name
   */
  const translatePlanet = (planet: string): string => {
    return t(`planets.${planet}`, { defaultValue: planet });
  };

  /**
   * Translate an aspect name
   * @param aspect - English aspect name (e.g., "Conjunction", "Trine")
   * @returns Translated aspect name
   */
  const translateAspect = (aspect: string): string => {
    return t(`aspects.${aspect}`, { defaultValue: aspect });
  };

  /**
   * Translate a house system name
   * @param system - House system name (e.g., "placidus", "whole_sign")
   * @returns Translated house system name
   */
  const translateHouseSystem = (system: string): string => {
    return t(`houseSystems.${system}`, { defaultValue: system });
  };

  return {
    translateSign,
    translatePlanet,
    translateAspect,
    translateHouseSystem,
    t, // Export raw t function for other astrology translations
  };
}
