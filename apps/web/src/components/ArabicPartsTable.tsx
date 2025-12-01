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
  // Extended Arabic Parts (Issue #110 - Phase 2)
  marriage?: ArabicPart;
  victory?: ArabicPart;
  father?: ArabicPart;
  mother?: ArabicPart;
  children?: ArabicPart;
  exaltation?: ArabicPart;
  illness?: ArabicPart;
  courage?: ArabicPart;
  reputation?: ArabicPart;
}

interface ArabicPartsInterpretations {
  fortune?: string;
  spirit?: string;
  eros?: string;
  necessity?: string;
  // Extended Arabic Parts (Issue #110 - Phase 2)
  marriage?: string;
  victory?: string;
  father?: string;
  mother?: string;
  children?: string;
  exaltation?: string;
  illness?: string;
  courage?: string;
  reputation?: string;
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
      description: t('components.arabicParts.fortuneDesc', {
        defaultValue: 'Corpo, saúde, riqueza material',
      }),
      color: 'from-amber-500/10 to-yellow-500/10 border-amber-500/20',
      tooltipContent: t('components.arabicParts.fortuneTooltip', {
        defaultValue:
          'A mais importante das Partes Árabes. Representa o corpo físico, a saúde vital e a riqueza material que "vem até nós". Na tradição helenística, é calculada a partir do Sol, Lua e Ascendente.',
      }),
    },
    {
      key: 'spirit' as const,
      name: t('components.arabicParts.spirit', { defaultValue: 'Lote do Espírito' }),
      nameEn: 'Part of Spirit',
      symbol: '☉',
      description: t('components.arabicParts.spiritDesc', {
        defaultValue: 'Mente, ação, iniciativas',
      }),
      color: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
      tooltipContent: t('components.arabicParts.spiritTooltip', {
        defaultValue:
          'Complementar ao Lote da Fortuna. Representa a mente, o intelecto e aquilo que "fazemos acontecer" através de nossas ações conscientes. É a fórmula inversa da Fortuna.',
      }),
    },
    {
      key: 'eros' as const,
      name: t('components.arabicParts.eros', { defaultValue: 'Lote de Eros' }),
      nameEn: 'Part of Eros',
      symbol: '♥',
      description: t('components.arabicParts.erosDesc', { defaultValue: 'Amor, desejo, paixão' }),
      color: 'from-pink-500/10 to-rose-500/10 border-pink-500/20',
      tooltipContent: t('components.arabicParts.erosTooltip', {
        defaultValue:
          'Representa o amor romântico, o desejo erótico e a paixão. Complementa a análise de Vênus, revelando como experimentamos o amor e a atração.',
      }),
    },
    {
      key: 'necessity' as const,
      name: t('components.arabicParts.necessity', { defaultValue: 'Lote da Necessidade' }),
      nameEn: 'Part of Necessity',
      symbol: '⚯',
      description: t('components.arabicParts.necessityDesc', {
        defaultValue: 'Restrições, karma, destino',
      }),
      color: 'from-gray-500/10 to-slate-500/10 border-gray-500/20',
      tooltipContent: t('components.arabicParts.necessityTooltip', {
        defaultValue:
          'Representa as restrições inevitáveis, o karma e as lições de vida. Indica áreas onde enfrentamos dificuldades necessárias para nosso desenvolvimento.',
      }),
    },
    // Extended Arabic Parts (Issue #110 - Phase 2)
    {
      key: 'marriage' as const,
      name: t('components.arabicParts.marriage', { defaultValue: 'Lote do Casamento' }),
      nameEn: 'Part of Marriage',
      symbol: '⚭',
      description: t('components.arabicParts.marriageDesc', {
        defaultValue: 'Relacionamentos, parcerias, casamento',
      }),
      color: 'from-purple-500/10 to-violet-500/10 border-purple-500/20',
      tooltipContent: t('components.arabicParts.marriageTooltip', {
        defaultValue:
          'Indica a natureza das parcerias comprometidas, potencial de casamento e o tipo de parceiro que atraímos. Calculado a partir de Vênus e Saturno.',
      }),
    },
    {
      key: 'victory' as const,
      name: t('components.arabicParts.victory', { defaultValue: 'Lote da Vitória' }),
      nameEn: 'Part of Victory',
      symbol: '♕',
      description: t('components.arabicParts.victoryDesc', {
        defaultValue: 'Sucesso, conquista, triunfo',
      }),
      color: 'from-fuchsia-500/10 to-pink-500/10 border-fuchsia-500/20',
      tooltipContent: t('components.arabicParts.victoryTooltip', {
        defaultValue:
          'Mostra áreas de triunfo e onde podemos alcançar sucesso. Associado a Júpiter e à capacidade do nativo para a vitória.',
      }),
    },
    {
      key: 'father' as const,
      name: t('components.arabicParts.father', { defaultValue: 'Lote do Pai' }),
      nameEn: 'Part of Father',
      symbol: '♂',
      description: t('components.arabicParts.fatherDesc', {
        defaultValue: 'Figura paterna, autoridade',
      }),
      color: 'from-orange-500/10 to-amber-500/10 border-orange-500/20',
      tooltipContent: t('components.arabicParts.fatherTooltip', {
        defaultValue:
          'Revela a relação com a figura paterna e herança paternal. Tradicionalmente calculado usando Sol e Saturno.',
      }),
    },
    {
      key: 'mother' as const,
      name: t('components.arabicParts.mother', { defaultValue: 'Lote da Mãe' }),
      nameEn: 'Part of Mother',
      symbol: '♀',
      description: t('components.arabicParts.motherDesc', {
        defaultValue: 'Figura materna, nutrição',
      }),
      color: 'from-teal-500/10 to-cyan-500/10 border-teal-500/20',
      tooltipContent: t('components.arabicParts.motherTooltip', {
        defaultValue:
          'Revela a relação com a figura materna e herança maternal. Tradicionalmente calculado usando Lua e Vênus.',
      }),
    },
    {
      key: 'children' as const,
      name: t('components.arabicParts.children', { defaultValue: 'Lote dos Filhos' }),
      nameEn: 'Part of Children',
      symbol: '☽',
      description: t('components.arabicParts.childrenDesc', {
        defaultValue: 'Filhos, criatividade, fertilidade',
      }),
      color: 'from-indigo-500/10 to-purple-500/10 border-indigo-500/20',
      tooltipContent: t('components.arabicParts.childrenTooltip', {
        defaultValue:
          'Indica fertilidade, relação com filhos e expressão criativa. Associado à casa 5 e Júpiter.',
      }),
    },
    {
      key: 'exaltation' as const,
      name: t('components.arabicParts.exaltation', { defaultValue: 'Lote da Exaltação' }),
      nameEn: 'Part of Exaltation',
      symbol: '⬆',
      description: t('components.arabicParts.exaltationDesc', {
        defaultValue: 'Honra, reconhecimento, elevação',
      }),
      color: 'from-yellow-500/10 to-lime-500/10 border-yellow-500/20',
      tooltipContent: t('components.arabicParts.exaltationTooltip', {
        defaultValue:
          'Mostra onde recebemos honra e reconhecimento. Usa fórmula fixa (não inverte por seita) baseada no grau de exaltação do Sol (19° Áries).',
      }),
    },
    {
      key: 'illness' as const,
      name: t('components.arabicParts.illness', { defaultValue: 'Lote da Doença' }),
      nameEn: 'Part of Illness',
      symbol: '☿',
      description: t('components.arabicParts.illnessDesc', {
        defaultValue: 'Saúde, vulnerabilidades',
      }),
      color: 'from-emerald-500/10 to-green-500/10 border-emerald-500/20',
      tooltipContent: t('components.arabicParts.illnessTooltip', {
        defaultValue:
          'Indica vulnerabilidades de saúde e áreas que requerem atenção. Associado à casa 6 e calculado com Marte e Saturno.',
      }),
    },
    {
      key: 'courage' as const,
      name: t('components.arabicParts.courage', { defaultValue: 'Lote da Coragem' }),
      nameEn: 'Part of Courage',
      symbol: '⚔',
      description: t('components.arabicParts.courageDesc', {
        defaultValue: 'Bravura, ousadia, iniciativa',
      }),
      color: 'from-red-500/10 to-orange-500/10 border-red-500/20',
      tooltipContent: t('components.arabicParts.courageTooltip', {
        defaultValue:
          'Revela a capacidade do nativo para bravura e ação ousada. Associado a Marte e ao Lote da Fortuna.',
      }),
    },
    {
      key: 'reputation' as const,
      name: t('components.arabicParts.reputation', { defaultValue: 'Lote da Reputação' }),
      nameEn: 'Part of Reputation',
      symbol: '★',
      description: t('components.arabicParts.reputationDesc', {
        defaultValue: 'Fama, imagem pública',
      }),
      color: 'from-violet-500/10 to-purple-500/10 border-violet-500/20',
      tooltipContent: t('components.arabicParts.reputationTooltip', {
        defaultValue:
          'Mostra como somos percebidos publicamente e potencial para fama. Calculado a partir do Lote da Fortuna e do Espírito.',
      }),
    },
  ];

  const partsInfo = getPartsInfo();

  // Filter to only show parts that are available in the data
  const availableParts = partsInfo.filter((info) => parts[info.key]);

  return (
    <div className="space-y-4">
      {/* Grid de Cards - responsive layout up to 4 columns on XL screens */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {availableParts.map((info) => {
          const part = parts[info.key]!;

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
                        <InfoTooltip content={info.tooltipContent} side="top" />
                      </div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        {isEn ? info.name : info.nameEn}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      {t('components.arabicParts.position', { defaultValue: 'Posição' })}:
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {formatDegree(part.degree)}° {getSignSymbol(part.sign)}{' '}
                      {translateSign(part.sign)}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      {t('components.arabicParts.house', { defaultValue: 'Casa' })}:
                    </span>
                    <span className="text-sm font-medium text-foreground">
                      {t('components.arabicParts.houseNumber', {
                        defaultValue: 'Casa {{num}}',
                        num: part.house,
                      })}
                    </span>
                  </div>

                  <div className="pt-2 mt-2 border-t border-border/50">
                    <p className="text-xs text-muted-foreground italic">{info.description}</p>
                  </div>

                  {/* Interpretation section */}
                  {interpretations && interpretations[info.key] && (
                    <div className="pt-3 mt-3 border-t border-border/50">
                      <p className="text-sm font-medium text-foreground mb-1">
                        {t('components.arabicParts.interpretation', {
                          defaultValue: 'Interpretação',
                        })}
                        :
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
                {availableParts.map((info) => {
                  const part = parts[info.key]!;

                  return (
                    <tr
                      key={info.key}
                      className="border-b border-border/50 hover:bg-muted/30 transition-colors"
                    >
                      <td className="py-3 px-2 text-sm font-medium text-foreground">
                        {isEn ? info.nameEn : info.name}
                      </td>
                      <td className="py-3 px-2 text-center text-2xl">{info.symbol}</td>
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
