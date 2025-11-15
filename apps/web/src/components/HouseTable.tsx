/**
 * House Table component - displays all 12 houses with their cusps
 */

import { getSignSymbol, formatDMS, isAngularHouse, getHouseType } from '../utils/astro';

export interface HousePosition {
  house: number;
  longitude: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
}

interface HouseTableProps {
  houses: HousePosition[];
  interpretations?: Record<string, string>;
  interpretationsLoading?: boolean;
  onRegenerateInterpretations?: () => void;
}

export function HouseTable({
  houses,
  interpretations,
  interpretationsLoading = false,
  onRegenerateInterpretations,
}: HouseTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/50">
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Casa
            </th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Signo na Cúspide
            </th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Posição
            </th>
            <th className="px-4 py-3 text-center font-semibold text-foreground">
              Tipo
            </th>
          </tr>
        </thead>
        <tbody>
          {houses.map((house, index) => {
            const angular = isAngularHouse(house.house);
            const houseType = getHouseType(house.house);

            return (
              <tr
                key={house.house}
                className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${
                  index % 2 === 0 ? 'bg-background' : 'bg-muted/20'
                } ${angular ? 'font-semibold' : ''}`}
              >
                {/* House Number */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center justify-center w-9 h-9 rounded-full text-sm ${
                        angular
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {house.house}
                    </span>
                    {angular && (
                      <span className="text-xs text-primary">●</span>
                    )}
                  </div>
                </td>

                {/* Sign on Cusp with Symbol */}
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl" title={house.sign}>
                      {getSignSymbol(house.sign)}
                    </span>
                    <span className={angular ? 'text-foreground' : 'text-muted-foreground'}>
                      {house.sign}
                    </span>
                  </div>
                </td>

                {/* Position (Degree, Minute, Second) */}
                <td className="px-4 py-3">
                  <span className={`font-mono ${angular ? 'text-foreground' : 'text-muted-foreground'}`}>
                    {formatDMS(house.degree, house.minute, house.second)}
                  </span>
                </td>

                {/* House Type */}
                <td className="px-4 py-3 text-center">
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
                      houseType === 'Angular'
                        ? 'bg-primary/10 text-primary'
                        : houseType === 'Succedent'
                        ? 'bg-secondary/50 text-secondary-foreground'
                        : 'bg-muted text-muted-foreground'
                    }`}
                  >
                    {houseType}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Legend */}
      <div className="mt-4 px-4 py-3 bg-muted/30 rounded-md text-xs text-muted-foreground space-y-1">
        <p>
          <strong className="text-foreground">Angular</strong> (1, 4, 7, 10) - Casas de ação e iniciativa
        </p>
        <p>
          <strong className="text-foreground">Succedent</strong> (2, 5, 8, 11) - Casas de recursos e valores
        </p>
        <p>
          <strong className="text-foreground">Cadent</strong> (3, 6, 9, 12) - Casas de aprendizado e adaptação
        </p>
      </div>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="mt-8">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-foreground">
              Interpretações Astrológicas
            </h3>
            {onRegenerateInterpretations && (
              <button
                onClick={onRegenerateInterpretations}
                disabled={interpretationsLoading}
                className="px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {interpretationsLoading ? 'Regenerando...' : '↻ Regenerar'}
              </button>
            )}
          </div>

          {interpretationsLoading ? (
            <div className="space-y-4">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="bg-muted/30 border border-border rounded-lg p-5 animate-pulse">
                  <div className="h-6 bg-muted rounded w-1/4 mb-3"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded w-full"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
                const interpretation = interpretations[houseNum.toString()];
                if (!interpretation) return null;

                return (
                  <div
                    key={houseNum}
                    className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
                  >
                    <h4 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                        {houseNum}
                      </span>
                      Casa {houseNum}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                      {interpretation}
                    </p>
                  </div>
                );
              })}
              {Object.keys(interpretations).length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  Nenhuma interpretação disponível
                </p>
              )}
            </div>
          )}

          <div className="mt-6 bg-muted/30 border border-border rounded-lg p-4">
            <p className="text-xs text-muted-foreground">
              <strong>ℹ️ Sobre as interpretações:</strong> Geradas por IA baseando-se em
              princípios de astrologia tradicional. Interpretações consideram o signo na cúspide
              e significado de cada casa.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
