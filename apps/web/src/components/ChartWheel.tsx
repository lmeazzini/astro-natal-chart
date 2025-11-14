/**
 * Chart Wheel component - circular birth chart visualization
 */

import {
  getPlanetSymbol,
  getSignSymbol,
  longitudeToAngle,
  polarToCartesian,
  getAspectColor,
  isMajorAspect,
  ZODIAC_SIGNS,
} from '../utils/astro';
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
      const endAngle = longitudeToAngle(startLongitude + 30);
      const midAngle = longitudeToAngle(midLongitude);

      // Draw arc for sign boundary
      const startOuter = polarToCartesian(center, center, outerRadius, startAngle);
      const startSign = polarToCartesian(center, center, signRadius, startAngle);

      // Symbol position
      const symbolPos = polarToCartesian(center, center, (outerRadius + signRadius) / 2, midAngle);

      return (
        <g key={sign}>
          {/* Sign boundary line */}
          <line
            x1={startOuter.x}
            y1={startOuter.y}
            x2={startSign.x}
            y2={startSign.y}
            stroke="currentColor"
            strokeWidth="1"
            className="text-border opacity-50"
          />

          {/* Sign symbol */}
          <text
            x={symbolPos.x}
            y={symbolPos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className="text-foreground text-xl font-semibold"
          >
            {getSignSymbol(sign)}
          </text>
        </g>
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
    return planets.map((planet) => {
      const angle = longitudeToAngle(planet.longitude);
      const pos = polarToCartesian(center, center, planetRadius, angle);

      return (
        <g key={planet.name}>
          {/* Planet symbol */}
          <text
            x={pos.x}
            y={pos.y}
            textAnchor="middle"
            dominantBaseline="central"
            className="text-2xl font-bold text-foreground"
            style={{
              filter: 'drop-shadow(0 0 2px white) drop-shadow(0 0 4px white)',
            }}
          >
            {getPlanetSymbol(planet.name)}
          </text>

          {/* Retrograde indicator */}
          {planet.retrograde && (
            <text
              x={pos.x + 15}
              y={pos.y - 12}
              textAnchor="middle"
              className="text-[10px] font-bold text-destructive"
            >
              R
            </text>
          )}
        </g>
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
        <line
          key={`${aspect.planet1}-${aspect.planet2}-${aspect.aspect}-${index}`}
          x1={pos1.x}
          y1={pos1.y}
          x2={pos2.x}
          y2={pos2.y}
          stroke={color}
          strokeWidth={aspect.orb <= 1 ? '2' : '1'}
          strokeOpacity={opacity}
          strokeDasharray={aspect.applying ? '0' : '4 2'}
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
    <div className="flex justify-center p-4">
      <svg
        viewBox={`0 0 ${size} ${size}`}
        className="w-full max-w-2xl h-auto"
        style={{ maxHeight: '600px' }}
      >
        {/* Background */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius}
          fill="currentColor"
          className="text-background"
        />

        {/* Outer circle */}
        <circle
          cx={center}
          cy={center}
          r={outerRadius}
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className="text-border"
        />

        {/* Sign circle */}
        <circle
          cx={center}
          cy={center}
          r={signRadius}
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-border opacity-50"
        />

        {/* House circle */}
        <circle
          cx={center}
          cy={center}
          r={houseRadius}
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-border opacity-50"
        />

        {/* Inner circle */}
        <circle
          cx={center}
          cy={center}
          r={innerRadius}
          fill="currentColor"
          stroke="currentColor"
          strokeWidth="1"
          className="text-muted/20 stroke-border opacity-50"
        />

        {/* Render elements in layers */}
        {renderAspects()}
        {renderZodiacSigns()}
        {renderHouses()}
        {renderAscendant()}
        {renderMidheaven()}
        {renderPlanets()}
      </svg>
    </div>
  );
}
