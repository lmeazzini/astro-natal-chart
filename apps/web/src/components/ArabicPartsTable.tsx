/**
 * Arabic Parts Table Component
 * Displays calculated Arabic Parts (Lots) in traditional astrology
 */

import { useTranslation } from 'react-i18next';
import { getSignSymbol } from '@/utils/astro';
import { useAstroTranslation } from '@/hooks/useAstroTranslation';
import { Card, CardContent } from '@/components/ui/card';
import { InfoTooltip } from '@/components/InfoTooltip';

export interface ArabicPart {
  longitude: number;
  sign: string;
  degree: number;
  house: number;
}

export interface ArabicParts {
  fortune: ArabicPart;
  spirit: ArabicPart;
  eros: ArabicPart;
  necessity: ArabicPart;
}

interface ArabicPartsInterpretations {
  fortune?: string;
  spirit?: string;
  eros?: string;
  necessity?: string;
}

interface ArabicPartsTableProps {
  parts: ArabicParts;
  interpretations?: ArabicPartsInterpretations;
}

function formatDegree(degree: number): string {
  return degree.toFixed(2);
}

export function ArabicPartsTable({ parts, interpretations }: ArabicPartsTableProps) {
  const { t, i18n } = useTranslation();
  const { translateSign } = useAstroTranslation();
  const isEn = i18n.language === 'en-US' || i18n.language === 'en';

  // Translated parts info
  const getPartsInfo = () => [
    {
      key: 'fortune' as const,
      name: t('components.arabicParts.fortune', { defaultValue: 'Lote da Fortuna' }),
      nameEn: 'Part of Fortune',
      symbol: '⊗',
      description: t('components.arabicParts.fortuneDesc', { defaultValue: 'Corpo, saúde, riqueza material' }),
      color: 'from-amber-500/10 to-yellow-500/10 border-amber-500/20',
      tooltipContent: t('components.arabicParts.fortuneTooltip', { defaultValue: 'A mais importante das Partes Árabes. Representa o corpo físico, a saúde vital e a riqueza material que "vem até nós". Na tradição helenística, é calculada a partir do Sol, Lua e Ascendente.' }),
    },
    {
      key: 'spirit' as const,
      name: t('components.arabicParts.spirit', { defaultValue: 'Lote do Espírito' }),
      nameEn: 'Part of Spirit',
      symbol: '☉',
      description: t('components.arabicParts.spiritDesc', { defaultValue: 'Mente, ação, iniciativas' }),
      color: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
      tooltipContent: t('components.arabicParts.spiritTooltip', { defaultValue: 'Complementar ao Lote da Fortuna. Representa a mente, o intelecto e aquilo que "fazemos acontecer" através de nossas ações conscientes. É a fórmula inversa da Fortuna.' }),
    },
    {
      key: 'eros' as const,
      name: t('components.arabicParts.eros', { defaultValue: 'Lote de Eros' }),
      nameEn: 'Part of Eros',
      symbol: '♥',
      description: t('components.arabicParts.erosDesc', { defaultValue: 'Amor, desejo, paixão' }),
      color: 'from-pink-500/10 to-rose-500/10 border-pink-500/20',
      tooltipContent: t('components.arabicParts.erosTooltip', { defaultValue: 'Representa o amor romântico, o desejo erótico e a paixão. Complementa a análise de Vênus, revelando como experimentamos o amor e a atração.' }),
    },
    {
      key: 'necessity' as const,
      name: t('components.arabicParts.necessity', { defaultValue: 'Lote da Necessidade' }),
      nameEn: 'Part of Necessity',
      symbol: '⚯',
      description: t('components.arabicParts.necessityDesc', { defaultValue: 'Restrições, karma, destino' }),
      color: 'from-gray-500/10 to-slate-500/10 border-gray-500/20',
      tooltipContent: t('components.arabicParts.necessityTooltip', { defaultValue: 'Representa as restrições inevitáveis, o karma e as lições de vida. Indica áreas onde enfrentamos dificuldades necessárias para nosso desenvolvimento.' }),
    },
  ];

  const partsInfo = getPartsInfo();

  return (
    <div className="space-y-4">
      {/* Grid de Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {partsInfo.map((info) => {
          const part = parts[info.key];

          return (
            <Card key={info.key} className={`border-0 shadow-lg bg-gradient-to-br ${info.color}`}>
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl" title={info.nameEn}>
                      {info.symbol}
                    </span>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-lg font-semibold text-foreground">
                          {isEn ? info.nameEn : info.name}
                        </h4>
                        <InfoTooltip
                          content={info.tooltipContent}
                          side="top"
                        />
                      </div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        {isEn ? info.name : info.nameEn}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{t('components.arabicParts.position', { defaultValue: 'Posição' })}:</span>
                    <span className="text-sm font-medium text-foreground">
                      {formatDegree(part.degree)}° {getSignSymbol(part.sign)} {translateSign(part.sign)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">{t('components.arabicParts.house', { defaultValue: 'Casa' })}:</span>
                    <span className="text-sm font-medium text-foreground">
                      {t('components.arabicParts.houseNumber', { defaultValue: 'Casa {{num}}', num: part.house })}
                    </span>
                  </div>

                  <div className="pt-2 mt-2 border-t border-border/50">
                    <p className="text-xs text-muted-foreground italic">
                      {info.description}
                    </p>
                  </div>

                  {/* Interpretation section */}
                  {interpretations && interpretations[info.key] && (
                    <div className="pt-3 mt-3 border-t border-border/50">
                      <p className="text-sm font-medium text-foreground mb-1">
                        {t('components.arabicParts.interpretation', { defaultValue: 'Interpretação' })}:
                      </p>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {interpretations[info.key]}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Tabela Resumo (opcional, para visualização compacta) */}
      <Card className="border-0 shadow-lg">
        <CardContent className="pt-6">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 px-2 text-sm font-semibold text-muted-foreground">
                    {t('components.arabicParts.part', { defaultValue: 'Parte' })}
                  </th>
                  <th className="text-center py-2 px-2 text-sm font-semibold text-muted-foreground">
                    {t('components.arabicParts.symbol', { defaultValue: 'Símbolo' })}
                  </th>
                  <th className="text-left py-2 px-2 text-sm font-semibold text-muted-foreground">
                    {t('components.arabicParts.position', { defaultValue: 'Posição' })}
                  </th>
                  <th className="text-left py-2 px-2 text-sm font-semibold text-muted-foreground">
                    {t('components.arabicParts.sign', { defaultValue: 'Signo' })}
                  </th>
                  <th className="text-center py-2 px-2 text-sm font-semibold text-muted-foreground">
                    {t('components.arabicParts.house', { defaultValue: 'Casa' })}
                  </th>
                </tr>
              </thead>
              <tbody>
                {partsInfo.map((info) => {
                  const part = parts[info.key];

                  return (
                    <tr key={info.key} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-2 text-sm font-medium text-foreground">
                        {isEn ? info.nameEn : info.name}
                      </td>
                      <td className="py-3 px-2 text-center text-2xl">
                        {info.symbol}
                      </td>
                      <td className="py-3 px-2 text-sm text-foreground">
                        {formatDegree(part.degree)}°
                      </td>
                      <td className="py-3 px-2 text-sm text-foreground">
                        <span className="flex items-center gap-1">
                          {getSignSymbol(part.sign)} {translateSign(part.sign)}
                        </span>
                      </td>
                      <td className="py-3 px-2 text-center text-sm text-foreground">
                        {part.house}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
