/**
 * Aspect Grid component - displays all aspects between planets
 */

import { useState } from 'react';
import {
  getPlanetSymbol,
  getAspectSymbol,
  getAspectColor,
  formatOrb,
  isMajorAspect,
} from '../utils/astro';

// shadcn/ui components
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group';
import { Info } from 'lucide-react';

export interface AspectData {
  planet1: string;
  planet2: string;
  aspect: string;
  angle: number;
  orb: number;
  applying: boolean;
}

interface AspectGridProps {
  aspects: AspectData[];
  interpretations?: Record<string, string>;
}

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

export function AspectGrid({
  aspects,
  interpretations,
}: AspectGridProps) {
  const [filter, setFilter] = useState<'all' | 'major'>('all');
  const [sortBy, setSortBy] = useState<'orb' | 'type'>('orb');

  // Filter aspects
  let filteredAspects = aspects;
  if (filter === 'major') {
    filteredAspects = aspects.filter((a) => isMajorAspect(a.aspect));
  }

  // Sort aspects
  const sortedAspects = [...filteredAspects].sort((a, b) => {
    if (sortBy === 'orb') {
      return a.orb - b.orb; // Tighter orbs first
    } else {
      return a.aspect.localeCompare(b.aspect);
    }
  });

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">Filtro:</label>
          <ToggleGroup type="single" value={filter} onValueChange={(value) => value && setFilter(value as 'all' | 'major')}>
            <ToggleGroupItem value="all" aria-label="Todos os aspectos">
              Todos ({aspects.length})
            </ToggleGroupItem>
            <ToggleGroupItem value="major" aria-label="Aspectos principais">
              Principais ({aspects.filter((a) => isMajorAspect(a.aspect)).length})
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">Ordenar:</label>
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as 'orb' | 'type')}>
            <SelectTrigger className="w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="orb">Por Orbe (exato → amplo)</SelectItem>
              <SelectItem value="type">Por Tipo</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Aspect Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Planeta 1</TableHead>
              <TableHead className="text-center">Aspecto</TableHead>
              <TableHead>Planeta 2</TableHead>
              <TableHead className="text-center">Orbe</TableHead>
              <TableHead className="text-center">Status</TableHead>
              <TableHead className="text-right">Ângulo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedAspects.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-muted-foreground"
                >
                  Nenhum aspecto encontrado
                </TableCell>
              </TableRow>
            ) : (
              sortedAspects.map((aspect) => {
                const aspectColor = getAspectColor(aspect.aspect);

                return (
                  <TableRow key={`${aspect.planet1}-${aspect.planet2}-${aspect.aspect}`}>
                    {/* Planet 1 */}
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span className="text-xl" title={aspect.planet1}>
                          {getPlanetSymbol(aspect.planet1)}
                        </span>
                        <span className="font-medium text-foreground">
                          {aspect.planet1}
                        </span>
                      </div>
                    </TableCell>

                    {/* Aspect Symbol and Name */}
                    <TableCell className="text-center">
                      <div className="flex flex-col items-center gap-1">
                        <span
                          className="text-2xl"
                          style={{ color: aspectColor }}
                          title={aspect.aspect}
                        >
                          {getAspectSymbol(aspect.aspect)}
                        </span>
                        <span
                          className="text-xs font-medium"
                          style={{ color: aspectColor }}
                        >
                          {aspect.aspect}
                        </span>
                      </div>
                    </TableCell>

                    {/* Planet 2 */}
                    <TableCell className="">
                      <div className="flex items-center gap-2">
                        <span className="text-xl" title={aspect.planet2}>
                          {getPlanetSymbol(aspect.planet2)}
                        </span>
                        <span className="font-medium text-foreground">
                          {aspect.planet2}
                        </span>
                      </div>
                    </TableCell>

                    {/* Orb */}
                    <TableCell className=" text-center">
                      <span
                        className={`font-mono text-xs ${
                          aspect.orb <= 1
                            ? 'text-primary font-semibold'
                            : aspect.orb <= 3
                            ? 'text-foreground'
                            : 'text-muted-foreground'
                        }`}
                      >
                        {formatOrb(aspect.orb)}
                      </span>
                    </TableCell>

                    {/* Applying/Separating */}
                    <TableCell className="text-center">
                      <Badge
                        variant={aspect.applying ? 'default' : 'outline'}
                      >
                        {aspect.applying ? 'Aplicando' : 'Separando'}
                      </Badge>
                    </TableCell>

                    {/* Exact Angle */}
                    <TableCell className=" text-right">
                      <span className="font-mono text-xs text-muted-foreground">
                        {aspect.angle.toFixed(2)}°
                      </span>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </div>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Legenda</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>Orbe:</strong> Distância do aspecto exato.
            Orbes menores indicam aspectos mais fortes.
          </p>
          <p>
            <strong>Aplicando:</strong> Aspecto se aproximando da exatidão.{' '}
            <strong>Separando:</strong> Aspecto se afastando da exatidão.
          </p>
          <div className="flex flex-wrap gap-3 mt-2">
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Conjunction') }}>●</span> Conjunção
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Opposition') }}>●</span> Oposição
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Trine') }}>●</span> Trígono
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Square') }}>●</span> Quadratura
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Sextile') }}>●</span> Sextil
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground">
            Interpretações Astrológicas
          </h3>

          <div className="space-y-4">
            {Object.entries(interpretations).map(([aspectKey, interpretation]) => {
              // Parse aspect key like "Sun-Trine-Moon"
              const parts = aspectKey.split('-');
              if (parts.length !== 3) return null;

              const [planet1, aspect, planet2] = parts;

              return (
                <Card key={aspectKey}>
                  <CardHeader>
                    <div className="text-sm text-muted-foreground mb-1">{aspect}</div>
                    <CardTitle className="flex items-center gap-2 flex-wrap">
                      <span className="text-xl">{getPlanetSymbol(planet1)}</span>
                      <span className="text-sm">{PLANET_NAMES_PT[planet1] || planet1}</span>
                      <span className="text-sm text-muted-foreground">-</span>
                      <span className="text-xl">{getPlanetSymbol(planet2)}</span>
                      <span className="text-sm">{PLANET_NAMES_PT[planet2] || planet2}</span>
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
            {Object.keys(interpretations).length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                Nenhuma interpretação disponível
              </p>
            )}
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Sobre as interpretações:</strong> Geradas por IA baseando-se em
              princípios de astrologia tradicional. Interpretações consideram a natureza do
              aspecto e os planetas envolvidos.
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
