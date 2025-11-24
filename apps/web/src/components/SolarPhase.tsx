/**
 * Solar Phase component - displays Sun phase at birth
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface SolarPhaseData {
  phase_number: number;
  phase_name: string;
  temperament: string;
  temperament_pt: string;
  qualities: string;
  qualities_pt: string;
  signs: string[];
  signs_pt: string[];
  description: string;
}

interface SolarPhaseProps {
  solarPhase: SolarPhaseData;
}

// Temperament emoji mapping
const temperamentEmoji: Record<string, string> = {
  Sanguine: '🌬️',
  Choleric: '🔥',
  Melancholic: '🌍',
  Phlegmatic: '💧',
};

// Color classes for each temperament
const temperamentColors: Record<string, string> = {
  Sanguine: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
  Choleric: 'from-red-500/10 to-orange-500/10 border-red-500/20',
  Melancholic: 'from-purple-500/10 to-indigo-500/10 border-purple-500/20',
  Phlegmatic: 'from-teal-500/10 to-green-500/10 border-teal-500/20',
};

export function SolarPhase({ solarPhase }: SolarPhaseProps) {
  const { t, i18n } = useTranslation();
  const isEn = i18n.language === 'en-US' || i18n.language === 'en';

  const emoji = temperamentEmoji[solarPhase.temperament] || '☀️';
  const colorClass = temperamentColors[solarPhase.temperament] || 'from-yellow-500/10 to-orange-500/10 border-yellow-500/20';

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={solarPhase.temperament_pt}>
            {emoji}
          </span>
          <div>
            <div className="text-lg font-semibold text-foreground">
              {solarPhase.phase_name} - {isEn ? solarPhase.temperament : solarPhase.temperament_pt}
            </div>
            <div className="text-xs text-muted-foreground font-normal">
              {isEn ? solarPhase.temperament_pt : solarPhase.temperament}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Phase Details */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.solarPhase.qualities', { defaultValue: 'Qualidades' })}
            </p>
            <p className="text-sm font-semibold text-foreground">
              {isEn ? solarPhase.qualities : solarPhase.qualities_pt}
            </p>
            <p className="text-xs text-muted-foreground">
              {isEn ? solarPhase.qualities_pt : solarPhase.qualities}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.solarPhase.phaseSigns', { defaultValue: 'Signos da Fase' })}
            </p>
            <div className="flex flex-wrap gap-1">
              {(isEn ? solarPhase.signs : solarPhase.signs_pt).map((sign, index) => (
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
            {t('components.solarPhase.interpretation', { defaultValue: 'Interpretação' })}
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {solarPhase.description}
          </p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            💡 {t('components.solarPhase.note', { defaultValue: 'A fase solar no nascimento está baseada no signo do Sol e revela o temperamento fundamental e as qualidades primárias da sua personalidade segundo a astrologia tradicional.' })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
