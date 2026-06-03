// src/lib/api.ts

import type {
    HealthResponse,
    VoyageInput,
    RouteAnalysisResult,
    RiskPredictionInput,
    RiskPredictionResult,
    SpeedPredictionInput,
    SpeedPredictionResult,
  } from '@/types/maritime';
  
  // ─── Config ───────────────────────────────────────────────────────────────────
  
  const BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ?? 'http://127.0.0.1:8000';

  function formatErrorDetail(detail: unknown): string {
    if (typeof detail === 'string') return detail;
    return JSON.stringify(detail, null, 2);
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
        message: 'Cannot reach the backend. Is it running on port 8000?',
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
  
    analyzeRoute(payload: VoyageInput): Promise<RouteAnalysisResult> {
      return request<RouteAnalysisResult>('/api/v1/analyze-route', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  
    predictRisk(payload: RiskPredictionInput): Promise<RiskPredictionResult> {
      return request<RiskPredictionResult>('/api/v1/predict-risk', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  
    predictSpeed(payload: SpeedPredictionInput): Promise<SpeedPredictionResult> {
      return request<SpeedPredictionResult>('/api/v1/predict-speed', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    },
  };