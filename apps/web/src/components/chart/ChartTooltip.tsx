/**
 * Chart Tooltip component - displays information on hover over chart elements
 */

import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getPlanetSymbol,
  getSignSymbol,
  getAspectSymbol,
  formatDMS,
  getAspectColor,
} from '../../utils/astro';
import { getDignityBadge, getDignityScore, getScoreColorClass } from '../../utils/dignities';
import { useAstroTranslation } from '../../hooks/useAstroTranslation';
import type { PlanetPosition } from '../PlanetList';
import type { HousePosition } from '../HouseTable';
import type { AspectData } from '../AspectGrid';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface ChartTooltipProps {
  type: 'planet' | 'house' | 'aspect';
  data: PlanetPosition | HousePosition | AspectData;
  position: { x: number; y: number };
  containerRef?: React.RefObject<HTMLDivElement>;
}

export function ChartTooltip({ type, data, position, containerRef }: ChartTooltipProps) {
  // Calculate position to keep tooltip within container
  const getAdjustedPosition = () => {
    let x = position.x + 15;
    let y = position.y - 10;

    if (containerRef?.current) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const tooltipWidth = 280;
      const tooltipHeight = 200;

      // Adjust if tooltip would go outside container
      if (x + tooltipWidth > containerRect.width) {
        x = position.x - tooltipWidth - 15;
      }
      if (y + tooltipHeight > containerRect.height) {
        y = containerRect.height - tooltipHeight - 10;
      }
      if (y < 0) {
        y = 10;
      }
    }

    return { x, y };
  };

  const adjustedPosition = getAdjustedPosition();

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        transition={{ duration: 0.15 }}
        className="absolute z-50 bg-card border border-border rounded-lg shadow-lg p-3 min-w-[220px] max-w-[280px] pointer-events-none"
        style={{
          left: adjustedPosition.x,
          top: adjustedPosition.y,
        }}
      >
        {type === 'planet' && <PlanetTooltipContent planet={data as PlanetPosition} />}
        {type === 'house' && <HouseTooltipContent house={data as HousePosition} />}
        {type === 'aspect' && <AspectTooltipContent aspect={data as AspectData} />}
      </motion.div>
    </AnimatePresence>
  );
}

function PlanetTooltipContent({ planet }: { planet: PlanetPosition }) {
  const { t } = useTranslation();
  const { translatePlanet, translateSign } = useAstroTranslation();

  const dignityScore = planet.dignities ? getDignityScore(planet.dignities) : 0;
  const dignityBadge = planet.dignities ? getDignityBadge(planet.dignities) : null;

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="text-2xl">{getPlanetSymbol(planet.name)}</span>
        <span className="font-semibold text-foreground">{translatePlanet(planet.name)}</span>
        {planet.retrograde && (
          <Badge variant="destructive" className="text-xs">
            R
          </Badge>
        )}
      </div>

      <Separator />

      {/* Position */}
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.position', { defaultValue: 'Posição' })}:
          </span>
          <span className="font-medium">
            {formatDMS(planet.degree, planet.minute, planet.second)} {getSignSymbol(planet.sign)}{' '}
            {translateSign(planet.sign)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.house', { defaultValue: 'Casa' })}:
          </span>
          <span className="font-medium">{planet.house}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.speed', { defaultValue: 'Velocidade' })}:
          </span>
          <span className="font-medium">{planet.speed.toFixed(3)}°/dia</span>
        </div>
      </div>

      {/* Dignities */}
      {planet.dignities && (
        <>
          <Separator />
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {t('components.chartTooltip.dignities', { defaultValue: 'Dignidades' })}:
              </span>
              {dignityBadge && (
                <Badge variant="secondary" className="text-xs">
                  {dignityBadge.icon} {dignityBadge.label}
                </Badge>
              )}
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                {t('components.chartTooltip.score', { defaultValue: 'Score' })}:
              </span>
              <span className={`font-bold ${getScoreColorClass(dignityScore)}`}>
                {dignityScore > 0 ? '+' : ''}
                {dignityScore}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function HouseTooltipContent({ house }: { house: HousePosition }) {
  const { t } = useTranslation();
  const { translateSign } = useAstroTranslation();

  const houseName =
    house.house === 1
      ? t('components.chartTooltip.ascendant', { defaultValue: 'Ascendente' })
      : house.house === 10
        ? t('components.chartTooltip.midheaven', { defaultValue: 'Meio do Céu' })
        : t('components.chartTooltip.houseN', {
            n: house.house,
            defaultValue: `Casa ${house.house}`,
          });

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="text-xl font-bold text-primary">{house.house}</span>
        <span className="font-semibold text-foreground">{houseName}</span>
      </div>

      <Separator />

      {/* Position */}
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.cusp', { defaultValue: 'Cúspide' })}:
          </span>
          <span className="font-medium">
            {formatDMS(house.degree, house.minute, house.second)} {getSignSymbol(house.sign)}{' '}
            {translateSign(house.sign)}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.longitude', { defaultValue: 'Longitude' })}:
          </span>
          <span className="font-medium">{house.longitude.toFixed(2)}°</span>
        </div>
      </div>
    </div>
  );
}

function AspectTooltipContent({ aspect }: { aspect: AspectData }) {
  const { t } = useTranslation();
  const { translatePlanet, translateAspect } = useAstroTranslation();

  const color = getAspectColor(aspect.aspect);
  const isHarmonic = ['Trine', 'Sextile', 'Conjunction'].includes(aspect.aspect);
  const isTense = ['Square', 'Opposition'].includes(aspect.aspect);

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="flex items-center gap-2">
        <span className="text-xl">{getPlanetSymbol(aspect.planet1)}</span>
        <span className="text-xl" style={{ color }}>
          {getAspectSymbol(aspect.aspect)}
        </span>
        <span className="text-xl">{getPlanetSymbol(aspect.planet2)}</span>
      </div>
      <div className="text-sm font-medium text-center">
        {translatePlanet(aspect.planet1)} {translateAspect(aspect.aspect)}{' '}
        {translatePlanet(aspect.planet2)}
      </div>

      <Separator />

      {/* Details */}
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.angle', { defaultValue: 'Ângulo' })}:
          </span>
          <span className="font-medium">{aspect.angle.toFixed(1)}°</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.orb', { defaultValue: 'Orbe' })}:
          </span>
          <span className="font-medium">{aspect.orb.toFixed(2)}°</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('components.chartTooltip.applying', { defaultValue: 'Aplicando' })}:
          </span>
          <span className="font-medium">
            {aspect.applying
              ? t('common.yes', { defaultValue: 'Sim' })
              : t('common.no', { defaultValue: 'Não' })}
          </span>
        </div>
      </div>

      {/* Nature */}
      <div className="flex justify-center">
        <Badge
          variant={isHarmonic ? 'default' : isTense ? 'destructive' : 'secondary'}
          className="text-xs"
        >
          {isHarmonic
            ? t('components.chartTooltip.harmonic', { defaultValue: 'Harmônico' })
            : isTense
              ? t('components.chartTooltip.tense', { defaultValue: 'Tenso' })
              : t('components.chartTooltip.neutral', { defaultValue: 'Neutro' })}
        </Badge>
      </div>
    </div>
  );
}
