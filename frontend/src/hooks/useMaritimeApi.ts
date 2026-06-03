// src/hooks/useMaritimeApi.ts

import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import type { VoyageInput, MaritimeApiState } from '@/types/maritime';

// ─── Initial state ────────────────────────────────────────────────────────────

const INITIAL_STATE: MaritimeApiState = {
  panelState: 'idle',
  error: null,
  routeResult: null,
  riskResult: null,
  speedResult: null,
};

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useMaritimeApi() {
  const [state, setState] = useState<MaritimeApiState>(INITIAL_STATE);

  const analyze = useCallback(async (input: VoyageInput) => {
    setState({ ...INITIAL_STATE, panelState: 'loading' });

    // Build the shared fields needed by risk + speed endpoints
    const sharedFields = {
      lat: input.origin.lat,
      lon: input.origin.lon,
      timestamp: input.departure_time,
      vessel_type: input.vessel_type,
      vessel_draft_meters: input.vessel_draft_meters,
    };

    try {
      const [routeResult, riskResult, speedResult] = await Promise.all([
        api.analyzeRoute(input),
        api.predictRisk(sharedFields),
        api.predictSpeed({
          ...sharedFields,
          target_speed_knots: input.vessel_speed_knots,
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