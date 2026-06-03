// src/hooks/useMaritimeApi.ts

import { useState, useCallback } from 'react';
import { api, buildAnalyzeRouteRequest } from '@/lib/api';
import type { VoyageInput, MaritimeApiState, WeatherConditions } from '@/types/maritime';

const DEFAULT_WEATHER: WeatherConditions = {
  wind_speed_knots: 15,
  wind_direction_deg: 45,
  wave_height_m: 1.5,
  current_speed_knots: 0.5,
  current_direction_deg: 90,
};

function bearingDeg(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const φ1 = toRad(lat1);
  const φ2 = toRad(lat2);
  const Δλ = toRad(lon2 - lon1);
  const y = Math.sin(Δλ) * Math.cos(φ2);
  const x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ);
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360;
}

function distanceNm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const toRad = (d: number) => (d * Math.PI) / 180;
  const φ1 = toRad(lat1);
  const φ2 = toRad(lat2);
  const Δφ = toRad(lat2 - lat1);
  const Δλ = toRad(lon2 - lon1);
  const a =
    Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
  return 3440.065 * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const INITIAL_STATE: MaritimeApiState = {
  panelState: 'idle',
  error: null,
  routeResult: null,
  riskResult: null,
  speedResult: null,
};

export function useMaritimeApi() {
  const [state, setState] = useState<MaritimeApiState>(INITIAL_STATE);

  const analyze = useCallback(async (input: VoyageInput) => {
    setState({ ...INITIAL_STATE, panelState: 'loading' });

    const vessel_heading_deg = bearingDeg(
      input.origin.lat,
      input.origin.lon,
      input.destination.lat,
      input.destination.lon,
    );
    const distance_nm = distanceNm(
      input.origin.lat,
      input.origin.lon,
      input.destination.lat,
      input.destination.lon,
    );
    const weather = DEFAULT_WEATHER;

    try {
      const [routeResult, riskResult, speedResult] = await Promise.all([
        api.analyzeRoute(buildAnalyzeRouteRequest(input, vessel_heading_deg)),
        api.predictRisk({ weather, vessel_heading_deg }),
        api.predictSpeed({
          stw_knots: input.vessel_speed_knots,
          weather,
          vessel_heading_deg,
          distance_nm,
        }),
      ]);

      setState({
        panelState: 'success',
        error: null,
        routeResult,
        riskResult,
        speedResult,
      });
    } catch (err: unknown) {
      const apiErr = err as { message?: unknown; status?: number };
      const raw = apiErr?.message;
      const message =
        typeof raw === 'string'
          ? raw
          : raw != null
            ? JSON.stringify(raw, null, 2)
            : 'An unexpected error occurred.';
      setState({
        ...INITIAL_STATE,
        panelState: 'error',
        error: { message, status: apiErr?.status },
      });
    }
  }, []);

  const reset = useCallback(() => setState(INITIAL_STATE), []);

  return { ...state, analyze, reset };
}
