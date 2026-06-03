'use client';

import { useState, type FormEvent } from 'react';
import { useMaritimeApi } from '@/hooks/useMaritimeApi';
import type { VoyageInput } from '@/types/maritime';

function renderText(value: unknown): string {
  if (value == null) return '';
  if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }
  return JSON.stringify(value, null, 2);
}

export default function HomePage() {
  const { panelState, error, routeResult, riskResult, speedResult, analyze, reset } =
    useMaritimeApi();

  const [originLat, setOriginLat] = useState('1.29');
  const [originLon, setOriginLon] = useState('103.85');
  const [destLat, setDestLat] = useState('22.3');
  const [destLon, setDestLon] = useState('114.2');
  const [departurePort, setDeparturePort] = useState('Singapore');
  const [destinationPort, setDestinationPort] = useState('Hong Kong');
  const [vesselName, setVesselName] = useState('MV Explorer');
  const [speed, setSpeed] = useState('12');

  const loading = panelState === 'loading';

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const input: VoyageInput = {
      origin: { lat: Number(originLat), lon: Number(originLon), name: departurePort },
      destination: { lat: Number(destLat), lon: Number(destLon), name: destinationPort },
      departure_port: departurePort,
      destination_port: destinationPort,
      vessel_name: vesselName,
      vessel_speed_knots: Number(speed),
    };
    void analyze(input);
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>Maritime voyage planner</h1>
        <p className="subtitle">Weather routing, risk assessment, and speed guidance for your passage.</p>
      </header>

      <form className="card form-card" onSubmit={handleSubmit}>
        <fieldset>
          <legend>Ports</legend>
          <div className="field-grid">
            <label>
              Port of departure
              <input
                value={departurePort}
                onChange={(e) => setDeparturePort(e.target.value)}
                placeholder="e.g. Singapore"
                required
              />
            </label>
            <label>
              Port of destination
              <input
                value={destinationPort}
                onChange={(e) => setDestinationPort(e.target.value)}
                placeholder="e.g. Hong Kong"
                required
              />
            </label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Origin waypoint</legend>
          <div className="field-grid">
            <label>
              Latitude (°)
              <span className="label-hint">Decimal degrees, WGS 84</span>
              <input
                value={originLat}
                onChange={(e) => setOriginLat(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
            <label>
              Longitude (°)
              <span className="label-hint">Decimal degrees, WGS 84</span>
              <input
                value={originLon}
                onChange={(e) => setOriginLon(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Destination waypoint</legend>
          <div className="field-grid">
            <label>
              Latitude (°)
              <span className="label-hint">Decimal degrees, WGS 84</span>
              <input
                value={destLat}
                onChange={(e) => setDestLat(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
            <label>
              Longitude (°)
              <span className="label-hint">Decimal degrees, WGS 84</span>
              <input
                value={destLon}
                onChange={(e) => setDestLon(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
          </div>
        </fieldset>

        <fieldset>
          <legend>Vessel</legend>
          <div className="field-grid">
            <label>
              Vessel name
              <input
                value={vesselName}
                onChange={(e) => setVesselName(e.target.value)}
                placeholder="e.g. MV Explorer"
                required
              />
            </label>
            <label>
              Speed through water (kn)
              <span className="label-hint">STW in knots</span>
              <input
                value={speed}
                onChange={(e) => setSpeed(e.target.value)}
                inputMode="decimal"
                required
              />
            </label>
          </div>
        </fieldset>

        <div className="actions">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Running analysis…' : 'Run voyage analysis'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={reset} disabled={loading}>
            Clear form
          </button>
        </div>
      </form>

      <div className="results">
        {error && (
          <section className="card result-card error-card">
            <h2>Request failed</h2>
            <pre>{renderText(error.message) || 'An unexpected error occurred. Please try again.'}</pre>
            {error.status != null && (
              <p className="status-line">HTTP status: {error.status}</p>
            )}
          </section>
        )}

        {routeResult && (
          <section className="card result-card">
            <h2>Route assessment</h2>
            <p className="result-summary">{renderText(routeResult.summary)}</p>
            <p>
              <span className="metric-label">Distance: </span>
              {Number(routeResult.total_distance_nm).toFixed(1)} NM
            </p>
            <p>
              <span className="metric-label">Passage time: </span>
              {Number(routeResult.estimated_duration_hours).toFixed(1)} hours
            </p>
            <p>
              <span className="metric-label">Overall risk: </span>
              {(Number(routeResult.overall_risk_score) * 100).toFixed(0)}%
            </p>
            <p>
              <span className="metric-label">Route recommendation: </span>
              {routeResult.recommended ? 'Recommended' : 'Not recommended'}
            </p>
            <p className="metric-label">Waypoints</p>
            <ul>
              {routeResult.waypoints.map((wp, i) => (
                <li key={i}>
                  {wp.lat.toFixed(2)}°, {wp.lon.toFixed(2)}°
                  {wp.weather_summary ? ` — ${renderText(wp.weather_summary)}` : ''}
                </li>
              ))}
            </ul>
          </section>
        )}

        {riskResult && (
          <section className="card result-card">
            <h2>Weather risk assessment</h2>
            <p>
              <span className="metric-label">Risk level: </span>
              {renderText(riskResult.risk_level)} —{' '}
              {(Number(riskResult.risk_score) * 100).toFixed(0)}%
              <span className="metric-label"> (confidence </span>
              {(Number(riskResult.confidence) * 100).toFixed(0)}%)
            </p>
            {riskResult.contributing_factors.length > 0 && (
              <>
                <p className="metric-label">Contributing factors</p>
                <ul>
                  {riskResult.contributing_factors.map((f, i) => (
                    <li key={i}>{renderText(f)}</li>
                  ))}
                </ul>
              </>
            )}
            {riskResult.recommendations.length > 0 && (
              <>
                <p className="metric-label">Recommendations</p>
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
          <section className="card result-card">
            <h2>Speed advisory</h2>
            <p>
              <span className="metric-label">Recommended speed: </span>
              {speedResult.recommended_speed_knots.toFixed(1)} kn
            </p>
            <p>
              <span className="metric-label">Weather speed loss: </span>
              {speedResult.weather_penalty_knots.toFixed(1)} kn
            </p>
            <p>
              <span className="metric-label">Fuel efficiency index: </span>
              {(speedResult.fuel_efficiency_score * 100).toFixed(0)}%
            </p>
            <p>
              <span className="metric-label">Safety margin: </span>
              {renderText(speedResult.safety_margin)}
            </p>
            <p>{renderText(speedResult.reasoning)}</p>
          </section>
        )}
      </div>
    </main>
  );
}
