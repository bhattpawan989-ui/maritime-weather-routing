-- Route diversion recommendations and laycan analysis

CREATE TABLE route_recommendations (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    voyage_id               UUID NOT NULL REFERENCES voyages (id) ON DELETE CASCADE,
    recommended_route       GEOGRAPHY(LINESTRING, 4326) NOT NULL,
    extra_distance_nm       NUMERIC(10, 2) NOT NULL DEFAULT 0,
    eta_difference_hours    NUMERIC(8, 2) NOT NULL DEFAULT 0,
    fuel_difference_mt      NUMERIC(12, 4) NOT NULL DEFAULT 0,
    fuel_difference_cost_usd NUMERIC(14, 2),
    status                  recommendation_status NOT NULL DEFAULT 'pending',
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT route_recommendations_extra_distance_non_negative CHECK (
        extra_distance_nm >= 0
    )
);

CREATE TABLE laycan_analysis (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    voyage_id               UUID NOT NULL REFERENCES voyages (id) ON DELETE CASCADE,
    laycan_start            TIMESTAMPTZ NOT NULL,
    laycan_end              TIMESTAMPTZ NOT NULL,
    eta                     TIMESTAMPTZ NOT NULL,
    laycan_risk_pct         NUMERIC(5, 2) NOT NULL,
    missed_laycan_warning   BOOLEAN NOT NULL DEFAULT FALSE,
    analyzed_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT laycan_analysis_window_order CHECK (laycan_end >= laycan_start),
    CONSTRAINT laycan_analysis_risk_pct_range CHECK (
        laycan_risk_pct >= 0 AND laycan_risk_pct <= 100
    )
);
