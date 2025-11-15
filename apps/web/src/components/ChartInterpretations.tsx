/**
 * Chart Interpretations component - displays AI-generated astrological interpretations
 */

import { useState, useEffect } from 'react';
import { interpretationsService, ChartInterpretations } from '../services/interpretations';
import { getPlanetSymbol } from '../utils/astro';

const TOKEN_KEY = 'astro_access_token';

// Classical 7 planets only
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

interface ChartInterpretationsProps {
  chartId: string;
}

export function ChartInterpretationsComponent({ chartId }: ChartInterpretationsProps) {
  const [interpretations, setInterpretations] = useState<ChartInterpretations | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [error, setError] = useState('');
  const [activeSection, setActiveSection] = useState<'planets' | 'houses' | 'aspects'>('planets');

  useEffect(() => {
    loadInterpretations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartId]);

  async function loadInterpretations() {
    try {
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) return;

      const data = await interpretationsService.getByChartId(chartId, token);
      setInterpretations(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar interpretações');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleRegenerate() {
    if (!confirm('Deseja regenerar todas as interpretações? As atuais serão substituídas.')) {
      return;
    }

    try {
      setIsRegenerating(true);
      const token = localStorage.getItem(TOKEN_KEY);
      if (!token) return;

      const data = await interpretationsService.regenerate(chartId, token);
      setInterpretations(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao regenerar interpretações');
    } finally {
      setIsRegenerating(false);
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-3"></div>
          <p className="text-sm text-muted-foreground">Carregando interpretações...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <p className="text-sm text-destructive">{error}</p>
      </div>
    );
  }

  if (!interpretations) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Nenhuma interpretação disponível</p>
      </div>
    );
  }

  // Count interpretations
  const planetsCount = Object.keys(interpretations.planets || {}).length;
  const housesCount = Object.keys(interpretations.houses || {}).length;
  const aspectsCount = Object.keys(interpretations.aspects || {}).length;

  return (
    <div>
      {/* Header with Regenerate Button */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-semibold text-foreground">
            Interpretações Astrológicas
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Geradas por IA • Baseadas em astrologia tradicional
          </p>
        </div>
        <button
          onClick={handleRegenerate}
          disabled={isRegenerating}
          className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:opacity-90 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isRegenerating ? 'Regenerando...' : '↻ Regenerar'}
        </button>
      </div>

      {/* Section Tabs */}
      <div className="mb-6 flex gap-2 border-b border-border">
        <button
          onClick={() => setActiveSection('planets')}
          className={`px-4 py-3 text-sm font-medium transition-colors ${
            activeSection === 'planets'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Planetas ({planetsCount})
        </button>
        <button
          onClick={() => setActiveSection('houses')}
          className={`px-4 py-3 text-sm font-medium transition-colors ${
            activeSection === 'houses'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Casas ({housesCount})
        </button>
        <button
          onClick={() => setActiveSection('aspects')}
          className={`px-4 py-3 text-sm font-medium transition-colors ${
            activeSection === 'aspects'
              ? 'text-primary border-b-2 border-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          Aspectos ({aspectsCount})
        </button>
      </div>

      {/* Planet Interpretations */}
      {activeSection === 'planets' && (
        <div className="space-y-4">
          {CLASSICAL_PLANETS.map((planetKey) => {
            const interpretation = interpretations.planets[planetKey];
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
                  <h3 className="text-lg font-semibold text-foreground">
                    {PLANET_NAMES_PT[planetKey] || planetKey}
                  </h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {interpretation}
                </p>
              </div>
            );
          })}
          {planetsCount === 0 && (
            <p className="text-center text-muted-foreground py-8">
              Nenhuma interpretação de planetas disponível
            </p>
          )}
        </div>
      )}

      {/* House Interpretations */}
      {activeSection === 'houses' && (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
            const interpretation = interpretations.houses[houseNum.toString()];
            if (!interpretation) return null;

            return (
              <div
                key={houseNum}
                className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
              >
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-sm">
                    {houseNum}
                  </span>
                  Casa {houseNum}
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {interpretation}
                </p>
              </div>
            );
          })}
          {housesCount === 0 && (
            <p className="text-center text-muted-foreground py-8">
              Nenhuma interpretação de casas disponível
            </p>
          )}
        </div>
      )}

      {/* Aspect Interpretations */}
      {activeSection === 'aspects' && (
        <div className="space-y-4">
          {Object.entries(interpretations.aspects || {}).map(([aspectKey, interpretation]) => {
            // Parse aspect key like "Sun-Trine-Moon"
            const parts = aspectKey.split('-');
            if (parts.length !== 3) return null;

            const [planet1, aspect, planet2] = parts;

            return (
              <div
                key={aspectKey}
                className="bg-gradient-to-r from-muted/50 to-background border border-border rounded-lg p-5"
              >
                <h3 className="text-lg font-semibold text-foreground mb-3 flex items-center gap-2">
                  <span className="text-xl">{getPlanetSymbol(planet1)}</span>
                  <span className="text-sm text-muted-foreground">{aspect}</span>
                  <span className="text-xl">{getPlanetSymbol(planet2)}</span>
                  <span className="text-sm text-muted-foreground">
                    {PLANET_NAMES_PT[planet1]} - {PLANET_NAMES_PT[planet2]}
                  </span>
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
                  {interpretation}
                </p>
              </div>
            );
          })}
          {aspectsCount === 0 && (
            <p className="text-center text-muted-foreground py-8">
              Nenhuma interpretação de aspectos disponível
            </p>
          )}
        </div>
      )}

      {/* Footer Info */}
      <div className="mt-8 bg-muted/30 border border-border rounded-lg p-4">
        <p className="text-xs text-muted-foreground">
          <strong>ℹ️ Sobre as interpretações:</strong> Estas interpretações foram geradas
          automaticamente por inteligência artificial baseando-se em princípios de astrologia
          tradicional helênica e medieval. Consideram dignidades essenciais, sect (dia/noite),
          e focam nos 7 planetas clássicos. Use-as como ferramenta de reflexão e
          autoconhecimento.
        </p>
      </div>
    </div>
  );
}
