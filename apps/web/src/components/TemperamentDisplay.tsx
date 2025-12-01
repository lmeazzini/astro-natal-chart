/**
 * Temperament Display component - shows dominant temperament based on 5 traditional factors
 *
 * The API returns already-localized data based on the `lang` query parameter,
 * so no frontend language switching is needed - just display the values directly.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface TemperamentScores {
  hot: number;
  cold: number;
  wet: number;
  dry: number;
}

export interface TemperamentFactor {
  factor: string;
  value: string;
  qualities: string[];
  weight?: number; // Dignity-based weight (0.5-2.0)
  dignity?: string | null; // Dignity name for display
}

export interface TemperamentData {
  dominant: string;
  dominant_key: string; // English key for internal lookup (e.g., "choleric")
  element: string;
  element_key: string; // English key for internal lookup (e.g., "fire")
  icon: string;
  scores: TemperamentScores;
  factors: TemperamentFactor[];
  description: string;
}

interface TemperamentDisplayProps {
  temperament: TemperamentData;
}

// Temperament colors (uses English keys for internal lookup)
const temperamentColors: Record<string, string> = {
  choleric: 'from-red-500/10 to-orange-500/10 border-red-500/20',
  sanguine: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
  melancholic: 'from-purple-500/10 to-gray-500/10 border-purple-500/20',
  phlegmatic: 'from-teal-500/10 to-green-500/10 border-teal-500/20',
};

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

// Dignity colors for display (labels are now provided by the API)
const dignityColors: Record<string, string> = {
  domicile: 'bg-green-500/20 text-green-700 dark:text-green-400',
  exaltation: 'bg-blue-500/20 text-blue-700 dark:text-blue-400',
  triplicity: 'bg-cyan-500/20 text-cyan-700 dark:text-cyan-400',
  term: 'bg-purple-500/20 text-purple-700 dark:text-purple-400',
  face: 'bg-indigo-500/20 text-indigo-700 dark:text-indigo-400',
  peregrine: 'bg-gray-500/20 text-gray-700 dark:text-gray-400',
  detriment: 'bg-orange-500/20 text-orange-700 dark:text-orange-400',
  fall: 'bg-red-500/20 text-red-700 dark:text-red-400',
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
  const { t } = useTranslation();

  // Use dominant_key for color lookup (always English), fall back to dominant for legacy
  const dominantKey = temperament.dominant_key || temperament.dominant;
  const colorClass =
    temperamentColors[dominantKey] || 'from-gray-500/10 to-gray-500/10 border-gray-500/20';

  // Calculate dynamic max value based on actual scores
  // With weights, max theoretical is 14 (3 fixed factors @ 1.0 + 2 weighted @ 2.0 each = 7 per quality axis)
  // But we use actual sum for better visualization
  const totalScores =
    temperament.scores.hot +
    temperament.scores.cold +
    temperament.scores.wet +
    temperament.scores.dry;
  const maxQualityValue = Math.max(totalScores / 2, 10); // At least 10 for backward compatibility

  // Get dignity color class
  const getDignityColor = (dignity: string | null | undefined): string | null => {
    if (!dignity) return null;
    return dignityColors[dignity] || null;
  };

  // Quality labels - API now provides translated labels via factor data
  const getQualityLabel = (quality: string) => {
    const labels: Record<string, string> = {
      hot: t('components.temperament.hot', { defaultValue: 'Hot' }),
      cold: t('components.temperament.cold', { defaultValue: 'Cold' }),
      wet: t('components.temperament.wet', { defaultValue: 'Wet' }),
      dry: t('components.temperament.dry', { defaultValue: 'Dry' }),
    };
    return labels[quality] || quality;
  };

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={temperament.dominant}>
            {temperament.icon}
          </span>
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground">
              {t('components.temperament.title', { defaultValue: 'Temperament' })}:{' '}
              {temperament.dominant}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.temperament.element', { defaultValue: 'Element' })}{' '}
              {temperament.element} •{' '}
              {t('components.temperament.basedOn', {
                defaultValue: 'Based on 5 traditional factors',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Quality Scores */}
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.temperament.qualityScores', { defaultValue: 'Quality Scores' })}
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
              defaultValue: 'Contributing Factors',
            })}
          </p>
          <div className="space-y-2">
            {temperament.factors.map((factor, index) => {
              const dignityColor = getDignityColor(factor.dignity);
              const hasWeight = factor.weight !== undefined && factor.weight !== 1.0;

              return (
                <div
                  key={index}
                  className="flex items-start justify-between p-3 rounded-md bg-card/50 border border-border/50"
                >
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-semibold text-foreground">{factor.factor}</p>
                      {hasWeight && (
                        <span
                          className={`text-xs font-mono px-1.5 py-0.5 rounded ${
                            factor.weight && factor.weight > 1
                              ? 'bg-green-500/20 text-green-700 dark:text-green-400'
                              : 'bg-red-500/20 text-red-700 dark:text-red-400'
                          }`}
                          title={t('components.temperament.weightTooltip', {
                            defaultValue: 'Weight based on planetary dignity',
                          })}
                        >
                          ×{factor.weight?.toFixed(2)}
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">{factor.value}</p>
                    {factor.dignity && dignityColor && (
                      <span
                        className={`inline-block text-xs px-2 py-0.5 rounded-full ${dignityColor}`}
                      >
                        {factor.dignity}
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
            {t('components.temperament.interpretation', { defaultValue: 'Interpretation' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">{temperament.description}</p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border space-y-2">
          <p className="text-xs text-muted-foreground">
            ⚖️{' '}
            {t('components.temperament.note', {
              defaultValue:
                'Temperament is determined by the sum of elemental qualities (Hot, Cold, Wet, Dry) from 5 natal chart factors: Ascendant, Ascendant Ruler, Solar Quadrant, Lunar Phase, and Lord of the Nativity, following medieval astrological tradition.',
            })}
          </p>
          <p className="text-xs text-muted-foreground">
            📊{' '}
            {t('components.temperament.weightNote', {
              defaultValue:
                'Planetary factors (Ascendant Ruler and Lord of the Nativity) have their weights adjusted by essential dignity: dignified planets (domicile, exaltation) contribute more, while debilitated planets (detriment, fall) contribute less.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
