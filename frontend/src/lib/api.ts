// src/lib/api.ts

import type {
    HealthResponse,
    VoyageInput,
    AnalyzeRouteRequest,
    AnalyzeRouteApiResponse,
    RouteAnalysisResult,
    RiskPredictionInput,
    RiskPredictionResult,
    SpeedPredictionInput,
    SpeedPredictionResult,
    PredictRiskApiResponse,
    PredictSpeedApiResponse,
  } from '@/types/maritime';
  
  // ─── Config ───────────────────────────────────────────────────────────────────
  
  const BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ?? 'https://maritime-weather-routing.onrender.com';

  function formatErrorDetail(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    return JSON.stringify(detail, null, 2);
  }

  function mapRiskResponse(data: PredictRiskApiResponse): RiskPredictionResult {
    const level = data.risk_level.toLowerCase();
    const risk_level =
      level === 'safe' ? 'LOW' : level === 'dangerous' ? 'HIGH' : 'MODERATE';
    return {
      risk_score: data.risk_score / 100,
      risk_level,
      contributing_factors: [`Relative heading: ${data.relative_heading_deg.toFixed(1)}°`],
      recommendations: [],
      confidence: 1,
    };
  }

  export function buildAnalyzeRouteRequest(
    input: VoyageInput,
    vessel_heading_deg: number,
  ): AnalyzeRouteRequest {
    return {
      vessel: {
        name: input.vessel_name,
        default_stw_knots: input.vessel_speed_knots,
      },
      departure_port: input.departure_port,
      destination_port: input.destination_port,
      waypoints: [
        {
          sequence_order: 0,
          lat: input.origin.lat,
          lon: input.origin.lon,
          name: input.origin.name,
          vessel_heading_deg,
        },
        {
          sequence_order: 1,
          lat: input.destination.lat,
          lon: input.destination.lon,
          name: input.destination.name,
        },
      ],
      save_to_db: false,
    };
  }

  function mapRouteResponse(data: AnalyzeRouteApiResponse): RouteAnalysisResult {
    const alerts = data.weather_alerts?.length
      ? data.weather_alerts.join('; ')
      : `Fuel ${data.aggregate_fuel_mt.toFixed(1)} mt · delay ${data.aggregate_delay_hours.toFixed(1)} h`;
    return {
      route_id: data.voyage_id ?? 'local',
      total_distance_nm: data.total_distance_nm,
      estimated_duration_hours: data.planned_eta_hours,
      waypoints: data.waypoints.map((wp) => ({
        lat: wp.lat,
        lon: wp.lon,
        weather_summary: `Wind ${wp.weather.wind_speed_knots} kn · waves ${wp.weather.wave_height_m} m`,
      })),
      overall_risk_score: data.max_risk_score / 100,
      recommended: data.max_risk_score < 50,
      summary: alerts,
    };
  }

  function mapSpeedResponse(
    data: PredictSpeedApiResponse,
    stw_knots: number,
  ): SpeedPredictionResult {
    return {
      recommended_speed_knots: data.effective_sog_knots,
      fuel_efficiency_score: 0.8,
      weather_penalty_knots: Math.max(0, stw_knots - data.effective_sog_knots),
      safety_margin: data.delay_hours > 0 ? 'Reduced' : 'Normal',
      reasoning: `Estimated delay: ${data.delay_hours.toFixed(2)} h`,
    };
  }
  
  // ─── Core fetch wrapper ───────────────────────────────────────────────────────
  
  async function request<T>(path: string, options?: RequestInit): Promise<T> {
    let res: Response;
  
    try {
      res = await fetch(`${BASE_URL}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
    } catch {
      throw {
        message: 'Cannot reach the API server. Check your connection or try again later.',
        status: 0,
      };
    }
  
    if (!res.ok) {
      let message = `${res.status} ${res.statusText}`;
      try {
        const body = await res.json();
        if (body?.detail) message = formatErrorDetail(body.detail);
      } catch {}
      throw { message, status: res.status };
    }
  
    return res.json() as Promise<T>;
  }
  
  // ─── API methods ──────────────────────────────────────────────────────────────
  
  export const api = {
    health(): Promise<HealthResponse> {
      return request<HealthResponse>('/health');
    },
  
    async analyzeRoute(
      payload: AnalyzeRouteRequest,
    ): Promise<RouteAnalysisResult> {
      const data = await request<AnalyzeRouteApiResponse>('/api/v1/analyze-route', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      return mapRouteResponse(data);
    },
  
    async predictRisk(payload: RiskPredictionInput): Promise<RiskPredictionResult> {
      const data = await request<PredictRiskApiResponse>('/api/v1/predict-risk', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      return mapRiskResponse(data);
    },

    async predictSpeed(payload: SpeedPredictionInput): Promise<SpeedPredictionResult> {
      const data = await request<PredictSpeedApiResponse>('/api/v1/predict-speed', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      return mapSpeedResponse(data, payload.stw_knots);
    },
  };