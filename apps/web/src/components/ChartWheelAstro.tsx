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

      // Create chart instance with aspect settings
      const settings = {
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
      const radix = chart.radix(astroData);

      console.log('[ChartWheelAstro] Radix object:', radix);

      // Draw all chart elements explicitly
      console.log('[ChartWheelAstro] Drawing background...');
      if (typeof radix.drawBg === 'function') {
        radix.drawBg();
      }

      console.log('[ChartWheelAstro] Drawing universe (zodiac signs)...');
      if (typeof radix.drawUniverse === 'function') {
        radix.drawUniverse();
      }

      console.log('[ChartWheelAstro] Drawing points (planets)...');
      if (typeof radix.drawPoints === 'function') {
        radix.drawPoints();
      }

      console.log('[ChartWheelAstro] Drawing axis...');
      if (typeof radix.drawAxis === 'function') {
        radix.drawAxis();
      }

      console.log('[ChartWheelAstro] Drawing cusps (houses)...');
      if (typeof radix.drawCusps === 'function') {
        radix.drawCusps();
      }

      // Add angular houses (As, Mc, Ic, Ds)
      if (Object.keys(pointsOfInterest).length > 0) {
        console.log('[ChartWheelAstro] Adding points of interest...');
        radix.addPointsOfInterest(pointsOfInterest);
      }

      // Calculate and display aspects
      console.log('[ChartWheelAstro] Calculating and drawing aspects...');
      const aspectsResult = radix.aspects();
      console.log('[ChartWheelAstro] Aspects result:', aspectsResult);

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
