/**
 * ChartWheelAstro - Professional natal chart visualization using AstroChart library
 * Replaces the custom SVG implementation with a professional astrology library
 */

import { useEffect, useRef } from 'react';
import astrochart from '@astrodraw/astrochart';
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

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Generate unique ID for the chart container
    const chartId = `astrochart-${Math.random().toString(36).substr(2, 9)}`;
    chartContainerRef.current.id = chartId;

    try {
      // Convert our data format to AstroChart format
      const astroData = convertToAstroChartFormat(chartData);
      const pointsOfInterest = extractPointsOfInterest(chartData);

      // Create chart instance
      const chart = new astrochart.Chart(chartId, width, height);

      // Generate radix (natal) chart
      chart.radix(astroData);

      // Add angular houses (As, Mc, Ic, Ds)
      if (Object.keys(pointsOfInterest).length > 0) {
        chart.addPointsOfInterest(pointsOfInterest);
      }

      // Calculate and display aspects
      chart.aspects();

      // Store reference for cleanup
      chartInstanceRef.current = chart;
    } catch (error) {
      console.error('Error rendering AstroChart:', error);
    }

    // Cleanup function
    return () => {
      if (chartInstanceRef.current) {
        try {
          chartInstanceRef.current.clear();
        } catch (error) {
          console.error('Error clearing chart:', error);
        }
      }
    };
  }, [chartData, width, height]);

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
