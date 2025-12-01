/**
 * Solar Phase component - displays Sun phase at birth
 *
 * The API returns already-localized data based on the `lang` query parameter,
 * so no frontend language switching is needed - just display the values directly.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface SolarPhaseData {
  phase_number: number;
  phase_name: string;
  temperament: string;
  temperament_key: string;
  qualities: string;
  signs: string[];
  description: string;
}

interface SolarPhaseProps {
  solarPhase: SolarPhaseData;
}

// Temperament emoji mapping (uses English keys for internal lookup)
const temperamentEmoji: Record<string, string> = {
  Sanguine: '🌬️',
  Choleric: '🔥',
  Melancholic: '🌍',
  Phlegmatic: '💧',
};

// Color classes for each temperament (uses English keys)
const temperamentColors: Record<string, string> = {
  Sanguine: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
  Choleric: 'from-red-500/10 to-orange-500/10 border-red-500/20',
  Melancholic: 'from-purple-500/10 to-indigo-500/10 border-purple-500/20',
  Phlegmatic: 'from-teal-500/10 to-green-500/10 border-teal-500/20',
};

export function SolarPhase({ solarPhase }: SolarPhaseProps) {
  const { t } = useTranslation();

  // Use temperament_key for emoji/color lookup (always English), fall back to temperament for legacy
  const temperamentKey = solarPhase.temperament_key || solarPhase.temperament;
  const emoji = temperamentEmoji[temperamentKey] || '☀️';
  const colorClass =
    temperamentColors[temperamentKey] || 'from-yellow-500/10 to-orange-500/10 border-yellow-500/20';

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={solarPhase.temperament}>
            {emoji}
          </span>
          <div>
            <div className="text-lg font-semibold text-foreground">
              {solarPhase.phase_name} - {solarPhase.temperament}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Phase Details */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.solarPhase.qualities', { defaultValue: 'Qualities' })}
            </p>
            <p className="text-sm font-semibold text-foreground">{solarPhase.qualities}</p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.solarPhase.phaseSigns', { defaultValue: 'Phase Signs' })}
            </p>
            <div className="flex flex-wrap gap-1">
              {solarPhase.signs.map((sign, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {sign}
                </Badge>
              ))}
            </div>
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.solarPhase.interpretation', { defaultValue: 'Interpretation' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">{solarPhase.description}</p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            💡{' '}
            {t('components.solarPhase.note', {
              defaultValue:
                'The solar phase at birth is based on the Sun sign and reveals your fundamental temperament and primary personality qualities according to traditional astrology.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
