-- Weather observations, risk scores, and fuel predictions

CREATE TABLE weather_data (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    waypoint_id             UUID NOT NULL REFERENCES route_waypoints (id) ON DELETE CASCADE,
    wind_speed_knots        NUMERIC(6, 2) NOT NULL,
    wind_direction_deg      NUMERIC(6, 2) NOT NULL,
    wave_height_m           NUMERIC(6, 2) NOT NULL,
    current_speed_knots     NUMERIC(6, 2) NOT NULL,
    current_direction_deg   NUMERIC(6, 2) NOT NULL,
    forecast_time           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    data_source             VARCHAR(64) NOT NULL DEFAULT 'synthetic',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT weather_data_wind_non_negative CHECK (wind_speed_knots >= 0),
    CONSTRAINT weather_data_wave_non_negative CHECK (wave_height_m >= 0),
    CONSTRAINT weather_data_current_non_negative CHECK (current_speed_knots >= 0),
    CONSTRAINT weather_data_wind_dir_range CHECK (
        wind_direction_deg >= 0 AND wind_direction_deg < 360
    ),
    CONSTRAINT weather_data_current_dir_range CHECK (
        current_direction_deg >= 0 AND current_direction_deg < 360
    )
);

CREATE TABLE weather_risk (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    waypoint_id             UUID NOT NULL REFERENCES route_waypoints (id) ON DELETE CASCADE,
    risk_score              NUMERIC(5, 2) NOT NULL,
    risk_level              risk_level NOT NULL,
    relative_heading_deg    NUMERIC(6, 2),
    model_version           VARCHAR(32),
    predicted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT weather_risk_score_range CHECK (
        risk_score >= 0 AND risk_score <= 100
    ),
    CONSTRAINT weather_risk_heading_range CHECK (
        relative_heading_deg IS NULL
        OR (relative_heading_deg >= 0 AND relative_heading_deg < 360)
    )
);

CREATE TABLE fuel_predictions (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    voyage_id               UUID NOT NULL REFERENCES voyages (id) ON DELETE CASCADE,
    waypoint_id             UUID REFERENCES route_waypoints (id) ON DELETE SET NULL,
    stw_knots               NUMERIC(6, 2) NOT NULL,
    effective_sog_knots     NUMERIC(6, 2) NOT NULL,
    distance_nm             NUMERIC(10, 2),
    fuel_consumption_mt     NUMERIC(12, 4) NOT NULL,
    fuel_cost_usd           NUMERIC(14, 2),
    delay_hours             NUMERIC(8, 2) NOT NULL DEFAULT 0,
    predicted_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fuel_predictions_stw_positive CHECK (stw_knots > 0),
    CONSTRAINT fuel_predictions_sog_non_negative CHECK (effective_sog_knots >= 0),
    CONSTRAINT fuel_predictions_fuel_non_negative CHECK (fuel_consumption_mt >= 0),
    CONSTRAINT fuel_predictions_distance_non_negative CHECK (
        distance_nm IS NULL OR distance_nm >= 0
    )
);
