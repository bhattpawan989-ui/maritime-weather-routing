-- Spatial indexes, lookup indexes, updated_at triggers

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_vessels_updated_at
    BEFORE UPDATE ON vessels
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();

CREATE TRIGGER trg_voyages_updated_at
    BEFORE UPDATE ON voyages
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();

CREATE TRIGGER trg_route_recommendations_updated_at
    BEFORE UPDATE ON route_recommendations
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();

-- Vessels
CREATE INDEX idx_vessels_name ON vessels (name);
CREATE INDEX idx_vessels_imo ON vessels (imo_number) WHERE imo_number IS NOT NULL;

-- Voyages
CREATE INDEX idx_voyages_vessel_id ON voyages (vessel_id);
CREATE INDEX idx_voyages_status ON voyages (status);
CREATE INDEX idx_voyages_laycan ON voyages (laycan_start, laycan_end);
CREATE INDEX idx_voyages_departure_point ON voyages USING GIST (departure_point);
CREATE INDEX idx_voyages_destination_point ON voyages USING GIST (destination_point);
CREATE INDEX idx_voyages_route_line ON voyages USING GIST (route_line);

-- Route waypoints
CREATE INDEX idx_route_waypoints_voyage_id ON route_waypoints (voyage_id);
CREATE INDEX idx_route_waypoints_location ON route_waypoints USING GIST (location);
CREATE INDEX idx_route_waypoints_voyage_sequence ON route_waypoints (voyage_id, sequence_order);

-- Weather
CREATE INDEX idx_weather_data_waypoint_id ON weather_data (waypoint_id);
CREATE INDEX idx_weather_data_forecast_time ON weather_data (forecast_time);

CREATE INDEX idx_weather_risk_waypoint_id ON weather_risk (waypoint_id);
CREATE INDEX idx_weather_risk_level ON weather_risk (risk_level);
CREATE INDEX idx_weather_risk_predicted_at ON weather_risk (predicted_at);

-- Fuel
CREATE INDEX idx_fuel_predictions_voyage_id ON fuel_predictions (voyage_id);
CREATE INDEX idx_fuel_predictions_waypoint_id ON fuel_predictions (waypoint_id)
    WHERE waypoint_id IS NOT NULL;
CREATE INDEX idx_fuel_predictions_predicted_at ON fuel_predictions (predicted_at);

-- Recommendations & laycan
CREATE INDEX idx_route_recommendations_voyage_id ON route_recommendations (voyage_id);
CREATE INDEX idx_route_recommendations_status ON route_recommendations (status);
CREATE INDEX idx_route_recommendations_route ON route_recommendations USING GIST (recommended_route);

CREATE INDEX idx_laycan_analysis_voyage_id ON laycan_analysis (voyage_id);
CREATE INDEX idx_laycan_analysis_analyzed_at ON laycan_analysis (analyzed_at);
CREATE INDEX idx_laycan_analysis_missed_warning ON laycan_analysis (missed_laycan_warning)
    WHERE missed_laycan_warning = TRUE;

-- Latest weather/risk per waypoint (common read pattern)
CREATE INDEX idx_weather_data_waypoint_forecast ON weather_data (waypoint_id, forecast_time DESC);
CREATE INDEX idx_weather_risk_waypoint_predicted ON weather_risk (waypoint_id, predicted_at DESC);
