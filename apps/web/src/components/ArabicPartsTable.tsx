/**
 * Arabic Parts Table Component
 * Displays calculated Arabic Parts (Lots) in traditional astrology
 */

import { getSignSymbol } from '@/utils/astro';
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

interface ArabicPartsTableProps {
  parts: ArabicParts;
}

interface PartInfo {
  key: keyof ArabicParts;
  name: string;
  nameEn: string;
  symbol: string;
  description: string;
  color: string;
  tooltipContent: string;
}

const PARTS_INFO: PartInfo[] = [
  {
    key: 'fortune',
    name: 'Lote da Fortuna',
    nameEn: 'Part of Fortune',
    symbol: '⊗',
    description: 'Corpo, saúde, riqueza material',
    color: 'from-amber-500/10 to-yellow-500/10 border-amber-500/20',
    tooltipContent: 'A mais importante das Partes Árabes. Representa o corpo físico, a saúde vital e a riqueza material que "vem até nós". Na tradição helenística, é calculada a partir do Sol, Lua e Ascendente.',
  },
  {
    key: 'spirit',
    name: 'Lote do Espírito',
    nameEn: 'Part of Spirit',
    symbol: '☉',
    description: 'Mente, ação, iniciativas',
    color: 'from-blue-500/10 to-cyan-500/10 border-blue-500/20',
    tooltipContent: 'Complementar ao Lote da Fortuna. Representa a mente, o intelecto e aquilo que "fazemos acontecer" através de nossas ações conscientes. É a fórmula inversa da Fortuna.',
  },
  {
    key: 'eros',
    name: 'Lote de Eros',
    nameEn: 'Part of Eros',
    symbol: '♥',
    description: 'Amor, desejo, paixão',
    color: 'from-pink-500/10 to-rose-500/10 border-pink-500/20',
    tooltipContent: 'Representa o amor romântico, o desejo erótico e a paixão. Complementa a análise de Vênus, revelando como experimentamos o amor e a atração.',
  },
  {
    key: 'necessity',
    name: 'Lote da Necessidade',
    nameEn: 'Part of Necessity',
    symbol: '⚯',
    description: 'Restrições, karma, destino',
    color: 'from-gray-500/10 to-slate-500/10 border-gray-500/20',
    tooltipContent: 'Representa as restrições inevitáveis, o karma e as lições de vida. Indica áreas onde enfrentamos dificuldades necessárias para nosso desenvolvimento.',
  },
];

function formatDegree(degree: number): string {
  return degree.toFixed(2);
}

export function ArabicPartsTable({ parts }: ArabicPartsTableProps) {
  return (
    <div className="space-y-4">
      {/* Grid de Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {PARTS_INFO.map((info) => {
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
                          {info.name}
                        </h4>
                        <InfoTooltip
                          content={info.tooltipContent}
                          side="top"
                        />
                      </div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wide">
                        {info.nameEn}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Posição:</span>
                    <span className="text-sm font-medium text-foreground">
                      {formatDegree(part.degree)}° {getSignSymbol(part.sign)} {part.sign}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Casa:</span>
                    <span className="text-sm font-medium text-foreground">
                      Casa {part.house}
                    </span>
                  </div>

                  <div className="pt-2 mt-2 border-t border-border/50">
                    <p className="text-xs text-muted-foreground italic">
                      {info.description}
                    </p>
                  </div>
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
                    Parte
                  </th>
                  <th className="text-center py-2 px-2 text-sm font-semibold text-muted-foreground">
                    Símbolo
                  </th>
                  <th className="text-left py-2 px-2 text-sm font-semibold text-muted-foreground">
                    Posição
                  </th>
                  <th className="text-left py-2 px-2 text-sm font-semibold text-muted-foreground">
                    Signo
                  </th>
                  <th className="text-center py-2 px-2 text-sm font-semibold text-muted-foreground">
                    Casa
                  </th>
                </tr>
              </thead>
              <tbody>
                {PARTS_INFO.map((info) => {
                  const part = parts[info.key];

                  return (
                    <tr key={info.key} className="border-b border-border/50 hover:bg-muted/30 transition-colors">
                      <td className="py-3 px-2 text-sm font-medium text-foreground">
                        {info.name}
                      </td>
                      <td className="py-3 px-2 text-center text-2xl">
                        {info.symbol}
                      </td>
                      <td className="py-3 px-2 text-sm text-foreground">
                        {formatDegree(part.degree)}°
                      </td>
                      <td className="py-3 px-2 text-sm text-foreground">
                        <span className="flex items-center gap-1">
                          {getSignSymbol(part.sign)} {part.sign}
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
