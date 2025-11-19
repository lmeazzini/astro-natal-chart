/**
 * Adapter to convert our backend chart data format to AstroChart library format
 */

export interface PlanetData {
  name: string;
  longitude: number;
  latitude?: number;
  speed?: number;
  retrograde?: boolean;
  sign?: string;
  degree?: number;
  house?: number;
}

export interface HouseData {
  number?: number;
  house?: number;
  cusp: number;
  sign?: string;
}

export interface ChartData {
  planets: PlanetData[];
  houses: HouseData[];
  chart_info?: {
    ascendant?: number;
    mc?: number;
    ic?: number;
    descendant?: number;
  };
}

export interface AstroChartData {
  planets: Record<string, [number] | [number, number]>;
  cusps: number[];
}

export interface AstroChartPointsOfInterest {
  As?: [number];
  Mc?: [number];
  Ic?: [number];
  Ds?: [number];
}

/**
 * Planet name mapping from our backend to AstroChart expected names
 */
const PLANET_NAME_MAP: Record<string, string> = {
  Sun: 'Sun',
  Moon: 'Moon',
  Mercury: 'Mercury',
  Venus: 'Venus',
  Mars: 'Mars',
  Jupiter: 'Jupiter',
  Saturn: 'Saturn',
  Uranus: 'Uranus',
  Neptune: 'Neptune',
  Pluto: 'Pluto',
  'North Node': 'NNode',
  'South Node': 'SNode',
  Chiron: 'Chiron',
  Lilith: 'Lilith',
};

/**
 * Convert our chart data to AstroChart format
 */
export function convertToAstroChartFormat(data: ChartData): AstroChartData {
  // Convert planets
  const planets: Record<string, [number] | [number, number]> = {};

  data.planets.forEach((planet) => {
    const astroChartName = PLANET_NAME_MAP[planet.name];
    if (astroChartName) {
      // AstroChart format: [longitude] or [longitude, retrograde_indicator]
      // Retrograde indicator: positive value like 0.2 means retrograde
      if (planet.retrograde) {
        planets[astroChartName] = [planet.longitude, 0.2];
      } else {
        planets[astroChartName] = [planet.longitude];
      }
    }
  });

  // Convert houses (cusps)
  // Sort by house number to ensure correct order
  const sortedHouses = [...data.houses].sort((a, b) => {
    const houseA = a.number || a.house || 0;
    const houseB = b.number || b.house || 0;
    return houseA - houseB;
  });

  const cusps = sortedHouses.map((house) => house.cusp);

  return {
    planets,
    cusps,
  };
}

/**
 * Extract points of interest (angular houses) from chart data
 */
export function extractPointsOfInterest(data: ChartData): AstroChartPointsOfInterest {
  const poi: AstroChartPointsOfInterest = {};

  if (data.chart_info?.ascendant !== undefined) {
    poi.As = [data.chart_info.ascendant];
  }

  if (data.chart_info?.mc !== undefined) {
    poi.Mc = [data.chart_info.mc];
  }

  if (data.chart_info?.ic !== undefined) {
    poi.Ic = [data.chart_info.ic];
  }

  if (data.chart_info?.descendant !== undefined) {
    poi.Ds = [data.chart_info.descendant];
  }

  // Fallback: if chart_info not available, extract from cusps
  if (!poi.As && data.houses.length >= 12) {
    const sortedHouses = [...data.houses].sort((a, b) => {
      const houseA = a.number || a.house || 0;
      const houseB = b.number || b.house || 0;
      return houseA - houseB;
    });

    poi.As = [sortedHouses[0].cusp]; // House 1 = Ascendant
    poi.Ic = [sortedHouses[3].cusp]; // House 4 = IC
    poi.Ds = [sortedHouses[6].cusp]; // House 7 = Descendant
    poi.Mc = [sortedHouses[9].cusp]; // House 10 = MC
  }

  return poi;
}

/**
 * Calculate dynamic shift to position Ascendant at 0° (top of chart)
 *
 * AstroChart library positioning:
 * - Default SHIFT_IN_DEGREES = 180° puts 0° at left (9 o'clock)
 * - We want Ascendant at top (12 o'clock / 0° position)
 * - Formula: shift = 90° - ascendant_longitude
 *
 * @param data Chart data containing ascendant position
 * @returns Calculated shift in degrees
 */
export function calculateDynamicShift(data: ChartData): number {
  // Get Ascendant position (longitude in degrees 0-360)
  let ascendant = data.chart_info?.ascendant;

  // Fallback: get from first house cusp
  if (ascendant === undefined && data.houses.length >= 12) {
    const sortedHouses = [...data.houses].sort((a, b) => {
      const houseA = a.number || a.house || 0;
      const houseB = b.number || b.house || 0;
      return houseA - houseB;
    });
    ascendant = sortedHouses[0].cusp; // House 1 = Ascendant
  }

  // If still no ascendant, return default shift
  if (ascendant === undefined) {
    console.warn('[astroChartAdapter] No Ascendant found, using default shift 180°');
    return 180;
  }

  // Calculate shift to position Ascendant at top (90° in AstroChart coordinate system)
  // AstroChart rotates counter-clockwise, so we subtract ascendant from 90°
  const shift = 90 - ascendant;

  return shift;
}
