/**
 * ChartWheelAstro - Professional natal chart visualization using AstroChart library
 * Replaces the custom SVG implementation with a professional astrology library
 */

import { useEffect, useRef, useState } from 'react';
import * as AstroChartLib from '@astrodraw/astrochart';
import {
  convertToAstroChartFormat,
  extractPointsOfInterest,
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
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current || !chartData) {
      console.warn('[ChartWheelAstro] Container or chartData not available');
      return;
    }

    console.log('[ChartWheelAstro] Initializing chart...');
    console.log('[ChartWheelAstro] chartData:', chartData);

    // Generate unique ID for the chart container
    const chartId = `astrochart-${Date.now()}`;
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

      // Create chart instance
      const chart = new AstroChart(chartId, width, height);

      console.log('[ChartWheelAstro] Rendering radix chart...');

      // Generate radix (natal) chart - returns radix object
      const radix = chart.radix(astroData);

      // Add angular houses (As, Mc, Ic, Ds)
      if (Object.keys(pointsOfInterest).length > 0) {
        console.log('[ChartWheelAstro] Adding points of interest...');
        radix.addPointsOfInterest(pointsOfInterest);
      }

      // Calculate and display aspects
      console.log('[ChartWheelAstro] Calculating aspects...');
      radix.aspects();

      console.log('[ChartWheelAstro] Chart rendered successfully!');

      // Store reference for cleanup
      chartInstanceRef.current = chart;
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      console.error('[ChartWheelAstro] Error rendering chart:', err);
      setError(errorMessage);
    }

    // Cleanup function
    return () => {
      if (chartInstanceRef.current) {
        try {
          chartInstanceRef.current.clear();
        } catch (err) {
          console.error('[ChartWheelAstro] Error clearing chart:', err);
        }
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
