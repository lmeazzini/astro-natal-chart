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
}

export function AspectGrid({ aspects }: AspectGridProps) {
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
    <div className="space-y-4">
      {/* Controls */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Filter */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">Filtro:</label>
          <div className="flex rounded-md border border-input overflow-hidden">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 text-xs font-medium transition-colors ${
                filter === 'all'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-background text-muted-foreground hover:bg-muted'
              }`}
            >
              Todos ({aspects.length})
            </button>
            <button
              onClick={() => setFilter('major')}
              className={`px-3 py-1 text-xs font-medium transition-colors border-l border-input ${
                filter === 'major'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-background text-muted-foreground hover:bg-muted'
              }`}
            >
              Principais ({aspects.filter((a) => isMajorAspect(a.aspect)).length})
            </button>
          </div>
        </div>

        {/* Sort */}
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-foreground">Ordenar:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'orb' | 'type')}
            className="px-3 py-1 text-xs bg-background border border-input rounded-md text-foreground"
          >
            <option value="orb">Por Orbe (exato → amplo)</option>
            <option value="type">Por Tipo</option>
          </select>
        </div>
      </div>

      {/* Aspect Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-4 py-3 text-left font-semibold text-foreground">
                Planeta 1
              </th>
              <th className="px-4 py-3 text-center font-semibold text-foreground">
                Aspecto
              </th>
              <th className="px-4 py-3 text-left font-semibold text-foreground">
                Planeta 2
              </th>
              <th className="px-4 py-3 text-center font-semibold text-foreground">
                Orbe
              </th>
              <th className="px-4 py-3 text-center font-semibold text-foreground">
                Status
              </th>
              <th className="px-4 py-3 text-right font-semibold text-foreground">
                Ângulo
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedAspects.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-4 py-8 text-center text-muted-foreground"
                >
                  Nenhum aspecto encontrado
                </td>
              </tr>
            ) : (
              sortedAspects.map((aspect, index) => {
                const aspectColor = getAspectColor(aspect.aspect);

                return (
                  <tr
                    key={`${aspect.planet1}-${aspect.planet2}-${aspect.aspect}`}
                    className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${
                      index % 2 === 0 ? 'bg-background' : 'bg-muted/20'
                    }`}
                  >
                    {/* Planet 1 */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xl" title={aspect.planet1}>
                          {getPlanetSymbol(aspect.planet1)}
                        </span>
                        <span className="font-medium text-foreground">
                          {aspect.planet1}
                        </span>
                      </div>
                    </td>

                    {/* Aspect Symbol and Name */}
                    <td className="px-4 py-3 text-center">
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
                    </td>

                    {/* Planet 2 */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <span className="text-xl" title={aspect.planet2}>
                          {getPlanetSymbol(aspect.planet2)}
                        </span>
                        <span className="font-medium text-foreground">
                          {aspect.planet2}
                        </span>
                      </div>
                    </td>

                    {/* Orb */}
                    <td className="px-4 py-3 text-center">
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
                    </td>

                    {/* Applying/Separating */}
                    <td className="px-4 py-3 text-center">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${
                          aspect.applying
                            ? 'bg-primary/10 text-primary'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {aspect.applying ? 'Aplicando' : 'Separando'}
                      </span>
                    </td>

                    {/* Exact Angle */}
                    <td className="px-4 py-3 text-right">
                      <span className="font-mono text-xs text-muted-foreground">
                        {aspect.angle.toFixed(2)}°
                      </span>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="px-4 py-3 bg-muted/30 rounded-md text-xs text-muted-foreground space-y-2">
        <p>
          <strong className="text-foreground">Orbe:</strong> Distância do aspecto exato.
          Orbes menores indicam aspectos mais fortes.
        </p>
        <p>
          <strong className="text-foreground">Aplicando:</strong> Aspecto se aproximando da exatidão.{' '}
          <strong className="text-foreground">Separando:</strong> Aspecto se afastando da exatidão.
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
      </div>
    </div>
  );
}
