/**
 * ChartWheelAstro - Professional natal chart visualization using AstroChart library
 * Replaces the custom SVG implementation with a professional astrology library
 */

import { useEffect, useRef, useState } from 'react';
import * as AstroChartLib from '@astrodraw/astrochart';
import {
  convertToAstroChartFormat,
  extractPointsOfInterest,
  calculateDynamicShift,
  type ChartData,
} from '@/utils/astroChartAdapter';

interface ChartWheelAstroProps {
  chartData: ChartData;
  width?: number;
  height?: number;
}

export function ChartWheelAstro({
  chartData,
  width = 600,
  height = 600,
}: ChartWheelAstroProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartInstanceRef = useRef<any>(null);
  const isRenderingRef = useRef<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !chartData) {
      console.warn('[ChartWheelAstro] Container or chartData not available');
      return;
    }

    // Prevent duplicate renders
    if (isRenderingRef.current) {
      console.warn('[ChartWheelAstro] Already rendering, skipping...');
      return;
    }

    isRenderingRef.current = true;
    console.log('[ChartWheelAstro] Initializing chart...');
    console.log('[ChartWheelAstro] chartData:', chartData);

    // Clear any existing content
    if (chartContainerRef.current) {
      chartContainerRef.current.innerHTML = '';
    }

    // Generate unique ID for the chart container
    const chartId = `astrochart-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    chartContainerRef.current.id = chartId;

    try {
      // Convert our data format to AstroChart format
      const astroData = convertToAstroChartFormat(chartData);
      const pointsOfInterest = extractPointsOfInterest(chartData);

      console.log('[ChartWheelAstro] Converted data:', astroData);
      console.log('[ChartWheelAstro] Points of interest:', pointsOfInterest);

      // Access the Chart class correctly based on the library export
      const AstroChart = (AstroChartLib as any).Chart || (AstroChartLib as any).default?.Chart;

      if (!AstroChart) {
        throw new Error('AstroChart library not loaded correctly');
      }

      console.log('[ChartWheelAstro] Creating chart instance...');

      // Calculate dynamic shift to position Ascendant at 9 o'clock (left)
      const dynamicShift = calculateDynamicShift(chartData);
      console.log('[ChartWheelAstro] Ascendant longitude:', chartData.chart_info?.ascendant || chartData.houses[0]?.cusp);
      console.log('[ChartWheelAstro] Calculated dynamic shift:', dynamicShift);

      // Create chart instance with custom settings
      const settings = {
        // Position Ascendant at 9 o'clock (left of the circle) using dynamic calculation
        // This shift is calculated based on the actual Ascendant position in this chart
        SHIFT_IN_DEGREES: dynamicShift,

        // Aspect configurations with colors
        ASPECTS: {
          conjunction: { degree: 0, orbit: 10, color: '#5757e8' },
          opposition: { degree: 180, orbit: 10, color: '#d20000' },
          trine: { degree: 120, orbit: 8, color: '#27AE60' },
          square: { degree: 90, orbit: 8, color: '#d20000' },
          sextile: { degree: 60, orbit: 6, color: '#27AE60' },
        },
      };

      const chart = new AstroChart(chartId, width, height, settings);

      console.log('[ChartWheelAstro] Rendering radix chart...');

      // Generate radix (natal) chart - returns radix object
      // The radix() method automatically draws: background, universe, points, axis, cusps
      const radix = chart.radix(astroData);

      console.log('[ChartWheelAstro] Radix chart created');

      // Calculate and display aspects (lines between planets)
      console.log('[ChartWheelAstro] Calculating aspects...');
      radix.aspects();
      console.log('[ChartWheelAstro] Aspects calculated');

      console.log('[ChartWheelAstro] Chart rendered successfully!');

      // Store reference for cleanup
      chartInstanceRef.current = chart;
      setError(null);
      isRenderingRef.current = false;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('[ChartWheelAstro] Error rendering chart:', err);
      setError(errorMessage);
      isRenderingRef.current = false;
    }

    // Cleanup function
    return () => {
      console.log('[ChartWheelAstro] Cleaning up...');
      isRenderingRef.current = false;
      if (chartInstanceRef.current) {
        try {
          if (typeof chartInstanceRef.current.clear === 'function') {
            chartInstanceRef.current.clear();
          }
        } catch (err) {
          console.error('[ChartWheelAstro] Error clearing chart:', err);
        }
        chartInstanceRef.current = null;
      }
      // Clear container content
      if (chartContainerRef.current) {
        chartContainerRef.current.innerHTML = '';
      }
    };
  }, [chartData, width, height]);

  if (error) {
    return (
      <div className="flex justify-center items-center bg-background p-4 rounded-lg border border-destructive text-destructive">
        <div className="text-center">
          <p className="font-semibold">Erro ao renderizar mapa natal</p>
          <p className="text-sm mt-2">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center bg-background p-4 rounded-lg border border-border">
      <div
        ref={chartContainerRef}
        className="astrochart-container"
        style={{ minHeight: height, minWidth: width }}
      />
    </div>
  );
}
