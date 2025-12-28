/**
 * PrenatalSyzygy - Display the prenatal syzygy (last New Moon or Full Moon before birth).
 *
 * The prenatal syzygy is significant in traditional astrology as it indicates
 * the lunar cycle during which the person was conceived. It's used in:
 * - Almuten Figuris calculation
 * - Rectification techniques
 * - Understanding prenatal influences
 *
 * The API returns already-localized data based on the `lang` query parameter,
 * so no frontend language switching is needed - just display the values directly.
 */

import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export interface PrenatalSyzygyData {
  type: 'new_moon' | 'full_moon';
  type_name: string;
  longitude: number;
  sign: string;
  sign_key: string;
  degree: number;
  minute: number;
  house: number;
  emoji: string;
  interpretation: string;
  keywords: string;
}

interface PrenatalSyzygyProps {
  prenatalSyzygy: PrenatalSyzygyData;
}

export function PrenatalSyzygy({ prenatalSyzygy }: PrenatalSyzygyProps) {
  const { t } = useTranslation();

  // Format degree and minute nicely
  const formatPosition = () => {
    const deg = prenatalSyzygy.degree;
    const min = prenatalSyzygy.minute.toString().padStart(2, '0');
    return `${deg}°${min}'`;
  };

  return (
    <Card className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border-indigo-500/20">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-3">
          <span className="text-4xl" role="img" aria-label={prenatalSyzygy.type_name}>
            {prenatalSyzygy.emoji}
          </span>
          <div>
            <div className="text-lg font-semibold text-foreground">{prenatalSyzygy.type_name}</div>
            <div className="text-sm text-muted-foreground">
              {formatPosition()} {prenatalSyzygy.sign}
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Position Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.prenatalSyzygy.position')}
            </p>
            <p className="text-sm font-medium text-foreground">
              {formatPosition()} {prenatalSyzygy.sign}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.prenatalSyzygy.house')}
            </p>
            <p className="text-sm font-medium text-foreground">
              {t('common.houseNumber', { number: prenatalSyzygy.house })}
            </p>
          </div>
        </div>

        {/* Keywords */}
        {prenatalSyzygy.keywords && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.prenatalSyzygy.keywords')}
            </p>
            <div className="flex flex-wrap gap-2">
              {prenatalSyzygy.keywords.split(',').map((keyword, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {keyword.trim()}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Interpretation */}
        {prenatalSyzygy.interpretation && (
          <div className="space-y-2">
            <p className="text-xs text-muted-foreground uppercase tracking-wide">
              {t('components.prenatalSyzygy.interpretation')}
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {prenatalSyzygy.interpretation}
            </p>
          </div>
        )}

        {/* Info Note */}
        <div className="pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground">{t('components.prenatalSyzygy.note')}</p>
        </div>
      </CardContent>
    </Card>
  );
}
