/**
 * Planet List component - displays all planets with their positions
 */

import { useState } from 'react';
import { getPlanetSymbol, getSignSymbol, formatDMS } from '../utils/astro';
import {
  Dignities,
  getDignityBadge,
  getDignityScore,
  getScoreColorClass,
  getDignityDetails,
  getClassificationLabel,
} from '../utils/dignities';

// shadcn/ui components
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Info } from 'lucide-react';

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
  dignities?: Dignities;
}

interface LordOfNativityData {
  planet: string;
  score: number;
  sign: string;
  house: number;
  classification: string;
}

interface PlanetListProps {
  planets: PlanetPosition[];
  showOnlyClassical?: boolean;
  interpretations?: Record<string, string>;
  lordOfNativity?: LordOfNativityData | null;
}

type SortBy = 'position' | 'house' | 'dignity';

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
  lordOfNativity,
}: PlanetListProps) {
  const [sortBy, setSortBy] = useState<SortBy>('position');
  const [showDignityInfo, setShowDignityInfo] = useState(false);

  // Filter planets if showOnlyClassical is true
  let displayPlanets = showOnlyClassical
    ? planets.filter((p) => CLASSICAL_PLANETS.includes(p.name))
    : planets;

  // Sort planets based on selected criteria
  displayPlanets = [...displayPlanets].sort((a, b) => {
    if (sortBy === 'dignity') {
      const scoreA = getDignityScore(a.dignities);
      const scoreB = getDignityScore(b.dignities);
      return scoreB - scoreA; // Higher score first
    }
    if (sortBy === 'house') {
      return a.house - b.house;
    }
    // Default: sort by position (longitude)
    return a.longitude - b.longitude;
  });
  // Check if any planet has dignities (for showing dignity column)
  const hasDignities = displayPlanets.some((p) => p.dignities !== undefined);

  return (
    <div className="space-y-6">
      {/* Sorting Controls */}
      {hasDignities && (
        <div className="flex gap-4 items-center flex-wrap">
          <label className="text-sm font-medium text-foreground">Ordenar por:</label>
          <ToggleGroup type="single" value={sortBy} onValueChange={(value) => value && setSortBy(value as SortBy)}>
            <ToggleGroupItem value="position" aria-label="Ordenar por posição">
              Posição
            </ToggleGroupItem>
            <ToggleGroupItem value="house" aria-label="Ordenar por casa">
              Casa
            </ToggleGroupItem>
            <ToggleGroupItem value="dignity" aria-label="Ordenar por força">
              💪 Força
            </ToggleGroupItem>
          </ToggleGroup>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDignityInfo(!showDignityInfo)}
            className="ml-auto"
          >
            <Info className="h-4 w-4 mr-2" />
            {showDignityInfo ? 'Esconder Info' : 'Mostrar Info'}
          </Button>
        </div>
      )}

      {/* Dignity Info Card */}
      {showDignityInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Dignidades Essenciais</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              As dignidades essenciais mostram a força de um planeta em determinado signo,
              baseadas na astrologia tradicional.
            </p>
            <dl className="space-y-2 text-sm">
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">👑 Domicílio:</dt>
                <dd className="text-muted-foreground">Planeta no signo que rege (+5)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">🌟 Exaltação:</dt>
                <dd className="text-muted-foreground">Ponto de maior força (+4)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">⬇️ Queda:</dt>
                <dd className="text-muted-foreground">Oposto à exaltação (-4)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">⚠️ Detrimento:</dt>
                <dd className="text-muted-foreground">Oposto ao domicílio (-5)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">🔥/🌙 Triplicidade:</dt>
                <dd className="text-muted-foreground">Afinidade elemental (+3)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">📊 Termo:</dt>
                <dd className="text-muted-foreground">Divisão de graus (+2)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">👤 Face:</dt>
                <dd className="text-muted-foreground">Divisão de 10 graus (+1)</dd>
              </div>
              <div className="flex gap-2">
                <dt className="font-semibold min-w-[120px]">🚶 Peregrino:</dt>
                <dd className="text-muted-foreground">Sem dignidades (0)</dd>
              </div>
            </dl>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                Score positivo indica planeta forte. Score negativo indica debilitação.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Planeta</TableHead>
              <TableHead>Signo</TableHead>
              <TableHead>Posição</TableHead>
              <TableHead className="text-center">Casa</TableHead>
              {hasDignities && <TableHead>Dignidades</TableHead>}
              <TableHead className="text-center">Retrógrado</TableHead>
              <TableHead className="text-right">Velocidade</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayPlanets.map((planet) => (
              <TableRow key={planet.name}>
                {/* Planet Name with Symbol */}
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl" title={planet.name}>
                      {getPlanetSymbol(planet.name)}
                    </span>
                    <span className="font-medium text-foreground">
                      {planet.name}
                    </span>
                    {lordOfNativity && lordOfNativity.planet === planet.name && (
                      <Badge
                        variant="outline"
                        className="bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20 text-xs"
                        title="Senhor da Natividade - maior dignidade essencial"
                      >
                        👑
                      </Badge>
                    )}
                  </div>
                </TableCell>

                {/* Sign with Symbol */}
                <TableCell>
                  <div className="flex items-center gap-2">
                    <span className="text-xl" title={planet.sign}>
                      {getSignSymbol(planet.sign)}
                    </span>
                    <span className="text-muted-foreground">{planet.sign}</span>
                  </div>
                </TableCell>

                {/* Position (Degree, Minute, Second) */}
                <TableCell>
                  <span className="font-mono text-muted-foreground">
                    {formatDMS(planet.degree, planet.minute, planet.second)}
                  </span>
                </TableCell>

                {/* House */}
                <TableCell className="text-center">
                  <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-semibold text-xs">
                    {planet.house}
                  </span>
                </TableCell>

                {/* Dignities Badge */}
                {hasDignities && (
                  <TableCell>
                    {planet.dignities ? (
                      <div className="flex flex-col gap-1">
                        <div
                          className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md border text-xs font-medium ${
                            getDignityBadge(planet.dignities).color
                          }`}
                          title={`Score: ${getDignityScore(planet.dignities)}`}
                        >
                          <span>{getDignityBadge(planet.dignities).icon}</span>
                          <span>{getDignityBadge(planet.dignities).label}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span
                            className={`text-xs font-semibold ${getScoreColorClass(
                              getDignityScore(planet.dignities)
                            )}`}
                          >
                            {getDignityScore(planet.dignities) > 0 ? '+' : ''}
                            {getDignityScore(planet.dignities)}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            ({getClassificationLabel(planet.dignities.classification)})
                          </span>
                        </div>
                        {/* Detailed dignity list */}
                        {getDignityDetails(planet.dignities).length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {getDignityDetails(planet.dignities).map((detail, idx) => (
                              <span
                                key={idx}
                                className="inline-flex items-center gap-0.5 text-xs text-muted-foreground"
                                title={`${detail.label}: ${detail.points > 0 ? '+' : ''}${detail.points}`}
                              >
                                {detail.icon}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-xs text-muted-foreground">—</span>
                    )}
                  </TableCell>
                )}

                {/* Retrograde Indicator */}
                <TableCell className="text-center">
                  {planet.retrograde ? (
                    <Badge variant="destructive" className="font-semibold">
                      R
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground/30 text-xs">—</span>
                  )}
                </TableCell>

                {/* Speed (Daily Motion) */}
                <TableCell className="text-right">
                  <span
                    className={`font-mono text-xs ${
                      planet.speed < 0
                        ? 'text-destructive'
                        : 'text-muted-foreground'
                    }`}
                  >
                    {planet.speed.toFixed(4)}°/dia
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Summary */}
      <Card>
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            <strong className="text-foreground">{displayPlanets.length}</strong> planetas
            {showOnlyClassical && ' clássicos'} calculados •{' '}
            <strong className="text-foreground">
              {displayPlanets.filter((p) => p.retrograde).length}
            </strong>{' '}
            retrógrado(s)
          </p>
          {showOnlyClassical && (
            <p className="mt-2 text-xs text-muted-foreground">
              Exibindo apenas os 7 planetas clássicos da astrologia tradicional
            </p>
          )}
        </CardContent>
      </Card>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground">
            Interpretações Astrológicas
          </h3>

          <div className="space-y-4">
            {CLASSICAL_PLANETS.map((planetKey) => {
              const interpretation = interpretations[planetKey];
              if (!interpretation) return null;

              return (
                <Card key={planetKey}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <span className="text-2xl" title={PLANET_NAMES_PT[planetKey]}>
                        {getPlanetSymbol(planetKey)}
                      </span>
                      {PLANET_NAMES_PT[planetKey] || planetKey}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                      {interpretation}
                    </p>
                  </CardContent>
                </Card>
              );
            })}
            {Object.keys(interpretations).filter((k) => CLASSICAL_PLANETS.includes(k)).length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                Nenhuma interpretação disponível
              </p>
            )}
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Sobre as interpretações:</strong> Geradas por IA baseando-se em
              princípios de astrologia tradicional (dignidades essenciais, sect). Foco nos 7
              planetas clássicos.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
