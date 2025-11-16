/**
 * Dignities utility functions
 *
 * Provides helper functions to work with essential dignities
 * in traditional astrology.
 */

export interface Dignities {
  is_ruler: boolean;
  is_exalted: boolean;
  is_detriment: boolean;
  is_fall: boolean;
  triplicity_ruler: 'day' | 'night' | null;
  term_ruler: string | null;
  face_ruler: string | null;
  score: number;
  classification: 'very_strong' | 'strong' | 'moderate' | 'weak' | 'very_weak' | 'peregrine';
}

export interface DignityBadge {
  icon: string;
  label: string;
  color: string;
}

/**
 * Get the total dignity score for a planet
 */
export function getDignityScore(dignities?: Dignities): number {
  if (!dignities) return 0;
  return dignities.score;
}

/**
 * Get badge information based on dignities
 */
export function getDignityBadge(dignities?: Dignities): DignityBadge {
  if (!dignities) {
    return {
      icon: '🚶',
      label: 'Peregrino',
      color: 'bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600'
    };
  }

  // Priority order: Ruler > Exalted > Fall > Detriment > Triplicity > Term > Face
  if (dignities.is_ruler) {
    return {
      icon: '👑',
      label: 'Domicílio',
      color: 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200 dark:border-green-700'
    };
  }

  if (dignities.is_exalted) {
    return {
      icon: '🌟',
      label: 'Exaltação',
      color: 'bg-lime-100 text-lime-800 border-lime-300 dark:bg-lime-900 dark:text-lime-200 dark:border-lime-700'
    };
  }

  if (dignities.is_fall) {
    return {
      icon: '⬇️',
      label: 'Queda',
      color: 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200 dark:border-red-700'
    };
  }

  if (dignities.is_detriment) {
    return {
      icon: '⚠️',
      label: 'Detrimento',
      color: 'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900 dark:text-orange-200 dark:border-orange-700'
    };
  }

  if (dignities.triplicity_ruler) {
    const icon = dignities.triplicity_ruler === 'day' ? '🔥' : '🌙';
    return {
      icon,
      label: 'Triplicidade',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-700'
    };
  }

  if (dignities.term_ruler) {
    return {
      icon: '📊',
      label: 'Termo',
      color: 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900 dark:text-blue-200 dark:border-blue-700'
    };
  }

  if (dignities.face_ruler) {
    return {
      icon: '👤',
      label: 'Face',
      color: 'bg-purple-100 text-purple-800 border-purple-300 dark:bg-purple-900 dark:text-purple-200 dark:border-purple-700'
    };
  }

  // Peregrine (no dignities or debilities)
  return {
    icon: '🚶',
    label: 'Peregrino',
    color: 'bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600'
  };
}

/**
 * Get text color class based on dignity score
 */
export function getScoreColorClass(score: number): string {
  if (score >= 7) return 'text-green-700 dark:text-green-400';
  if (score >= 4) return 'text-lime-700 dark:text-lime-400';
  if (score >= 1) return 'text-yellow-700 dark:text-yellow-400';
  if (score >= -3) return 'text-gray-700 dark:text-gray-400';
  if (score >= -6) return 'text-orange-700 dark:text-orange-400';
  return 'text-red-700 dark:text-red-400';
}

/**
 * Get badge color class based on dignity score
 */
export function getScoreBadgeColor(score: number): string {
  if (score >= 7) return 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200 dark:border-green-700';
  if (score >= 4) return 'bg-lime-100 text-lime-800 border-lime-300 dark:bg-lime-900 dark:text-lime-200 dark:border-lime-700';
  if (score >= 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200 dark:border-yellow-700';
  if (score >= -3) return 'bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-200 dark:border-gray-600';
  if (score >= -6) return 'bg-orange-100 text-orange-800 border-orange-300 dark:bg-orange-900 dark:text-orange-200 dark:border-orange-700';
  return 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200 dark:border-red-700';
}

/**
 * Get classification label in Portuguese
 */
export function getClassificationLabel(classification: string): string {
  const labels: Record<string, string> = {
    'very_strong': 'Muito Forte',
    'strong': 'Forte',
    'moderate': 'Moderado',
    'weak': 'Fraco',
    'very_weak': 'Muito Fraco',
    'peregrine': 'Peregrino'
  };
  return labels[classification] || classification;
}

/**
 * Get all dignity details as a list
 */
export function getDignityDetails(dignities?: Dignities): Array<{ icon: string; label: string; points: number }> {
  if (!dignities) return [];

  const details: Array<{ icon: string; label: string; points: number }> = [];

  if (dignities.is_ruler) {
    details.push({ icon: '👑', label: 'Domicílio', points: 5 });
  }

  if (dignities.is_exalted) {
    details.push({ icon: '🌟', label: 'Exaltação', points: 4 });
  }

  if (dignities.is_detriment) {
    details.push({ icon: '⚠️', label: 'Detrimento', points: -5 });
  }

  if (dignities.is_fall) {
    details.push({ icon: '⬇️', label: 'Queda', points: -4 });
  }

  if (dignities.triplicity_ruler) {
    const icon = dignities.triplicity_ruler === 'day' ? '🔥' : '🌙';
    details.push({ icon, label: `Triplicidade (${dignities.triplicity_ruler})`, points: 3 });
  }

  if (dignities.term_ruler) {
    details.push({ icon: '📊', label: `Termo: ${dignities.term_ruler}`, points: 2 });
  }

  if (dignities.face_ruler) {
    details.push({ icon: '👤', label: `Face: ${dignities.face_ruler}`, points: 1 });
  }

  return details;
}

/**
 * Check if planet is classical (has dignities)
 */
export function isClassicalPlanet(planetName: string): boolean {
  const classicalPlanets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'];
  return classicalPlanets.includes(planetName);
}

/**
 * Get dignity explanation text
 */
export function getDignityExplanation(dignities?: Dignities, planetName?: string, sign?: string): string {
  if (!dignities || !planetName || !sign) {
    return 'Sem informações de dignidades disponíveis.';
  }

  if (dignities.is_ruler) {
    return `${planetName} está em domicílio em ${sign}, manifestando suas qualidades naturais com força total.`;
  }

  if (dignities.is_exalted) {
    return `${planetName} está exaltado em ${sign}, manifestando suas melhores qualidades de forma harmoniosa.`;
  }

  if (dignities.is_fall) {
    return `${planetName} está em queda em ${sign}, suas qualidades estão debilitadas e podem manifestar-se de forma desafiadora.`;
  }

  if (dignities.is_detriment) {
    return `${planetName} está em detrimento em ${sign}, encontrando dificuldades para expressar suas qualidades naturais.`;
  }

  if (dignities.score > 0) {
    return `${planetName} possui dignidades menores em ${sign}, tendo alguma força apesar de não estar em domicílio ou exaltação.`;
  }

  if (dignities.score === 0) {
    return `${planetName} está peregrino em ${sign}, sem dignidades essenciais significativas.`;
  }

  return `${planetName} está debilitado em ${sign}.`;
}
