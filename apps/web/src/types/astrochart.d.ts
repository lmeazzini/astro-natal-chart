/**
 * TypeScript type definitions for @astrodraw/astrochart library
 * Based on: https://github.com/AstroDraw/AstroChart
 */

declare module '@astrodraw/astrochart' {
  export interface AstroChartPlanets {
    [planetName: string]: [number] | [number, number];
  }

  export interface AstroChartData {
    planets: AstroChartPlanets;
    cusps: number[];
  }

  export interface PointsOfInterest {
    As?: [number];
    Mc?: [number];
    Ic?: [number];
    Ds?: [number];
    [key: string]: [number] | undefined;
  }

  export interface AspectConfig {
    degree: number;
    orbit: number;
    color: string;
  }

  export interface ChartSettings {
    COLORS_SIGNS?: string[];
    COLORS_ASPECTS?: Record<string, string>;
    COLOR_POINTS?: string;
    COLOR_AXIS_FONT?: string;
    STROKE_ONLY?: boolean;
    CUSPS_STROKE?: number;
    SHIFT_IN_DEGREES?: number;
    ASPECTS?: Record<string, AspectConfig>;
    [key: string]:
      | string
      | number
      | boolean
      | string[]
      | Record<string, string | AspectConfig>
      | undefined;
  }

  export class Chart {
    /**
     * Create a new chart instance
     * @param elementId - ID of the HTML element to render the chart
     * @param width - Width of the chart in pixels
     * @param height - Height of the chart in pixels
     * @param settings - Optional chart settings
     */
    constructor(elementId: string, width: number, height: number, settings?: ChartSettings);

    /**
     * Generate a radix (natal) chart
     * @param data - Chart data with planets and cusps
     * @returns The Chart instance for chaining
     */
    radix(data: AstroChartData): Chart;

    /**
     * Generate a transit chart
     * @param data - Transit chart data
     * @returns The Chart instance for chaining
     */
    transit(data: AstroChartData): Chart;

    /**
     * Add points of interest (angular houses)
     * @param points - Points like Ascendant, MC, IC, Descendant
     * @returns The Chart instance for chaining
     */
    addPointsOfInterest(points: PointsOfInterest): Chart;

    /**
     * Calculate and display aspects between planets
     * @returns The Chart instance for chaining
     */
    aspects(): Chart;

    /**
     * Clear the chart
     * @returns The Chart instance for chaining
     */
    clear(): Chart;
  }

  const astrochart: {
    Chart: typeof Chart;
  };

  export default astrochart;
}
