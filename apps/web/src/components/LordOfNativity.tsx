/**
 * Lord of Nativity component - displays the planet with highest essential dignity
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { getSignSymbol } from '@/utils/astro';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';

export interface DignityDetail {
  type: string;
  label: string;
  points: number;
  icon: string;
}

export interface LordOfNativityData {
  planet: string;
  score: number;
  sign: string;
  house: number;
  classification: string;
  dignity_details: DignityDetail[];
}

interface LordOfNativityProps {
  lordOfNativity: LordOfNativityData;
}

// Planet symbols
const planetSymbols: Record<string, string> = {
  Sun: '☉',
  Moon: '☽',
  Mercury: '☿',
  Venus: '♀',
  Mars: '♂',
  Jupiter: '♃',
  Saturn: '♄',
};

// Classification colors
const classificationColors: Record<string, string> = {
  dignified: 'bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20',
  peregrine: 'bg-yellow-500/10 text-yellow-700 dark:text-yellow-400 border-yellow-500/20',
  debilitated: 'bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20',
};

const classificationLabels: Record<string, string> = {
  dignified: 'Dignificado',
  peregrine: 'Peregrino',
  debilitated: 'Debilitado',
};

export function LordOfNativity({ lordOfNativity }: LordOfNativityProps) {
  const { t } = useTranslation();
  const { translatePlanet, translateSign } = useAstroTranslation();

  const planetSymbol = planetSymbols[lordOfNativity.planet] || '★';
  const classificationColor =
    classificationColors[lordOfNativity.classification] ||
    'bg-gray-500/10 text-gray-700 dark:text-gray-400 border-gray-500/20';
  const classificationLabel =
    classificationLabels[lordOfNativity.classification] || lordOfNativity.classification;

  return (
    <Card className="bg-gradient-to-br from-amber-500/10 to-yellow-500/10 border-amber-500/20">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label="Coroa">
            👑
          </span>
          <div className="flex-1">
            <div className="text-lg font-semibold text-foreground flex items-center gap-2">
              <span className="text-2xl" title={translatePlanet(lordOfNativity.planet)}>
                {planetSymbol}
              </span>
              {t('components.lordOfNativity.title', { defaultValue: 'Senhor da Natividade' })}:{' '}
              {translatePlanet(lordOfNativity.planet)}
            </div>
            <div className="text-xs text-muted-foreground font-normal mt-1">
              {t('components.lordOfNativity.subtitle', {
                defaultValue: 'A força vital dominante do seu mapa natal',
              })}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Score and Classification */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.lordOfNativity.totalScore', { defaultValue: 'Pontuação Total' })}
            </p>
            <p className="text-2xl font-bold text-foreground">
              {lordOfNativity.score > 0 ? '+' : ''}
              {lordOfNativity.score}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.lordOfNativity.status', { defaultValue: 'Status' })}
            </p>
            <Badge variant="outline" className={`text-xs font-semibold ${classificationColor}`}>
              {classificationLabel}
            </Badge>
          </div>
        </div>

        {/* Position */}
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.lordOfNativity.position', { defaultValue: 'Posição' })}
          </p>
          <p className="text-sm font-semibold text-foreground">
            {getSignSymbol(lordOfNativity.sign)} {translateSign(lordOfNativity.sign)} •{' '}
            {t('components.lordOfNativity.house', { defaultValue: 'Casa' })} {lordOfNativity.house}
          </p>
        </div>

        {/* Dignity Breakdown */}
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {t('components.lordOfNativity.essentialDignities', {
              defaultValue: 'Dignidades Essenciais',
            })}
          </p>
          <div className="space-y-2">
            {lordOfNativity.dignity_details.map((detail, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 rounded-md bg-card/50 border border-border/50"
              >
                <div className="flex items-center gap-2">
                  <span className="text-xl" role="img" aria-label={detail.label}>
                    {detail.icon}
                  </span>
                  <span className="text-sm text-foreground">{detail.label}</span>
                </div>
                <Badge
                  variant="secondary"
                  className={`text-xs font-mono ${
                    detail.points > 0
                      ? 'bg-green-500/10 text-green-700 dark:text-green-400'
                      : 'bg-red-500/10 text-red-700 dark:text-red-400'
                  }`}
                >
                  {detail.points > 0 ? '+' : ''}
                  {detail.points}
                </Badge>
              </div>
            ))}
          </div>
        </div>

        {/* Info Note */}
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">
            👑{' '}
            {t('components.lordOfNativity.note', {
              defaultValue:
                'O Senhor da Natividade é o planeta com maior dignidade essencial no seu mapa natal. Segundo a astrologia tradicional, ele representa a força vital dominante que guia sua vida e indica onde você tem maior potencial de realização e maestria.',
            })}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
