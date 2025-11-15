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
  interpretations?: Record<string, string>;
  interpretationsLoading?: boolean;
  onRegenerateInterpretations?: () => void;
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
  interpretationsLoading = false,
  onRegenerateInterpretations,
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
              {[...Array(5)].map((_, i) => (
                <div key={i} className="bg-muted/30 border border-border rounded-lg p-5 animate-pulse">
                  <div className="h-6 bg-muted rounded w-1/3 mb-3"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-muted rounded w-full"></div>
                    <div className="h-4 bg-muted rounded w-5/6"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="space-y-4">
              {Object.entries(interpretations).map(([aspectKey, interpretation]) => {
                // Parse aspect key like "Sun-Trine-Moon"
                const parts = aspectKey.split('-');
                if (parts.length !== 3) return null;

                const [planet1, aspect, planet2] = parts;

                return (
                  <div
                    key={aspectKey}
                    className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
                  >
                    <h4 className="text-lg font-semibold text-foreground mb-3">
                      <div className="text-sm text-muted-foreground mb-1">{aspect}</div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xl">{getPlanetSymbol(planet1)}</span>
                        <span className="text-sm">{PLANET_NAMES_PT[planet1] || planet1}</span>
                        <span className="text-sm text-muted-foreground">-</span>
                        <span className="text-xl">{getPlanetSymbol(planet2)}</span>
                        <span className="text-sm">{PLANET_NAMES_PT[planet2] || planet2}</span>
                      </div>
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
              princípios de astrologia tradicional. Interpretações consideram a natureza do
              aspecto e os planetas envolvidos.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
