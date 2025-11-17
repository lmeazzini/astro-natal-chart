/**
 * Tests for dignities utility functions
 */

import { describe, it, expect } from 'vitest';
import {
  getDignityScore,
  getDignityBadge,
  getScoreColorClass,
  getScoreBadgeColor,
  getClassificationLabel,
  getDignityDetails,
  isClassicalPlanet,
  getDignityExplanation,
  type Dignities,
} from './dignities';

describe('getDignityScore', () => {
  it('should return score from dignities', () => {
    const dignities: Dignities = {
      is_ruler: true,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 5,
      classification: 'strong',
    };
    expect(getDignityScore(dignities)).toBe(5);
  });

  it('should return 0 for undefined dignities', () => {
    expect(getDignityScore(undefined)).toBe(0);
  });
});

describe('getDignityBadge', () => {
  it('should return ruler badge for domicile', () => {
    const dignities: Dignities = {
      is_ruler: true,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 5,
      classification: 'strong',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('👑');
    expect(badge.label).toBe('Domicílio');
    expect(badge.color).toContain('green');
  });

  it('should return exaltation badge', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: true,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 4,
      classification: 'strong',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('🌟');
    expect(badge.label).toBe('Exaltação');
    expect(badge.color).toContain('lime');
  });

  it('should return fall badge', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: false,
      is_fall: true,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: -4,
      classification: 'weak',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('⬇️');
    expect(badge.label).toBe('Queda');
    expect(badge.color).toContain('red');
  });

  it('should return detriment badge', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: true,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: -5,
      classification: 'weak',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('⚠️');
    expect(badge.label).toBe('Detrimento');
    expect(badge.color).toContain('orange');
  });

  it('should return triplicity badge for day ruler', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: 'day',
      term_ruler: null,
      face_ruler: null,
      score: 3,
      classification: 'moderate',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('🔥');
    expect(badge.label).toBe('Triplicidade');
    expect(badge.color).toContain('yellow');
  });

  it('should return triplicity badge for night ruler', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: 'night',
      term_ruler: null,
      face_ruler: null,
      score: 3,
      classification: 'moderate',
    };
    const badge = getDignityBadge(dignities);
    expect(badge.icon).toBe('🌙');
    expect(badge.label).toBe('Triplicidade');
  });

  it('should return peregrine badge for no dignities', () => {
    const badge = getDignityBadge(undefined);
    expect(badge.icon).toBe('🚶');
    expect(badge.label).toBe('Peregrino');
    expect(badge.color).toContain('gray');
  });
});

describe('getScoreColorClass', () => {
  it('should return green for very high scores', () => {
    expect(getScoreColorClass(7)).toContain('green');
    expect(getScoreColorClass(10)).toContain('green');
  });

  it('should return lime for high scores', () => {
    expect(getScoreColorClass(4)).toContain('lime');
    expect(getScoreColorClass(6)).toContain('lime');
  });

  it('should return yellow for moderate scores', () => {
    expect(getScoreColorClass(1)).toContain('yellow');
    expect(getScoreColorClass(3)).toContain('yellow');
  });

  it('should return gray for neutral scores', () => {
    expect(getScoreColorClass(0)).toContain('gray');
    expect(getScoreColorClass(-2)).toContain('gray');
  });

  it('should return orange for negative scores', () => {
    expect(getScoreColorClass(-4)).toContain('orange');
    expect(getScoreColorClass(-5)).toContain('orange');
  });

  it('should return red for very negative scores', () => {
    expect(getScoreColorClass(-7)).toContain('red');
    expect(getScoreColorClass(-10)).toContain('red');
  });
});

describe('getScoreBadgeColor', () => {
  it('should return appropriate badge colors', () => {
    expect(getScoreBadgeColor(8)).toContain('green');
    expect(getScoreBadgeColor(5)).toContain('lime');
    expect(getScoreBadgeColor(2)).toContain('yellow');
    expect(getScoreBadgeColor(0)).toContain('gray');
    expect(getScoreBadgeColor(-4)).toContain('orange');
    expect(getScoreBadgeColor(-8)).toContain('red');
  });
});

