/**
 * Planet List component - displays all planets with their positions
 */

import { getPlanetSymbol, getSignSymbol, formatDMS } from '../utils/astro';

export interface PlanetPosition {
  name: string;
  longitude: number;
  latitude: number;
  speed: number;
  sign: string;
  degree: number;
  minute: number;
  second: number;
  house: number;
  retrograde: boolean;
}

interface PlanetListProps {
  planets: PlanetPosition[];
}

export function PlanetList({ planets }: PlanetListProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-muted/50">
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Planeta
            </th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Signo
            </th>
            <th className="px-4 py-3 text-left font-semibold text-foreground">
              Posição
            </th>
            <th className="px-4 py-3 text-center font-semibold text-foreground">
              Casa
            </th>
            <th className="px-4 py-3 text-center font-semibold text-foreground">
              Retrógrado
            </th>
            <th className="px-4 py-3 text-right font-semibold text-foreground">
              Velocidade
            </th>
          </tr>
        </thead>
        <tbody>
          {planets.map((planet, index) => (
            <tr
              key={planet.name}
              className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${
                index % 2 === 0 ? 'bg-background' : 'bg-muted/20'
              }`}
            >
              {/* Planet Name with Symbol */}
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl" title={planet.name}>
                    {getPlanetSymbol(planet.name)}
                  </span>
                  <span className="font-medium text-foreground">
                    {planet.name}
                  </span>
                </div>
              </td>

              {/* Sign with Symbol */}
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <span className="text-xl" title={planet.sign}>
                    {getSignSymbol(planet.sign)}
                  </span>
                  <span className="text-muted-foreground">{planet.sign}</span>
                </div>
              </td>

              {/* Position (Degree, Minute, Second) */}
              <td className="px-4 py-3">
                <span className="font-mono text-muted-foreground">
                  {formatDMS(planet.degree, planet.minute, planet.second)}
                </span>
              </td>

              {/* House */}
              <td className="px-4 py-3 text-center">
                <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-xs">
                  {planet.house}
                </span>
              </td>

              {/* Retrograde Indicator */}
              <td className="px-4 py-3 text-center">
                {planet.retrograde ? (
                  <span className="inline-flex items-center px-2 py-1 rounded-md bg-destructive/10 text-destructive text-xs font-semibold">
                    R
                  </span>
                ) : (
                  <span className="text-muted-foreground/30 text-xs">—</span>
                )}
              </td>

              {/* Speed (Daily Motion) */}
              <td className="px-4 py-3 text-right">
                <span
                  className={`font-mono text-xs ${
                    planet.speed < 0
                      ? 'text-destructive'
                      : 'text-muted-foreground'
                  }`}
                >
                  {planet.speed.toFixed(4)}°/dia
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Summary */}
      <div className="mt-4 px-4 py-3 bg-muted/30 rounded-md text-sm text-muted-foreground">
        <p>
          <strong className="text-foreground">{planets.length}</strong> planetas
          calculados •{' '}
          <strong className="text-foreground">
            {planets.filter((p) => p.retrograde).length}
          </strong>{' '}
          retrógrado(s)
        </p>
      </div>
    </div>
  );
}
