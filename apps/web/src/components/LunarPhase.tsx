/**
 * Lunar Phase component - displays Moon phase at birth
 *
 * The API returns already-localized data based on the `lang` query parameter,
 * so no frontend language switching is needed - just display the values directly.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface LunarPhaseData {
  phase_key: string;
  phase_name: string;
  angle: number;
  illumination_percentage: number;
  emoji: string;
  keywords: string;
  interpretation: string;
}

interface LunarPhaseProps {
  lunarPhase: LunarPhaseData;
}

export function LunarPhase({ lunarPhase }: LunarPhaseProps) {
  const { t } = useTranslation();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={lunarPhase.phase_name}>
            {lunarPhase.emoji}
          </span>
          <div>
            <div className="text-lg font-semibold text-foreground">{lunarPhase.phase_name}</div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Phase Details */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.lunarPhase.sunMoonAngle', { defaultValue: 'Sun-Moon Angle' })}
            </p>
            <p className="text-sm font-semibold text-foreground">{lunarPhase.angle.toFixed(1)}°</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.lunarPhase.illumination', { defaultValue: 'Illumination' })}
            </p>
            <p className="text-sm font-semibold text-foreground">
              {lunarPhase.illumination_percentage.toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Keywords */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.lunarPhase.characteristics', { defaultValue: 'Characteristics' })}
          </p>
          <div className="flex flex-wrap gap-2">
            {lunarPhase.keywords.split(',').map((keyword, index) => (
              <Badge key={index} variant="secondary" className="text-xs">
                {keyword.trim()}
              </Badge>
            ))}
          </div>
        </div>

        {/* Interpretation */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.lunarPhase.interpretation', { defaultValue: 'Interpretation' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {lunarPhase.interpretation}
          </p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            💡{' '}
            {t('components.lunarPhase.note', {
              defaultValue:
                'The lunar phase at birth reveals patterns about temperament, life cycle, and how you process emotional experiences.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