describe('getClassificationLabel', () => {
  it('should return Portuguese labels', () => {
    expect(getClassificationLabel('very_strong')).toBe('Muito Forte');
    expect(getClassificationLabel('strong')).toBe('Forte');
    expect(getClassificationLabel('moderate')).toBe('Moderado');
    expect(getClassificationLabel('weak')).toBe('Fraco');
    expect(getClassificationLabel('very_weak')).toBe('Muito Fraco');
    expect(getClassificationLabel('peregrine')).toBe('Peregrino');
  });

  it('should return original value for unknown classification', () => {
    expect(getClassificationLabel('unknown')).toBe('unknown');
  });
});

describe('getDignityDetails', () => {
  it('should return empty array for no dignities', () => {
    expect(getDignityDetails(undefined)).toEqual([]);
  });

  it('should return details for ruler', () => {
    const dignities: Dignities = {
      is_ruler: true,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 5,
      classification: 'strong',
    };
    const details = getDignityDetails(dignities);
    expect(details).toHaveLength(1);
    expect(details[0]).toEqual({ icon: '👑', label: 'Domicílio', points: 5 });
  });

  it('should return multiple details', () => {
    const dignities: Dignities = {
      is_ruler: true,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: 'day',
      term_ruler: 'Mars',
      face_ruler: 'Venus',
      score: 11,
      classification: 'very_strong',
    };
    const details = getDignityDetails(dignities);
    expect(details).toHaveLength(4);
    expect(details[0].label).toBe('Domicílio');
    expect(details[1].label).toContain('Triplicidade');
    expect(details[2].label).toBe('Termo: Mars');
    expect(details[3].label).toBe('Face: Venus');
  });
});

describe('isClassicalPlanet', () => {
  it('should identify classical planets', () => {
    expect(isClassicalPlanet('Sun')).toBe(true);
    expect(isClassicalPlanet('Moon')).toBe(true);
    expect(isClassicalPlanet('Mercury')).toBe(true);
    expect(isClassicalPlanet('Venus')).toBe(true);
    expect(isClassicalPlanet('Mars')).toBe(true);
    expect(isClassicalPlanet('Jupiter')).toBe(true);
    expect(isClassicalPlanet('Saturn')).toBe(true);
  });

  it('should not identify modern planets as classical', () => {
    expect(isClassicalPlanet('Uranus')).toBe(false);
    expect(isClassicalPlanet('Neptune')).toBe(false);
    expect(isClassicalPlanet('Pluto')).toBe(false);
  });
});

describe('getDignityExplanation', () => {
  it('should return ruler explanation', () => {
    const dignities: Dignities = {
      is_ruler: true,
      is_exalted: false,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 5,
      classification: 'strong',
    };
    const explanation = getDignityExplanation(dignities, 'Sun', 'Leo');
    expect(explanation).toContain('domicílio');
    expect(explanation).toContain('Sun');
    expect(explanation).toContain('Leo');
  });

  it('should return exaltation explanation', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: true,
      is_detriment: false,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: 4,
      classification: 'strong',
    };
    const explanation = getDignityExplanation(dignities, 'Sun', 'Aries');
    expect(explanation).toContain('exaltado');
  });

  it('should return fall explanation', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: false,
      is_fall: true,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: -4,
      classification: 'weak',
    };
    const explanation = getDignityExplanation(dignities, 'Sun', 'Libra');
    expect(explanation).toContain('queda');
  });

  it('should return detriment explanation', () => {
    const dignities: Dignities = {
      is_ruler: false,
      is_exalted: false,
      is_detriment: true,
      is_fall: false,
      triplicity_ruler: null,
      term_ruler: null,
      face_ruler: null,
      score: -5,
      classification: 'weak',
    };
    const explanation = getDignityExplanation(dignities, 'Sun', 'Aquarius');
    expect(explanation).toContain('detrimento');
  });

  it('should return default message for missing params', () => {
    const explanation = getDignityExplanation(undefined, undefined, undefined);
    expect(explanation).toContain('Sem informações');
  });
});
