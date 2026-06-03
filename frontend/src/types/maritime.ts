// src/types/maritime.ts

// ─── Shared ───────────────────────────────────────────────────────────────────

export interface Waypoint {
  lat: number;
  lon: number;
  name?: string;
}

export type VesselType = 'cargo' | 'tanker' | 'container' | 'bulk' | 'passenger' | 'fishing';

export type RiskLevel = 'LOW' | 'MODERATE' | 'HIGH' | 'EXTREME';

export type PanelState = 'idle' | 'loading' | 'success' | 'error';

// ─── Request Payloads ─────────────────────────────────────────────────────────

export interface VoyageInput {
  origin: Waypoint;
  destination: Waypoint;
  departure_port: string;
  destination_port: string;
  vessel_name: string;
  vessel_speed_knots: number;
}

export interface VesselInput {
  name: string;
  default_stw_knots: number;
  base_fuel_rate_mt_per_day?: number;
}

export interface RouteWaypointInput {
  sequence_order: number;
  lat: number;
  lon: number;
  name?: string;
  vessel_heading_deg?: number;
}

export interface AnalyzeRouteRequest {
  vessel: VesselInput;
  departure_port: string;
  destination_port: string;
  waypoints: RouteWaypointInput[];
  save_to_db?: boolean;
}

export interface AnalyzeRouteApiResponse {
  voyage_id?: string | null;
  total_distance_nm: number;
  waypoints: Array<{
    sequence_order: number;
    lat: number;
    lon: number;
    weather: {
      wind_speed_knots: number;
      wind_direction_deg: number;
      wave_height_m: number;
    };
  }>;
  aggregate_fuel_mt: number;
  aggregate_delay_hours: number;
  planned_eta_hours: number;
  weather_alerts: string[];
  max_risk_score: number;
}

export interface WeatherConditions {
  wind_speed_knots: number;
  wind_direction_deg: number;
  wave_height_m: number;
  current_speed_knots: number;
  current_direction_deg: number;
}

export interface RiskPredictionInput {
  weather: WeatherConditions;
  vessel_heading_deg: number;
}

export interface SpeedPredictionInput {
  stw_knots: number;
  weather: WeatherConditions;
  vessel_heading_deg: number;
  distance_nm: number;
}

/** FastAPI PredictRiskResponse */
export interface PredictRiskApiResponse {
  risk_score: number;
  risk_level: string;
  relative_heading_deg: number;
}

/** FastAPI PredictSpeedResponse */
export interface PredictSpeedApiResponse {
  effective_sog_knots: number;
  delay_hours: number;
}

// ─── Response Shapes ──────────────────────────────────────────────────────────

export interface RouteWaypoint {
  lat: number;
  lon: number;
  eta?: string;
  weather_summary?: string;
}

export interface RouteAnalysisResult {
  route_id: string;
  total_distance_nm: number;
  estimated_duration_hours: number;
  waypoints: RouteWaypoint[];
  overall_risk_score: number;     // 0–1
  recommended: boolean;
  summary: string;
}

export interface RiskPredictionResult {
  risk_score: number;             // 0–1
  risk_level: RiskLevel;
  contributing_factors: string[];
  recommendations: string[];
  confidence: number;             // 0–1
}

export interface SpeedPredictionResult {
  recommended_speed_knots: number;
  fuel_efficiency_score: number;  // 0–1
  weather_penalty_knots: number;
  safety_margin: string;
  reasoning: string;
}

export interface HealthResponse {
  status: string;
  version?: string;
}

// ─── UI State ─────────────────────────────────────────────────────────────────

export interface ApiError {
  message: string;
  status?: number;
}

export interface MaritimeApiState {
  panelState: PanelState;
  error: ApiError | null;
  routeResult: RouteAnalysisResult | null;
  riskResult: RiskPredictionResult | null;
  speedResult: SpeedPredictionResult | null;
}