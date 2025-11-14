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
}

export function HouseTable({ houses }: HouseTableProps) {
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
    </div>
  );
}
