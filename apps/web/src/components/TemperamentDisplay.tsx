/**
 * Temperament Display component - shows dominant temperament based on 5 traditional factors
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';

export interface TemperamentScores {
  hot: number;
  cold: number;
  wet: number;
  dry: number;
}

export interface TemperamentFactor {
  factor: string;
  factor_pt: string;
  value: string;
  value_pt?: string;
  qualities: string[];
  weight?: number; // Dignity-based weight (0.5-2.0)
  dignity?: string | null; // Dignity name for display
}

export interface TemperamentData {
  dominant: string;
  dominant_pt: string;
  element: string;
  element_pt: string;
  icon: string;
  scores: TemperamentScores;
  factors: TemperamentFactor[];
  description: string;
}

interface TemperamentDisplayProps {
  temperament: TemperamentData;
}

// Temperament colors
const temperamentColors: Record<string, string> = {
  choleric: 'from-red-500/10 to-orange-500/10 border-red-500/20',
  sanguine: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
  melancholic: 'from-purple-500/10 to-gray-500/10 border-purple-500/20',
  phlegmatic: 'from-teal-500/10 to-green-500/10 border-teal-500/20',
};

// Quality labels are now translated dynamically using i18next
// See lines 177-180 where getQualityLabels() is defined

// Quality colors
const qualityColors: Record<string, string> = {
  hot: 'bg-red-500',
  cold: 'bg-blue-500',
  wet: 'bg-cyan-500',
  dry: 'bg-orange-500',
};

// Quality icons
const qualityIcons: Record<string, string> = {
  hot: '🔥',
  cold: '❄️',
  wet: '💧',
  dry: '🌵',
};

// Dignity labels for display
const dignityLabels: Record<string, { en: string; pt: string; color: string }> = {
  domicile: {
    en: 'Domicile',
    pt: 'Domicílio',
    color: 'bg-green-500/20 text-green-700 dark:text-green-400',
  },
  exaltation: {
    en: 'Exaltation',
    pt: 'Exaltação',
    color: 'bg-blue-500/20 text-blue-700 dark:text-blue-400',
  },
  triplicity: {
    en: 'Triplicity',
    pt: 'Triplicidade',
    color: 'bg-cyan-500/20 text-cyan-700 dark:text-cyan-400',
  },
  term: { en: 'Term', pt: 'Termo', color: 'bg-purple-500/20 text-purple-700 dark:text-purple-400' },
  face: { en: 'Face', pt: 'Face', color: 'bg-indigo-500/20 text-indigo-700 dark:text-indigo-400' },
  peregrine: {
    en: 'Peregrine',
    pt: 'Peregrino',
    color: 'bg-gray-500/20 text-gray-700 dark:text-gray-400',
  },
  detriment: {
    en: 'Detriment',
    pt: 'Detrimento',
    color: 'bg-orange-500/20 text-orange-700 dark:text-orange-400',
  },
  fall: { en: 'Fall', pt: 'Queda', color: 'bg-red-500/20 text-red-700 dark:text-red-400' },
};

interface QualityBarProps {
  quality: string;
  label: string;
  value: number;
  maxValue: number;
}

function QualityBar({ quality, label, value, maxValue }: QualityBarProps) {
  const percentage = Math.min((value / maxValue) * 100, 100);
  const color = qualityColors[quality] || 'bg-gray-500';
  const icon = qualityIcons[quality] || '';

  // Format value: show decimal only if not a whole number
  const formattedValue = Number.isInteger(value) ? value : value.toFixed(1);
  const formattedMax = Number.isInteger(maxValue) ? maxValue : maxValue.toFixed(1);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-foreground font-medium flex items-center gap-1">
          <span>{icon}</span>
          {label}
        </span>
        <span className="text-muted-foreground font-mono text-xs">
          {formattedValue}/{formattedMax}
        </span>
      </div>
      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
        <div
          className={`h-full ${color} transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function TemperamentDisplay({ temperament }: TemperamentDisplayProps) {
  const { t, i18n } = useTranslation();
  const { translatePlanet, translateSign, translateLunarPhase } = useAstroTranslation();
  const isEn = i18n.language === 'en-US' || i18n.language === 'en';

  const colorClass =
    temperamentColors[temperament.dominant] || 'from-gray-500/10 to-gray-500/10 border-gray-500/20';

  // Calculate dynamic max value based on actual scores
  // With weights, max theoretical is 14 (3 fixed factors @ 1.0 + 2 weighted @ 2.0 each = 7 per quality axis)
  // But we use actual sum for better visualization
  const totalScores =
    temperament.scores.hot +
    temperament.scores.cold +
    temperament.scores.wet +
    temperament.scores.dry;
  const maxQualityValue = Math.max(totalScores / 2, 10); // At least 10 for backward compatibility

  // Get dignity label
  const getDignityLabel = (
    dignity: string | null | undefined
  ): { label: string; color: string } | null => {
    if (!dignity) return null;
    const dignityInfo = dignityLabels[dignity];
    if (!dignityInfo) return null;
    return {
      label: isEn ? dignityInfo.en : dignityInfo.pt,
      color: dignityInfo.color,
    };
  };

  // Translated quality labels
  const getQualityLabel = (quality: string) => {
    const labels: Record<string, string> = {
      hot: t('components.temperament.hot', { defaultValue: 'Quente' }),
      cold: t('components.temperament.cold', { defaultValue: 'Frio' }),
      wet: t('components.temperament.wet', { defaultValue: 'Úmido' }),
      dry: t('components.temperament.dry', { defaultValue: 'Seco' }),
    };
    return labels[quality] || quality;
  };

  // Translate factor value (planets, signs, phases, or composite strings)
  const translateFactorValue = (value: string): string => {
    // Handle composite strings like "Jupiter in Scorpio" or "Moon in Cancer"
    const inPattern = / in /i;
    if (inPattern.test(value)) {
      const parts = value.split(inPattern);
      if (parts.length === 2) {
        const translatedPlanet = translatePlanet(parts[0].trim());
        const translatedSign = translateSign(parts[1].trim());
        return `${translatedPlanet} em ${translatedSign}`;
      }
    }

    // Try to translate as planet first
    const translatedPlanet = translatePlanet(value);
    if (translatedPlanet !== value) return translatedPlanet;

    // Try to translate as sign
    const translatedSign = translateSign(value);
    if (translatedSign !== value) return translatedSign;

    // Try to translate as lunar phase
    const translatedPhase = translateLunarPhase(value);
    if (translatedPhase !== value) return translatedPhase;

    // Return original if no translation found
    return value;
  };

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={temperament.dominant_pt}>
            {temperament.icon}
          </span>
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground">
              {t('components.temperament.title', { defaultValue: 'Temperamento' })}:{' '}
              {isEn ? temperament.dominant : temperament.dominant_pt}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.temperament.element', { defaultValue: 'Elemento' })}{' '}
              {isEn ? temperament.element : temperament.element_pt} •{' '}
              {t('components.temperament.basedOn', {
                defaultValue: 'Baseado em 5 fatores tradicionais',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Quality Scores */}
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.temperament.qualityScores', { defaultValue: 'Pontuação de Qualidades' })}
          </p>
          <div className="space-y-3">
            <QualityBar
              quality="hot"
              label={getQualityLabel('hot')}
              value={temperament.scores.hot}
              maxValue={maxQualityValue}
            />
            <QualityBar
              quality="cold"
              label={getQualityLabel('cold')}
              value={temperament.scores.cold}
              maxValue={maxQualityValue}
            />
            <QualityBar
              quality="wet"
              label={getQualityLabel('wet')}
              value={temperament.scores.wet}
              maxValue={maxQualityValue}
            />
            <QualityBar
              quality="dry"
              label={getQualityLabel('dry')}
              value={temperament.scores.dry}
              maxValue={maxQualityValue}
            />
          </div>
        </div>

        {/* Factors Breakdown */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.temperament.contributingFactors', {
              defaultValue: 'Fatores Contribuintes',
            })}
          </p>
          <div className="space-y-2">
            {temperament.factors.map((factor, index) => {
              const dignityInfo = getDignityLabel(factor.dignity);
              const hasWeight = factor.weight !== undefined && factor.weight !== 1.0;

              return (
                <div
                  key={index}
                  className="flex items-start justify-between p-3 rounded-md bg-card/50 border border-border/50"
                >
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-foreground">
                        {isEn ? factor.factor : factor.factor_pt}
                      </p>
                      {hasWeight && (
                        <span
                          className={`text-xs font-mono px-1.5 py-0.5 rounded ${
                            factor.weight && factor.weight > 1
                              ? 'bg-green-500/20 text-green-700 dark:text-green-400'
                              : 'bg-red-500/20 text-red-700 dark:text-red-400'
                          }`}
                          title={t('components.temperament.weightTooltip', {
                            defaultValue: 'Peso baseado na dignidade do planeta',
                          })}
                        >
                          ×{factor.weight?.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {isEn ? factor.value : translateFactorValue(factor.value)}
                    </p>
                    {dignityInfo && (
                      <span
                        className={`inline-block text-xs px-2 py-0.5 rounded-full ${dignityInfo.color}`}
                      >
                        {dignityInfo.label}
                      </span>
                    )}
                  </div>
                  <div className="flex gap-1 ml-2">
                    {factor.qualities.map((qual, qIndex) => (
                      <Badge
                        key={qIndex}
                        variant="secondary"
                        className="text-xs px-2"
                        title={getQualityLabel(qual)}
                      >
                        {qualityIcons[qual]}
                      </Badge>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.temperament.interpretation', { defaultValue: 'Interpretação' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">{temperament.description}</p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border space-y-2">
          <p className="text-xs text-muted-foreground">
            ⚖️{' '}
            {t('components.temperament.note', {
              defaultValue:
                'O temperamento é determinado pela soma das qualidades elementares (Quente, Frio, Úmido, Seco) de 5 fatores do mapa natal: Ascendente, Regente do Ascendente, Quadrante Solar, Fase Lunar e Senhor da Natividade, seguindo a tradição da astrologia medieval.',
            })}
          </p>
          <p className="text-xs text-muted-foreground">
            📊{' '}
            {t('components.temperament.weightNote', {
              defaultValue:
                'Os fatores planetários (Regente do Ascendente e Senhor da Natividade) têm seus pesos ajustados pela dignidade essencial: planetas dignificados (domicílio, exaltação) contribuem mais, enquanto planetas debilitados (detrimento, queda) contribuem menos.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
