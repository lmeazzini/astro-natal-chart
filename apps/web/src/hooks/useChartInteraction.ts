/**
 * Hook for managing chart interaction state (selection, hover, zoom, pan)
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import type { PlanetPosition } from '../components/PlanetList';
import type { HousePosition } from '../components/HouseTable';
import type { AspectData } from '../components/AspectGrid';

export type SelectedElementType = 'planet' | 'house' | 'aspect' | null;

export interface SelectedElement {
  type: SelectedElementType;
  id: string;
  data: PlanetPosition | HousePosition | AspectData;
}

export interface HoveredElement {
  type: 'planet' | 'house' | 'aspect';
  id: string;
  data: PlanetPosition | HousePosition | AspectData;
  position: { x: number; y: number };
}

export interface ZoomPanState {
  scale: number;
  translateX: number;
  translateY: number;
}

interface UseChartInteractionProps {
  planets: PlanetPosition[];
  houses: HousePosition[];
  aspects: AspectData[];
  onPlanetClick?: (planet: PlanetPosition) => void;
  onHouseClick?: (house: HousePosition) => void;
  onAspectClick?: (aspect: AspectData) => void;
}

interface UseChartInteractionReturn {
  // Selection state
  selectedElement: SelectedElement | null;
  selectPlanet: (planet: PlanetPosition) => void;
  selectHouse: (house: HousePosition) => void;
  selectAspect: (aspect: AspectData) => void;
  clearSelection: () => void;

  // Hover state
  hoveredElement: HoveredElement | null;
  setHoveredPlanet: (planet: PlanetPosition | null, position?: { x: number; y: number }) => void;
  setHoveredHouse: (house: HousePosition | null, position?: { x: number; y: number }) => void;
  setHoveredAspect: (aspect: AspectData | null, position?: { x: number; y: number }) => void;

  // Related elements (for highlighting)
  relatedPlanets: string[];
  relatedAspects: AspectData[];
  relatedHouses: number[];

  // Zoom/Pan state
  zoomPan: ZoomPanState;
  setZoom: (scale: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  setPan: (x: number, y: number) => void;

  // Keyboard handling
  handleKeyDown: (e: KeyboardEvent) => void;
}

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.0;
const ZOOM_STEP = 0.1;

export function useChartInteraction({
  planets,
  aspects,
  onPlanetClick,
  onHouseClick,
  onAspectClick,
}: UseChartInteractionProps): UseChartInteractionReturn {
  // Selection state
  const [selectedElement, setSelectedElement] = useState<SelectedElement | null>(null);

  // Hover state
  const [hoveredElement, setHoveredElement] = useState<HoveredElement | null>(null);

  // Zoom/Pan state
  const [zoomPan, setZoomPan] = useState<ZoomPanState>({
    scale: 1,
    translateX: 0,
    translateY: 0,
  });

  // Refs for cleanup
  const keyDownHandlerRef = useRef<((e: KeyboardEvent) => void) | null>(null);

  // Calculate related elements based on selection
  const getRelatedElements = useCallback(
    (selection: SelectedElement | null) => {
      if (!selection) {
        return { planets: [] as string[], aspects: [] as AspectData[], houses: [] as number[] };
      }

      if (selection.type === 'planet') {
        const planetName = (selection.data as PlanetPosition).name;
        const relatedAspects = aspects.filter(
          (a) => a.planet1 === planetName || a.planet2 === planetName
        );
        const relatedPlanetNames = relatedAspects.map((a) =>
          a.planet1 === planetName ? a.planet2 : a.planet1
        );
        const planetData = selection.data as PlanetPosition;
        return {
          planets: relatedPlanetNames,
          aspects: relatedAspects,
          houses: [planetData.house],
        };
      }

      if (selection.type === 'aspect') {
        const aspect = selection.data as AspectData;
        return {
          planets: [aspect.planet1, aspect.planet2],
          aspects: [aspect],
          houses: [] as number[],
        };
      }

      if (selection.type === 'house') {
        const houseNum = (selection.data as HousePosition).house;
        const planetsInHouse = planets.filter((p) => p.house === houseNum).map((p) => p.name);
        return {
          planets: planetsInHouse,
          aspects: [] as AspectData[],
          houses: [houseNum],
        };
      }

      return { planets: [] as string[], aspects: [] as AspectData[], houses: [] as number[] };
    },
    [planets, aspects]
  );

  const {
    planets: relatedPlanets,
    aspects: relatedAspects,
    houses: relatedHouses,
  } = getRelatedElements(selectedElement);

  // Selection handlers
  const selectPlanet = useCallback(
    (planet: PlanetPosition) => {
      setSelectedElement({
        type: 'planet',
        id: planet.name,
        data: planet,
      });
      onPlanetClick?.(planet);
    },
    [onPlanetClick]
  );

  const selectHouse = useCallback(
    (house: HousePosition) => {
      setSelectedElement({
        type: 'house',
        id: `house-${house.house}`,
        data: house,
      });
      onHouseClick?.(house);
    },
    [onHouseClick]
  );

  const selectAspect = useCallback(
    (aspect: AspectData) => {
      setSelectedElement({
        type: 'aspect',
        id: `${aspect.planet1}-${aspect.planet2}-${aspect.aspect}`,
        data: aspect,
      });
      onAspectClick?.(aspect);
    },
    [onAspectClick]
  );

  const clearSelection = useCallback(() => {
    setSelectedElement(null);
  }, []);

  // Hover handlers
  const setHoveredPlanet = useCallback(
    (planet: PlanetPosition | null, position?: { x: number; y: number }) => {
      if (planet && position) {
        setHoveredElement({
          type: 'planet',
          id: planet.name,
          data: planet,
          position,
        });
      } else {
        setHoveredElement(null);
      }
    },
    []
  );

  const setHoveredHouse = useCallback(
    (house: HousePosition | null, position?: { x: number; y: number }) => {
      if (house && position) {
        setHoveredElement({
          type: 'house',
          id: `house-${house.house}`,
          data: house,
          position,
        });
      } else {
        setHoveredElement(null);
      }
    },
    []
  );

  const setHoveredAspect = useCallback(
    (aspect: AspectData | null, position?: { x: number; y: number }) => {
      if (aspect && position) {
        setHoveredElement({
          type: 'aspect',
          id: `${aspect.planet1}-${aspect.planet2}-${aspect.aspect}`,
          data: aspect,
          position,
        });
      } else {
        setHoveredElement(null);
      }
    },
    []
  );

  // Zoom handlers
  const setZoom = useCallback((scale: number) => {
    setZoomPan((prev) => ({
      ...prev,
      scale: Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, scale)),
    }));
  }, []);

  const zoomIn = useCallback(() => {
    setZoomPan((prev) => ({
      ...prev,
      scale: Math.min(MAX_ZOOM, prev.scale + ZOOM_STEP),
    }));
  }, []);

  const zoomOut = useCallback(() => {
    setZoomPan((prev) => ({
      ...prev,
      scale: Math.max(MIN_ZOOM, prev.scale - ZOOM_STEP),
    }));
  }, []);

  const resetZoom = useCallback(() => {
    setZoomPan({
      scale: 1,
      translateX: 0,
      translateY: 0,
    });
  }, []);

  const setPan = useCallback((x: number, y: number) => {
    setZoomPan((prev) => ({
      ...prev,
      translateX: x,
      translateY: y,
    }));
  }, []);

  // Keyboard handler
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        clearSelection();
      } else if (e.key === '+' || e.key === '=') {
        zoomIn();
      } else if (e.key === '-') {
        zoomOut();
      } else if (e.key === '0') {
        resetZoom();
      }
    },
    [clearSelection, zoomIn, zoomOut, resetZoom]
  );

  // Store handler ref for cleanup
  keyDownHandlerRef.current = handleKeyDown;

  // Setup keyboard listener
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      keyDownHandlerRef.current?.(e);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  return {
    // Selection
    selectedElement,
    selectPlanet,
    selectHouse,
    selectAspect,
    clearSelection,

    // Hover
    hoveredElement,
    setHoveredPlanet,
    setHoveredHouse,
    setHoveredAspect,

    // Related elements
    relatedPlanets,
    relatedAspects,
    relatedHouses,

    // Zoom/Pan
    zoomPan,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
    setPan,

    // Keyboard
    handleKeyDown,
  };
}
