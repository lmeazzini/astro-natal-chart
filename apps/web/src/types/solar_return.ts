/**
 * Solar Return types for API responses.
 */

export interface SolarReturnLocation {
  latitude: number;
  longitude: number;
  city: string;
  country: string;
  timezone: string;
}

export interface SolarReturnPlanet {
  name: string;
  longitude: number;
  sign: string;
  degree: number;
  house: number;
  retrograde: boolean;
}

export interface SolarReturnHouse {
  number: number;
  cusp: number;
  sign: string;
}

export interface SolarReturnAspect {
  planet1: string;
  planet2: string;
  aspect: string;
  angle: number;
  orb: number;
}

export interface SRToNatalAspect {
  sr_planet: string;
  natal_planet: string;
  aspect: string;
  angle: number;
  orb: number;
  is_major: boolean;
}

export interface SolarReturnChart {
  return_datetime: string;
  return_year: number;
  location: SolarReturnLocation;
  natal_sun_longitude: number;
  return_sun_longitude: number;
  planets: SolarReturnPlanet[];
  houses: SolarReturnHouse[];
  aspects: SolarReturnAspect[];
  ascendant: number;
  ascendant_sign: string;
  ascendant_degree: number;
  midheaven: number;
  midheaven_sign: string;
  midheaven_degree: number;
  sun_house: number;
}

export interface SolarReturnComparison {
  sr_asc_in_natal_house: number;
  sr_mc_in_natal_house: number;
  sr_planets_in_natal_houses: Record<string, number>;
  natal_planets_in_sr_houses: Record<string, number>;
  key_aspects: SRToNatalAspect[];
}

export interface SolarReturnResponse {
  chart: SolarReturnChart;
  comparison: SolarReturnComparison | null;
}

export interface SolarReturnInterpretation {
  title: string;
  sr_ascendant_sign: string;
  sr_sun_house: number;
  general_introduction: string;
  general_interpretation: string;
  ascendant_interpretation: string;
  sun_house_interpretation: string;
}

export interface SolarReturnListResponse {
  returns: SolarReturnResponse[];
  start_year: number;
  end_year: number;
}
