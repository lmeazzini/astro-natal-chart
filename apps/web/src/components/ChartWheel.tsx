/**
 * Chart Wheel component - circular birth chart visualization with animations
 */

import { motion } from 'framer-motion';
import {
  getPlanetSymbol,
  getSignSymbol,
  longitudeToAngle,
  polarToCartesian,
  getAspectColor,
  isMajorAspect,
  ZODIAC_SIGNS,
} from '../utils/astro';
import { spring, staggerDelay, motionSafe, fadeIn } from '../config/animations';
import type { PlanetPosition } from './PlanetList';
import type { HousePosition } from './HouseTable';
import type { AspectData } from './AspectGrid';

interface ChartWheelProps {
  planets: PlanetPosition[];
  houses: HousePosition[];
  aspects: AspectData[];
  ascendant: number;
  midheaven: number;
}

export function ChartWheel({
  planets,
  houses,
  aspects,
  ascendant,
  midheaven,
}: ChartWheelProps) {
  const size = 600;
  const center = size / 2;
  const outerRadius = 280;
  const signRadius = 240;
  const planetRadius = 200;
  const houseRadius = 160;
  const innerRadius = 120;

  /**
   * Draw zodiac signs circle (outer ring)
   */
  function renderZodiacSigns() {
    return ZODIAC_SIGNS.map((sign, index) => {
      const startLongitude = index * 30;
      const midLongitude = startLongitude + 15;

      const startAngle = longitudeToAngle(startLongitude);
      const midAngle = longitudeToAngle(midLongitude);

      // Draw arc for sign boundary
      const startOuter = polarToCartesian(center, center, outerRadius, startAngle);
      const startSign = polarToCartesian(center, center, signRadius, startAngle);

      // Symbol position
      const symbolPos = polarToCartesian(center, center, (outerRadius + signRadius) / 2, midAngle);

      return (
        <motion.g
          key={sign}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: staggerDelay(index, 0.03), duration: 0.3 }}
        >
          {/* Sign boundary line */}
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

          {/* Sign symbol */}
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
              ...spring.bouncy
            }}
          >
            {getSignSymbol(sign)}
          </motion.text>
        </motion.g>
      );
    });
  }

  /**
   * Draw house divisions (inner ring)
   */
  function renderHouses() {
    return houses.map((house) => {
      const angle = longitudeToAngle(house.longitude);
      const outerPoint = polarToCartesian(center, center, signRadius, angle);
      const innerPoint = polarToCartesian(center, center, houseRadius, angle);

      // Calculate label position (middle of house)
      const nextHouse = houses[(house.house % 12)];
      const nextAngle = longitudeToAngle(nextHouse.longitude);
      const midAngle = (angle + nextAngle) / 2;
      const labelPos = polarToCartesian(center, center, (signRadius + houseRadius) / 2, midAngle);

      return (
        <g key={house.house}>
          {/* House cusp line */}
          <line
            x1={outerPoint.x}
            y1={outerPoint.y}
            x2={innerPoint.x}
            y2={innerPoint.y}
            stroke="currentColor"
            strokeWidth={[1, 4, 7, 10].includes(house.house) ? '2' : '1'}
            className={
              [1, 4, 7, 10].includes(house.house)
                ? 'text-primary'
                : 'text-muted-foreground opacity-40'
            }
          />

          {/* House number */}
          <text
            x={labelPos.x}
            y={labelPos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className="text-xs font-semibold text-muted-foreground"
          >
            {house.house}
          </text>
        </g>
      );
    });
  }

  /**
   * Draw planets
   */
  function renderPlanets() {
    return planets.map((planet, index) => {
      const angle = longitudeToAngle(planet.longitude);
      const pos = polarToCartesian(center, center, planetRadius, angle);

      return (
        <motion.g
          key={planet.name}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            delay: staggerDelay(index, 0.08) + 0.5,
            ...spring.bouncy
          }}
          whileHover={{ scale: 1.2 }}
          className="cursor-pointer"
        >
          {/* Planet symbol */}
          <motion.text
            x={pos.x}
            y={pos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className="text-2xl font-bold text-foreground"
            style={{
              filter: 'drop-shadow(0 0 2px white) drop-shadow(0 0 4px white)',
            }}
            whileHover={{
              filter: 'drop-shadow(0 0 4px white) drop-shadow(0 0 8px white)',
            }}
          >
            {getPlanetSymbol(planet.name)}
          </motion.text>

          {/* Retrograde indicator */}
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

  /**
   * Draw aspect lines between planets
   */
  function renderAspects() {
    // Only draw major aspects to avoid clutter
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
      const opacity = aspect.orb <= 2 ? 0.8 : aspect.orb <= 4 ? 0.5 : 0.3;

      return (
        <motion.line
          key={`${aspect.planet1}-${aspect.planet2}-${aspect.aspect}-${index}`}
          x1={pos1.x}
          y1={pos1.y}
          x2={pos2.x}
          y2={pos2.y}
          stroke={color}
          strokeWidth={aspect.orb <= 1 ? '2' : '1'}
          strokeOpacity={opacity}
          strokeDasharray={aspect.applying ? '0' : '4 2'}
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{
            pathLength: { delay: staggerDelay(index, 0.05) + 0.3, duration: 0.8 },
            opacity: { delay: staggerDelay(index, 0.05) + 0.3, duration: 0.3 }
          }}
        />
      );
    });
  }

  /**
   * Draw Ascendant (ASC) marker
   */
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

  /**
   * Draw Midheaven (MC) marker
   */
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
    <motion.div
      className="flex justify-center p-4"
      initial="hidden"
      animate="visible"
      variants={motionSafe(fadeIn)}
    >
      <motion.svg
        viewBox={`0 0 ${size} ${size}`}
        className="w-full max-w-2xl h-auto"
        style={{ maxHeight: '600px' }}
        initial={{ rotate: -90, scale: 0.8, opacity: 0 }}
        animate={{ rotate: 0, scale: 1, opacity: 1 }}
        transition={{ ...spring.gentle, duration: 1 }}
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
  );
}
