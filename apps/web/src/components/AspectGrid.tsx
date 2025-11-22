/**
 * Aspect Grid component - displays all aspects between planets
 */

import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  getPlanetSymbol,
  getAspectSymbol,
  getAspectColor,
  formatOrb,
  isMajorAspect,
} from '../utils/astro';
import { useAstroTranslation } from '../hooks/useAstroTranslation';

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

export function AspectGrid({
  aspects,
  interpretations,
}: AspectGridProps) {
  const { t } = useTranslation();
  const { translatePlanet, translateAspect } = useAstroTranslation();
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
          <label className="text-sm font-medium text-foreground">{t('components.aspectGrid.filter', { defaultValue: 'Filtro' })}:</label>
          <ToggleGroup type="single" value={filter} onValueChange={(value) => value && setFilter(value as 'all' | 'major')}>
            <ToggleGroupItem value="all" aria-label={t('components.aspectGrid.allAspects', { defaultValue: 'Todos os aspectos' })}>
              {t('components.aspectGrid.all', { defaultValue: 'Todos' })} ({aspects.length})
            </ToggleGroupItem>
            <ToggleGroupItem value="major" aria-label={t('components.aspectGrid.majorAspects', { defaultValue: 'Aspectos principais' })}>
              {t('components.aspectGrid.major', { defaultValue: 'Principais' })} ({aspects.filter((a) => isMajorAspect(a.aspect)).length})
            </ToggleGroupItem>
          </ToggleGroup>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">{t('components.aspectGrid.sort', { defaultValue: 'Ordenar' })}:</label>
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as 'orb' | 'type')}>
            <SelectTrigger className="w-[200px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="orb">{t('components.aspectGrid.byOrb', { defaultValue: 'Por Orbe (exato → amplo)' })}</SelectItem>
              <SelectItem value="type">{t('components.aspectGrid.byType', { defaultValue: 'Por Tipo' })}</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Aspect Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t('components.aspectGrid.planet1', { defaultValue: 'Planeta 1' })}</TableHead>
              <TableHead className="text-center">{t('components.aspectGrid.aspect', { defaultValue: 'Aspecto' })}</TableHead>
              <TableHead>{t('components.aspectGrid.planet2', { defaultValue: 'Planeta 2' })}</TableHead>
              <TableHead className="text-center">{t('components.aspectGrid.orb', { defaultValue: 'Orbe' })}</TableHead>
              <TableHead className="text-center">{t('components.aspectGrid.status', { defaultValue: 'Status' })}</TableHead>
              <TableHead className="text-right">{t('components.aspectGrid.angle', { defaultValue: 'Ângulo' })}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedAspects.length === 0 ? (
              <TableRow>
                <TableCell
                  colSpan={6}
                  className="text-center text-muted-foreground"
                >
                  {t('components.aspectGrid.noAspects', { defaultValue: 'Nenhum aspecto encontrado' })}
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
                        <span className="text-xl" title={translatePlanet(aspect.planet1)}>
                          {getPlanetSymbol(aspect.planet1)}
                        </span>
                        <span className="font-medium text-foreground">
                          {translatePlanet(aspect.planet1)}
                        </span>
                      </div>
                    </TableCell>

                    {/* Aspect Symbol and Name */}
                    <TableCell className="text-center">
                      <div className="flex flex-col items-center gap-1">
                        <span
                          className="text-2xl"
                          style={{ color: aspectColor }}
                          title={translateAspect(aspect.aspect)}
                        >
                          {getAspectSymbol(aspect.aspect)}
                        </span>
                        <span
                          className="text-xs font-medium"
                          style={{ color: aspectColor }}
                        >
                          {translateAspect(aspect.aspect)}
                        </span>
                      </div>
                    </TableCell>

                    {/* Planet 2 */}
                    <TableCell className="">
                      <div className="flex items-center gap-2">
                        <span className="text-xl" title={translatePlanet(aspect.planet2)}>
                          {getPlanetSymbol(aspect.planet2)}
                        </span>
                        <span className="font-medium text-foreground">
                          {translatePlanet(aspect.planet2)}
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
                        {aspect.applying ? t('components.aspectGrid.applying', { defaultValue: 'Aplicando' }) : t('components.aspectGrid.separating', { defaultValue: 'Separando' })}
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
          <CardTitle className="text-sm">{t('components.aspectGrid.legend', { defaultValue: 'Legenda' })}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <p>
            <strong>{t('components.aspectGrid.orb', { defaultValue: 'Orbe' })}:</strong> {t('components.aspectGrid.orbDesc', { defaultValue: 'Distância do aspecto exato. Orbes menores indicam aspectos mais fortes.' })}
          </p>
          <p>
            <strong>{t('components.aspectGrid.applying', { defaultValue: 'Aplicando' })}:</strong> {t('components.aspectGrid.applyingDesc', { defaultValue: 'Aspecto se aproximando da exatidão.' })}{' '}
            <strong>{t('components.aspectGrid.separating', { defaultValue: 'Separando' })}:</strong> {t('components.aspectGrid.separatingDesc', { defaultValue: 'Aspecto se afastando da exatidão.' })}
          </p>
          <div className="flex flex-wrap gap-3 mt-2">
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Conjunction') }}>●</span> {t('components.aspectGrid.conjunction', { defaultValue: 'Conjunção' })}
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Opposition') }}>●</span> {t('components.aspectGrid.opposition', { defaultValue: 'Oposição' })}
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Trine') }}>●</span> {t('components.aspectGrid.trine', { defaultValue: 'Trígono' })}
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Square') }}>●</span> {t('components.aspectGrid.square', { defaultValue: 'Quadratura' })}
            </span>
            <span className="flex items-center gap-1">
              <span style={{ color: getAspectColor('Sextile') }}>●</span> {t('components.aspectGrid.sextile', { defaultValue: 'Sextil' })}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Interpretations Section */}
      {interpretations && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-foreground">
            {t('components.aspectGrid.astrologicalInterpretations', { defaultValue: 'Interpretações Astrológicas' })}
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
                    <div className="text-sm text-muted-foreground mb-1">{translateAspect(aspect)}</div>
                    <CardTitle className="flex items-center gap-2 flex-wrap">
                      <span className="text-xl">{getPlanetSymbol(planet1)}</span>
                      <span className="text-sm">{translatePlanet(planet1)}</span>
                      <span className="text-sm text-muted-foreground">-</span>
                      <span className="text-xl">{getPlanetSymbol(planet2)}</span>
                      <span className="text-sm">{translatePlanet(planet2)}</span>
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
                {t('components.aspectGrid.noInterpretations', { defaultValue: 'Nenhuma interpretação disponível' })}
              </p>
            )}
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>{t('components.aspectGrid.aboutInterpretations', { defaultValue: 'Sobre as interpretações' })}:</strong> {t('components.aspectGrid.interpretationsDesc', { defaultValue: 'Geradas por IA baseando-se em princípios de astrologia tradicional. Interpretações consideram a natureza do aspecto e os planetas envolvidos.' })}
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
