'use client';

import { useState, type FormEvent } from 'react';
import { useMaritimeApi } from '@/hooks/useMaritimeApi';
import type { VesselType, VoyageInput } from '@/types/maritime';

function renderText(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  return JSON.stringify(value, null, 2);
}

const VESSEL_TYPES: VesselType[] = [
  'cargo',
  'tanker',
  'container',
  'bulk',
  'passenger',
  'fishing',
];

export default function HomePage() {
  const { panelState, error, routeResult, riskResult, speedResult, analyze, reset } =
    useMaritimeApi();

  const [originLat, setOriginLat] = useState('1.29');
  const [originLon, setOriginLon] = useState('103.85');
  const [destLat, setDestLat] = useState('22.3');
  const [destLon, setDestLon] = useState('114.2');
  const [departureTime, setDepartureTime] = useState('2024-06-01T08:00');
  const [vesselType, setVesselType] = useState<VesselType>('cargo');
  const [speed, setSpeed] = useState('12');
  const [draft, setDraft] = useState('10');

  const loading = panelState === 'loading';

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const input: VoyageInput = {
      origin: { lat: Number(originLat), lon: Number(originLon) },
      destination: { lat: Number(destLat), lon: Number(destLon) },
      departure_time: new Date(departureTime).toISOString(),
      vessel_type: vesselType,
      vessel_speed_knots: Number(speed),
      vessel_draft_meters: Number(draft),
    };
    void analyze(input);
  }

  return (
    <main>
      <h1>Maritime route planner</h1>

      <form onSubmit={handleSubmit}>
        <div className="row2">
          <label>
            Origin lat
            <input value={originLat} onChange={(e) => setOriginLat(e.target.value)} required />
          </label>
          <label>
            Origin lon
            <input value={originLon} onChange={(e) => setOriginLon(e.target.value)} required />
          </label>
        </div>
        <div className="row2">
          <label>
            Destination lat
            <input value={destLat} onChange={(e) => setDestLat(e.target.value)} required />
          </label>
          <label>
            Destination lon
            <input value={destLon} onChange={(e) => setDestLon(e.target.value)} required />
          </label>
        </div>
        <label>
          Departure (local)
          <input
            type="datetime-local"
            value={departureTime}
            onChange={(e) => setDepartureTime(e.target.value)}
            required
          />
        </label>
        <label>
          Vessel type
          <select value={vesselType} onChange={(e) => setVesselType(e.target.value as VesselType)}>
            {VESSEL_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </label>
        <div className="row2">
          <label>
            Speed (kn)
            <input value={speed} onChange={(e) => setSpeed(e.target.value)} required />
          </label>
          <label>
            Draft (m)
            <input value={draft} onChange={(e) => setDraft(e.target.value)} required />
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Analyzing…' : 'Analyze voyage'}
        </button>
        <button type="button" onClick={reset} disabled={loading}>
          Reset
        </button>
      </form>

      {error && (
        <section className="error">
          <h2>Error</h2>
          <pre>{renderText(error.message) || 'An unexpected error occurred.'}</pre>
          {error.status != null && <p>Status: {error.status}</p>}
        </section>
      )}

      {routeResult && (
        <section>
          <h2>Route analysis</h2>
          <p>{renderText(routeResult.summary)}</p>
          <p>Distance: {Number(routeResult.total_distance_nm).toFixed(1)} nm</p>
          <p>Duration: {Number(routeResult.estimated_duration_hours).toFixed(1)} h</p>
          <p>Risk score: {(Number(routeResult.overall_risk_score) * 100).toFixed(0)}%</p>
          <p>Recommended: {routeResult.recommended ? 'Yes' : 'No'}</p>
          <ul>
            {routeResult.waypoints.map((wp, i) => (
              <li key={i}>
                {wp.lat.toFixed(2)}, {wp.lon.toFixed(2)}
                {wp.weather_summary ? ` — ${renderText(wp.weather_summary)}` : ''}
              </li>
            ))}
          </ul>
        </section>
      )}

      {riskResult && (
        <section>
          <h2>Risk prediction</h2>
          <p>
            {renderText(riskResult.risk_level)} — {(Number(riskResult.risk_score) * 100).toFixed(0)}%
            (confidence {(Number(riskResult.confidence) * 100).toFixed(0)}%)
          </p>
          {riskResult.contributing_factors.length > 0 && (
            <>
              <p>Factors:</p>
              <ul>
                {riskResult.contributing_factors.map((f, i) => (
                  <li key={i}>{renderText(f)}</li>
                ))}
              </ul>
            </>
          )}
          {riskResult.recommendations.length > 0 && (
            <>
              <p>Recommendations:</p>
              <ul>
                {riskResult.recommendations.map((r, i) => (
                  <li key={i}>{renderText(r)}</li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}

      {speedResult && (
        <section>
          <h2>Speed prediction</h2>
          <p>Recommended: {speedResult.recommended_speed_knots.toFixed(1)} kn</p>
          <p>Weather penalty: {speedResult.weather_penalty_knots.toFixed(1)} kn</p>
          <p>Fuel efficiency: {(speedResult.fuel_efficiency_score * 100).toFixed(0)}%</p>
          <p>Safety: {renderText(speedResult.safety_margin)}</p>
          <p>{renderText(speedResult.reasoning)}</p>
        </section>
      )}
    </main>
  );
}
