/**
 * Interactive Chart Wheel component - circular birth chart visualization with
 * tooltips, highlights, zoom, and pan functionality
 */

import { useRef, useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getPlanetSymbol,
  getSignSymbol,
  longitudeToAngle,
  polarToCartesian,
  getAspectColor,
  isMajorAspect,
  ZODIAC_SIGNS,
} from '../../utils/astro';
import { spring, staggerDelay, motionSafe, fadeIn } from '../../config/animations';
import { useChartInteraction } from '../../hooks/useChartInteraction';
import { ChartTooltip } from './ChartTooltip';
import { Button } from '@/components/ui/button';
import { ZoomIn, ZoomOut, RotateCcw, Move } from 'lucide-react';
import type { PlanetPosition } from '../PlanetList';
import type { HousePosition } from '../HouseTable';
import type { AspectData } from '../AspectGrid';

interface InteractiveChartWheelProps {
  planets: PlanetPosition[];
  houses: HousePosition[];
  aspects: AspectData[];
  ascendant: number;
  midheaven: number;
  onPlanetClick?: (planet: PlanetPosition) => void;
  onHouseClick?: (house: HousePosition) => void;
  onAspectClick?: (aspect: AspectData) => void;
}

export function InteractiveChartWheel({
  planets,
  houses,
  aspects,
  ascendant,
  midheaven,
  onPlanetClick,
  onHouseClick,
  onAspectClick,
}: InteractiveChartWheelProps) {
  const { t } = useTranslation();
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Pan state
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });

  // Chart interaction hook
  const {
    selectedElement,
    selectPlanet,
    selectHouse,
    selectAspect,
    clearSelection,
    hoveredElement,
    setHoveredPlanet,
    setHoveredHouse,
    setHoveredAspect,
    relatedPlanets,
    relatedAspects,
    zoomPan,
    zoomIn,
    zoomOut,
    resetZoom,
    setPan,
  } = useChartInteraction({
    planets,
    houses,
    aspects,
    onPlanetClick,
    onHouseClick,
    onAspectClick,
  });

  // Chart dimensions
  const size = 600;
  const center = size / 2;
  const outerRadius = 280;
  const signRadius = 240;
  const planetRadius = 200;
  const houseRadius = 160;
  const innerRadius = 120;

  // Get mouse position relative to SVG
  const getMousePosition = useCallback((e: React.MouseEvent) => {
    if (!containerRef.current) return { x: 0, y: 0 };
    const rect = containerRef.current.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    };
  }, []);

  // Handle wheel zoom
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.1 : 0.1;
      const newScale = Math.max(0.5, Math.min(2, zoomPan.scale + delta));

      // Zoom towards mouse position
      if (svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect();
        const mouseX = e.clientX - rect.left - rect.width / 2;
        const mouseY = e.clientY - rect.top - rect.height / 2;

        const scaleDiff = newScale - zoomPan.scale;
        const newTranslateX = zoomPan.translateX - mouseX * scaleDiff * 0.5;
        const newTranslateY = zoomPan.translateY - mouseY * scaleDiff * 0.5;

        setPan(newTranslateX, newTranslateY);
      }
    },
    [zoomPan, setPan]
  );

  // Handle pan start
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (e.button === 0 && zoomPan.scale > 1) {
        setIsPanning(true);
        setPanStart({ x: e.clientX - zoomPan.translateX, y: e.clientY - zoomPan.translateY });
      }
    },
    [zoomPan]
  );

  // Handle pan move
  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (isPanning) {
        setPan(e.clientX - panStart.x, e.clientY - panStart.y);
      }
    },
    [isPanning, panStart, setPan]
  );

  // Handle pan end
  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Handle double click to reset zoom
  const handleDoubleClick = useCallback(() => {
    resetZoom();
  }, [resetZoom]);

  // Handle click outside to clear selection
  const handleBackgroundClick = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  // Check if a planet is selected or related
  const getPlanetStyle = useCallback(
    (planetName: string) => {
      if (selectedElement?.type === 'planet' && selectedElement.id === planetName) {
        return {
          className: 'text-primary',
          filter:
            'drop-shadow(0 0 8px hsl(var(--primary))) drop-shadow(0 0 16px hsl(var(--primary)))',
          scale: 1.3,
        };
      }
      if (relatedPlanets.includes(planetName)) {
        return {
          className: 'text-foreground',
          filter: 'drop-shadow(0 0 4px hsl(var(--primary)/0.5))',
          scale: 1.1,
        };
      }
      if (selectedElement && selectedElement.type !== 'planet') {
        return {
          className: 'text-muted-foreground',
          filter: 'none',
          scale: 1,
        };
      }
      return {
        className: 'text-foreground',
        filter: 'drop-shadow(0 0 2px white) drop-shadow(0 0 4px white)',
        scale: 1,
      };
    },
    [selectedElement, relatedPlanets]
  );

  // Check if an aspect is selected or related
  const getAspectStyle = useCallback(
    (aspect: AspectData) => {
      const aspectId = `${aspect.planet1}-${aspect.planet2}-${aspect.aspect}`;
      const isSelected = selectedElement?.type === 'aspect' && selectedElement.id === aspectId;
      const isRelated = relatedAspects.some(
        (a) => `${a.planet1}-${a.planet2}-${a.aspect}` === aspectId
      );

      if (isSelected) {
        return {
          strokeWidth: 3,
          opacity: 1,
          filter: 'drop-shadow(0 0 4px currentColor)',
        };
      }
      if (isRelated) {
        return {
          strokeWidth: 2,
          opacity: 0.9,
          filter: 'none',
        };
      }
      if (selectedElement) {
        return {
          strokeWidth: 1,
          opacity: 0.2,
          filter: 'none',
        };
      }
      return {
        strokeWidth: aspect.orb <= 1 ? 2 : 1,
        opacity: aspect.orb <= 2 ? 0.8 : aspect.orb <= 4 ? 0.5 : 0.3,
        filter: 'none',
      };
    },
    [selectedElement, relatedAspects]
  );

  // Render zodiac signs
  function renderZodiacSigns() {
    return ZODIAC_SIGNS.map((sign, index) => {
      const startLongitude = index * 30;
      const midLongitude = startLongitude + 15;
      const startAngle = longitudeToAngle(startLongitude);
      const midAngle = longitudeToAngle(midLongitude);
      const startOuter = polarToCartesian(center, center, outerRadius, startAngle);
      const startSign = polarToCartesian(center, center, signRadius, startAngle);
      const symbolPos = polarToCartesian(center, center, (outerRadius + signRadius) / 2, midAngle);

      return (
        <motion.g
          key={sign}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: staggerDelay(index, 0.03), duration: 0.3 }}
        >
          <motion.line
            x1={startOuter.x}
            y1={startOuter.y}
            x2={startSign.x}
            y2={startSign.y}
            stroke="currentColor"
            strokeWidth="1"
            className="text-border opacity-50"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ delay: staggerDelay(index, 0.02), duration: 0.2 }}
          />
          <motion.text
            x={symbolPos.x}
            y={symbolPos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className="text-foreground text-xl font-semibold"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{
              delay: staggerDelay(index, 0.03) + 0.1,
              ...spring.bouncy,
            }}
          >
            {getSignSymbol(sign)}
          </motion.text>
        </motion.g>
      );
    });
  }

  // Render houses
  function renderHouses() {
    return houses.map((house) => {
      const angle = longitudeToAngle(house.longitude);
      const outerPoint = polarToCartesian(center, center, signRadius, angle);
      const innerPoint = polarToCartesian(center, center, houseRadius, angle);
      const nextHouse = houses[house.house % 12];
      const nextAngle = longitudeToAngle(nextHouse.longitude);
      const midAngle = (angle + nextAngle) / 2;
      const labelPos = polarToCartesian(center, center, (signRadius + houseRadius) / 2, midAngle);

      const isAngular = [1, 4, 7, 10].includes(house.house);
      const isSelected =
        selectedElement?.type === 'house' && selectedElement.id === `house-${house.house}`;

      return (
        <g
          key={house.house}
          className="cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            selectHouse(house);
          }}
          onMouseEnter={(e) => {
            const pos = getMousePosition(e);
            setHoveredHouse(house, pos);
          }}
          onMouseLeave={() => setHoveredHouse(null)}
        >
          <line
            x1={outerPoint.x}
            y1={outerPoint.y}
            x2={innerPoint.x}
            y2={innerPoint.y}
            stroke="currentColor"
            strokeWidth={isAngular ? '2' : '1'}
            className={`${
              isSelected
                ? 'text-primary'
                : isAngular
                  ? 'text-primary'
                  : 'text-muted-foreground opacity-40'
            } transition-colors duration-200`}
            style={{
              filter: isSelected ? 'drop-shadow(0 0 4px hsl(var(--primary)))' : 'none',
            }}
          />
          <text
            x={labelPos.x}
            y={labelPos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className={`text-xs font-semibold transition-colors duration-200 ${
              isSelected ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            {house.house}
          </text>
        </g>
      );
    });
  }

  // Render planets
  function renderPlanets() {
    return planets.map((planet, index) => {
      const angle = longitudeToAngle(planet.longitude);
      const pos = polarToCartesian(center, center, planetRadius, angle);
      const style = getPlanetStyle(planet.name);

      return (
        <motion.g
          key={planet.name}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: style.scale }}
          transition={{
            delay: staggerDelay(index, 0.08) + 0.5,
            ...spring.bouncy,
          }}
          whileHover={{ scale: style.scale * 1.15 }}
          className="cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            selectPlanet(planet);
          }}
          onMouseEnter={(e) => {
            const mousePos = getMousePosition(e);
            setHoveredPlanet(planet, mousePos);
          }}
          onMouseLeave={() => setHoveredPlanet(null)}
        >
          <motion.text
            x={pos.x}
            y={pos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className={`text-2xl font-bold ${style.className} transition-colors duration-200`}
            style={{ filter: style.filter }}
          >
            {getPlanetSymbol(planet.name)}
          </motion.text>
          {planet.retrograde && (
            <motion.text
              x={pos.x + 15}
              y={pos.y - 12}
              textAnchor="middle"
              className="text-[10px] font-bold text-destructive"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: staggerDelay(index, 0.08) + 0.6 }}
            >
              R
            </motion.text>
          )}
        </motion.g>
      );
    });
  }

  // Render aspects
  function renderAspects() {
    const majorAspects = aspects.filter((a) => isMajorAspect(a.aspect));

    return majorAspects.map((aspect, index) => {
      const planet1 = planets.find((p) => p.name === aspect.planet1);
      const planet2 = planets.find((p) => p.name === aspect.planet2);

      if (!planet1 || !planet2) return null;

      const angle1 = longitudeToAngle(planet1.longitude);
      const angle2 = longitudeToAngle(planet2.longitude);
      const pos1 = polarToCartesian(center, center, innerRadius, angle1);
      const pos2 = polarToCartesian(center, center, innerRadius, angle2);
      const color = getAspectColor(aspect.aspect);
      const style = getAspectStyle(aspect);

      return (
        <motion.line
          key={`${aspect.planet1}-${aspect.planet2}-${aspect.aspect}-${index}`}
          x1={pos1.x}
          y1={pos1.y}
          x2={pos2.x}
          y2={pos2.y}
          stroke={color}
          strokeWidth={style.strokeWidth}
          strokeOpacity={style.opacity}
          strokeDasharray={aspect.applying ? '0' : '4 2'}
          style={{ filter: style.filter }}
          className="cursor-pointer transition-all duration-200"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{
            pathLength: { delay: staggerDelay(index, 0.05) + 0.3, duration: 0.8 },
            opacity: { delay: staggerDelay(index, 0.05) + 0.3, duration: 0.3 },
          }}
          onClick={(e) => {
            e.stopPropagation();
            selectAspect(aspect);
          }}
          onMouseEnter={(e) => {
            const mousePos = getMousePosition(e);
            setHoveredAspect(aspect, mousePos);
          }}
          onMouseLeave={() => setHoveredAspect(null)}
        />
      );
    });
  }

  // Render ASC marker
  function renderAscendant() {
    const angle = longitudeToAngle(ascendant);
    const outer = polarToCartesian(center, center, outerRadius + 10, angle);
    const inner = polarToCartesian(center, center, houseRadius - 10, angle);

    return (
      <g>
        <line
          x1={outer.x}
          y1={outer.y}
          x2={inner.x}
          y2={inner.y}
          stroke="currentColor"
          strokeWidth="3"
          className="text-primary"
        />
        <text
          x={outer.x}
          y={outer.y}
          textAnchor="middle"
          dominantBaseline="central"
          className="text-xs font-bold text-primary"
          transform={`translate(${outer.x > center ? 15 : -15}, 0)`}
        >
          ASC
        </text>
      </g>
    );
  }

  // Render MC marker
  function renderMidheaven() {
    const angle = longitudeToAngle(midheaven);
    const outer = polarToCartesian(center, center, outerRadius + 10, angle);
    const inner = polarToCartesian(center, center, houseRadius - 10, angle);

    return (
      <g>
        <line
          x1={outer.x}
          y1={outer.y}
          x2={inner.x}
          y2={inner.y}
          stroke="currentColor"
          strokeWidth="3"
          className="text-secondary"
        />
        <text
          x={outer.x}
          y={outer.y}
          textAnchor="middle"
          dominantBaseline="central"
          className="text-xs font-bold text-secondary"
          transform={`translate(0, ${outer.y < center ? -15 : 15})`}
        >
          MC
        </text>
      </g>
    );
  }

  return (
    <div className="relative" ref={containerRef}>
      {/* Zoom Controls */}
      <div className="absolute top-2 right-2 z-10 flex flex-col gap-1">
        <Button
          variant="outline"
          size="icon"
          className="h-8 w-8"
          onClick={zoomIn}
          title={t('components.chartWheel.zoomIn', { defaultValue: 'Ampliar' })}
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          className="h-8 w-8"
          onClick={zoomOut}
          title={t('components.chartWheel.zoomOut', { defaultValue: 'Reduzir' })}
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          className="h-8 w-8"
          onClick={resetZoom}
          title={t('components.chartWheel.resetZoom', { defaultValue: 'Resetar zoom' })}
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Zoom indicator */}
      {zoomPan.scale !== 1 && (
        <div className="absolute top-2 left-2 z-10 bg-card/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-muted-foreground">
          {Math.round(zoomPan.scale * 100)}%
        </div>
      )}

      {/* Pan indicator */}
      {zoomPan.scale > 1 && (
        <div className="absolute bottom-2 left-2 z-10 flex items-center gap-1 bg-card/80 backdrop-blur-sm px-2 py-1 rounded text-xs text-muted-foreground">
          <Move className="h-3 w-3" />
          {t('components.chartWheel.dragToPan', { defaultValue: 'Arraste para mover' })}
        </div>
      )}

      {/* Main chart */}
      <motion.div
        className="flex justify-center p-4 overflow-hidden"
        initial="hidden"
        animate="visible"
        variants={motionSafe(fadeIn)}
        style={{
          cursor: isPanning ? 'grabbing' : zoomPan.scale > 1 ? 'grab' : 'default',
        }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onDoubleClick={handleDoubleClick}
      >
        <motion.svg
          ref={svgRef}
          viewBox={`0 0 ${size} ${size}`}
          className="w-full max-w-2xl h-auto"
          style={{
            maxHeight: '600px',
            transform: `scale(${zoomPan.scale}) translate(${zoomPan.translateX / zoomPan.scale}px, ${zoomPan.translateY / zoomPan.scale}px)`,
            transformOrigin: 'center center',
          }}
          initial={{ rotate: -90, scale: 0.8, opacity: 0 }}
          animate={{ rotate: 0, scale: 1, opacity: 1 }}
          transition={{ ...spring.gentle, duration: 1 }}
          onClick={handleBackgroundClick}
        >
          {/* Background */}
          <motion.circle
            cx={center}
            cy={center}
            r={outerRadius}
            fill="currentColor"
            className="text-background"
            initial={{ r: 0 }}
            animate={{ r: outerRadius }}
            transition={{ duration: 0.5 }}
          />

          {/* Outer circle */}
          <motion.circle
            cx={center}
            cy={center}
            r={outerRadius}
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            className="text-border"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: 0.1 }}
          />

          {/* Sign circle */}
          <motion.circle
            cx={center}
            cy={center}
            r={signRadius}
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-border opacity-50"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: 0.15 }}
          />

          {/* House circle */}
          <motion.circle
            cx={center}
            cy={center}
            r={houseRadius}
            fill="none"
            stroke="currentColor"
            strokeWidth="1"
            className="text-border opacity-50"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          />

          {/* Inner circle */}
          <motion.circle
            cx={center}
            cy={center}
            r={innerRadius}
            fill="currentColor"
            stroke="currentColor"
            strokeWidth="1"
            className="text-muted/20 stroke-border opacity-50"
            initial={{ r: 0 }}
            animate={{ r: innerRadius }}
            transition={{ duration: 0.5, delay: 0.25 }}
          />

          {/* Render elements in layers */}
          {renderAspects()}
          {renderZodiacSigns()}
          {renderHouses()}
          {renderAscendant()}
          {renderMidheaven()}
          {renderPlanets()}
        </motion.svg>
      </motion.div>

      {/* Tooltip */}
      <AnimatePresence>
        {hoveredElement && (
          <ChartTooltip
            type={hoveredElement.type}
            data={hoveredElement.data}
            position={hoveredElement.position}
            containerRef={containerRef}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
