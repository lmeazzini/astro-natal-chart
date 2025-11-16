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
  showOnlyClassical?: boolean;
  interpretations?: Record<string, string>;
}

// Classical 7 planets (no modern planets)
const CLASSICAL_PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn'];

// Planet names in Portuguese
const PLANET_NAMES_PT: Record<string, string> = {
  Sun: 'Sol',
  Moon: 'Lua',
  Mercury: 'Mercúrio',
  Venus: 'Vênus',
  Mars: 'Marte',
  Jupiter: 'Júpiter',
  Saturn: 'Saturno',
};

export function PlanetList({
  planets,
  showOnlyClassical = false,
  interpretations,
}: PlanetListProps) {
  // Filter planets if showOnlyClassical is true
  const displayPlanets = showOnlyClassical
    ? planets.filter((p) => CLASSICAL_PLANETS.includes(p.name))
    : planets;
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
          {displayPlanets.map((planet, index) => (
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
          <strong className="text-foreground">{displayPlanets.length}</strong> planetas
          {showOnlyClassical && ' clássicos'} calculados •{' '}
          <strong className="text-foreground">
            {displayPlanets.filter((p) => p.retrograde).length}
          </strong>{' '}
          retrógrado(s)
        </p>
        {showOnlyClassical && (
          <p className="mt-1 text-xs">
            Exibindo apenas os 7 planetas clássicos da astrologia tradicional
          </p>
        )}
      </div>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Interpretações Astrológicas
          </h3>

          <div className="space-y-4">
            {CLASSICAL_PLANETS.map((planetKey) => {
              const interpretation = interpretations[planetKey];
              if (!interpretation) return null;

              return (
                <div
                  key={planetKey}
                  className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl" title={PLANET_NAMES_PT[planetKey]}>
                      {getPlanetSymbol(planetKey)}
                    </span>
                    <h4 className="text-lg font-semibold text-foreground">
                      {PLANET_NAMES_PT[planetKey] || planetKey}
                    </h4>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                    {interpretation}
                  </p>
                </div>
              );
            })}
            {Object.keys(interpretations).filter((k) => CLASSICAL_PLANETS.includes(k)).length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                Nenhuma interpretação disponível
              </p>
            )}
          </div>

          <div className="mt-6 bg-muted/30 border border-border rounded-lg p-4">
            <p className="text-xs text-muted-foreground">
              <strong>ℹ️ Sobre as interpretações:</strong> Geradas por IA baseando-se em
              princípios de astrologia tradicional (dignidades essenciais, sect). Foco nos 7
              planetas clássicos.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
