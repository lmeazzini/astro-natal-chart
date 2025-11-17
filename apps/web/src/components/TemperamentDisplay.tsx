/**
 * Temperament Display component - shows dominant temperament based on 5 traditional factors
 */

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
  factor_pt: string;
  value: string;
  value_pt?: string;
  qualities: string[];
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

// Quality labels in Portuguese
const qualityLabels: Record<string, string> = {
  hot: 'Quente',
  cold: 'Frio',
  wet: 'Úmido',
  dry: 'Seco',
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

interface QualityBarProps {
  quality: string;
  value: number;
  maxValue: number;
}

function QualityBar({ quality, value, maxValue }: QualityBarProps) {
  const percentage = (value / maxValue) * 100;
  const color = qualityColors[quality] || 'bg-gray-500';
  const label = qualityLabels[quality] || quality;
  const icon = qualityIcons[quality] || '';

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="text-foreground font-medium flex items-center gap-1">
          <span>{icon}</span>
          {label}
        </span>
        <span className="text-muted-foreground font-mono text-xs">
          {value}/{maxValue}
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
  const colorClass = temperamentColors[temperament.dominant] ||
    'from-gray-500/10 to-gray-500/10 border-gray-500/20';

  // Max value is 10 (5 factors x 2 qualities each)
  const maxQualityValue = 10;

  return (
    <Card className={`bg-gradient-to-br ${colorClass}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={temperament.dominant_pt}>
            {temperament.icon}
          </span>
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground">
              Temperamento: {temperament.dominant_pt}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              Elemento {temperament.element_pt} • Baseado em 5 fatores tradicionais
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Quality Scores */}
        <div className="space-y-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            Pontuação de Qualidades
          </p>
          <div className="space-y-3">
            <QualityBar quality="hot" value={temperament.scores.hot} maxValue={maxQualityValue} />
            <QualityBar quality="cold" value={temperament.scores.cold} maxValue={maxQualityValue} />
            <QualityBar quality="wet" value={temperament.scores.wet} maxValue={maxQualityValue} />
            <QualityBar quality="dry" value={temperament.scores.dry} maxValue={maxQualityValue} />
          </div>
        </div>

        {/* Factors Breakdown */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            Fatores Contribuintes
          </p>
          <div className="space-y-2">
            {temperament.factors.map((factor, index) => (
              <div
                key={index}
                className="flex items-start justify-between p-3 rounded-md bg-card/50 border border-border/50"
              >
                <div className="flex-1 space-y-1">
                  <p className="text-sm font-semibold text-foreground">
                    {factor.factor_pt}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {factor.value_pt || factor.value}
                  </p>
                </div>
                <div className="flex gap-1 ml-2">
                  {factor.qualities.map((qual, qIndex) => (
                    <Badge
                      key={qIndex}
                      variant="secondary"
                      className="text-xs px-2"
                      title={qualityLabels[qual]}
                    >
                      {qualityIcons[qual]}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide font-semibold">
            Interpretação
          </p>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {temperament.description}
          </p>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            ⚖️ O temperamento é determinado pela soma das qualidades elementares (Quente, Frio,
            Úmido, Seco) de 5 fatores do mapa natal: Ascendente, Regente do Ascendente, Quadrante
            Solar, Fase Lunar e Senhor da Natividade, seguindo a tradição da astrologia medieval.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
