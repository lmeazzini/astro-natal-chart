/**
 * Mentality Display component - shows intellectual analysis based on Mercury and mental houses
 *
 * Unlike Temperament (physical/emotional constitution), Mentality analyzes:
 * - Thinking speed and style
 * - Intellectual depth
 * - Mental versatility
 * - Abstract vs. concrete thinking
 *
 * The API returns already-localized data based on the `lang` query parameter.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface MentalityScores {
  strength: number;
  speed: number;
  depth: number;
  versatility: number;
}

export interface MentalityFactor {
  factor_key: string;
  factor: string;
  value: string;
  contribution: string;
}

export interface MercuryAnalysis {
  sign: string;
  sign_localized: string;
  house: number;
  retrograde: boolean;
  dignities: string[];
}

export interface MentalityData {
  type_key: string;
  type: string;
  icon: string;
  scores: MentalityScores;
  mercury_analysis: MercuryAnalysis | null;
  factors: MentalityFactor[];
  description: string;
}

interface MentalityCardProps {
  mentality: MentalityData;
}

// Mentality type colors (gradient backgrounds)
const mentalityColors: Record<string, string> = {
  agile_and_superficial: 'from-yellow-500/10 to-amber-500/10 border-yellow-500/20',
  agile_and_deep: 'from-emerald-500/10 to-cyan-500/10 border-emerald-500/20',
  slow_and_deep: 'from-indigo-500/10 to-purple-500/10 border-indigo-500/20',
  slow_and_superficial: 'from-gray-500/10 to-slate-500/10 border-gray-500/20',
  versatile: 'from-blue-500/10 to-sky-500/10 border-blue-500/20',
  specialized: 'from-rose-500/10 to-pink-500/10 border-rose-500/20',
  abstract: 'from-violet-500/10 to-purple-500/10 border-violet-500/20',
  concrete: 'from-orange-500/10 to-amber-500/10 border-orange-500/20',
  unknown: 'from-gray-500/10 to-gray-500/10 border-gray-500/20',
};

// Score bar colors
const scoreColors: Record<string, string> = {
  strength: 'bg-emerald-500',
  speed: 'bg-amber-500',
  depth: 'bg-indigo-500',
  versatility: 'bg-cyan-500',
};

// Score icons
const scoreIcons: Record<string, string> = {
  strength: '💪',
  speed: '⚡',
  depth: '🔍',
  versatility: '🔄',
};

interface ScoreBarProps {
  scoreKey: string;
  label: string;
  value: number;
  minValue: number;
  maxValue: number;
}

function ScoreBar({ scoreKey, label, value, minValue, maxValue }: ScoreBarProps) {
  const range = maxValue - minValue;
  const normalizedValue = value - minValue;
  const percentage = Math.max(0, Math.min((normalizedValue / range) * 100, 100));
  const color = scoreColors[scoreKey] || 'bg-gray-500';
  const icon = scoreIcons[scoreKey] || '';

  // Format value
  const formattedValue = Number.isInteger(value) ? value : value.toFixed(1);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-foreground font-medium flex items-center gap-1">
          <span>{icon}</span>
          {label}
        </span>
        <span className="text-muted-foreground font-mono text-xs">{formattedValue}</span>
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

export function MentalityCard({ mentality }: MentalityCardProps) {
  const { t } = useTranslation();

  const colorClass = mentalityColors[mentality.type_key] || mentalityColors.unknown;

  // Get score labels
  const getScoreLabel = (key: string) => {
    const labels: Record<string, string> = {
      strength: t('components.mentality.strength', { defaultValue: 'Strength' }),
      speed: t('components.mentality.speed', { defaultValue: 'Speed' }),
      depth: t('components.mentality.depth', { defaultValue: 'Depth' }),
      versatility: t('components.mentality.versatility', { defaultValue: 'Versatility' }),
    };
    return labels[key] || key;
  };

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={mentality.type}>
            {mentality.icon}
          </span>
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground">
              {t('components.mentality.title', { defaultValue: 'Mentality' })}: {mentality.type}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.mentality.subtitle', {
                defaultValue: 'Intellectual style based on Mercury analysis',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Mental Scores */}
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.mentality.mentalScores', { defaultValue: 'Mental Scores' })}
          </p>
          <div className="space-y-3">
            <ScoreBar
              scoreKey="strength"
              label={getScoreLabel('strength')}
              value={mentality.scores.strength}
              minValue={0}
              maxValue={100}
            />
            <ScoreBar
              scoreKey="speed"
              label={getScoreLabel('speed')}
              value={mentality.scores.speed}
              minValue={-15}
              maxValue={20}
            />
            <ScoreBar
              scoreKey="depth"
              label={getScoreLabel('depth')}
              value={mentality.scores.depth}
              minValue={0}
              maxValue={25}
            />
            <ScoreBar
              scoreKey="versatility"
              label={getScoreLabel('versatility')}
              value={mentality.scores.versatility}
              minValue={0}
              maxValue={20}
            />
          </div>
        </div>

        {/* Mercury Analysis */}
        {mentality.mercury_analysis && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
              {t('components.mentality.mercuryAnalysis', { defaultValue: 'Mercury Analysis' })}
            </p>
            <div className="p-3 rounded-md bg-card/50 border border-border/50">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">☿</span>
                <div>
                  <p className="text-sm font-semibold text-foreground">
                    {t('components.mentality.mercuryIn', { defaultValue: 'Mercury in' })}{' '}
                    {mentality.mercury_analysis.sign_localized}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {t('components.mentality.house', { defaultValue: 'House' })}{' '}
                    {mentality.mercury_analysis.house}
                    {mentality.mercury_analysis.retrograde && (
                      <span className="ml-2 text-orange-500">
                        ℞ {t('components.mentality.retrograde', { defaultValue: 'Retrograde' })}
                      </span>
                    )}
                  </p>
                </div>
              </div>
              {mentality.mercury_analysis.dignities.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {mentality.mercury_analysis.dignities.map((dignity, index) => (
                    <Badge key={index} variant="secondary" className="text-xs capitalize">
                      {dignity}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Contributing Factors */}
        {mentality.factors.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
              {t('components.mentality.contributingFactors', {
                defaultValue: 'Contributing Factors',
              })}
            </p>
            <div className="space-y-2">
              {mentality.factors.map((factor, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 rounded-md bg-card/50 border border-border/50"
                >
                  <div className="flex-1">
                    <p className="text-sm font-medium text-foreground">{factor.factor}</p>
                    <p className="text-xs text-muted-foreground">{factor.value}</p>
                  </div>
                  <Badge
                    variant={factor.contribution.startsWith('-') ? 'destructive' : 'default'}
                    className="text-xs font-mono ml-2"
                  >
                    {factor.contribution}
                  </Badge>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            {t('components.mentality.interpretation', { defaultValue: 'Interpretation' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">{mentality.description}</p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border space-y-2">
          <p className="text-xs text-muted-foreground">
            🧠{' '}
            {t('components.mentality.note', {
              defaultValue:
                "Mentality differs from Temperament. While Temperament describes physical/emotional constitution, Mentality analyzes intellectual capacity, thinking style, and communication patterns based primarily on Mercury's position, dignities, and aspects.",
            })}
          </p>
          <p className="text-xs text-muted-foreground">
            📊{' '}
            {t('components.mentality.scoreNote', {
              defaultValue:
                'Scores range from: Strength (0-100), Speed (-15 to +20), Depth (0-25), Versatility (0-20). Positive speed indicates quick thinking; negative speed indicates reflective thinking.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
