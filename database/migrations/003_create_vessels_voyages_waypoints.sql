-- Core entities: vessels, voyages, route waypoints

CREATE TABLE vessels (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                VARCHAR(255) NOT NULL,
    imo_number          VARCHAR(7) UNIQUE,
    vessel_type         VARCHAR(64),
    dwt                 NUMERIC(12, 2),
    default_stw_knots   NUMERIC(6, 2),
    base_fuel_rate_mt_per_day NUMERIC(10, 4),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT vessels_imo_format CHECK (
        imo_number IS NULL OR imo_number ~ '^[0-9]{7}$'
    ),
    CONSTRAINT vessels_dwt_positive CHECK (dwt IS NULL OR dwt > 0),
    CONSTRAINT vessels_stw_positive CHECK (
        default_stw_knots IS NULL OR default_stw_knots > 0
    )
);

CREATE TABLE voyages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vessel_id           UUID NOT NULL REFERENCES vessels (id) ON DELETE RESTRICT,
    voyage_code         VARCHAR(64),
    departure_port      VARCHAR(128) NOT NULL,
    destination_port    VARCHAR(128) NOT NULL,
    departure_point     GEOGRAPHY(POINT, 4326),
    destination_point   GEOGRAPHY(POINT, 4326),
    route_line          GEOGRAPHY(LINESTRING, 4326),
    laycan_start        TIMESTAMPTZ,
    laycan_end          TIMESTAMPTZ,
    planned_departure   TIMESTAMPTZ,
    planned_eta         TIMESTAMPTZ,
    status              voyage_status NOT NULL DEFAULT 'draft',
    total_distance_nm   NUMERIC(10, 2),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT voyages_laycan_order CHECK (
        laycan_start IS NULL
        OR laycan_end IS NULL
        OR laycan_end >= laycan_start
    ),
    CONSTRAINT voyages_distance_positive CHECK (
        total_distance_nm IS NULL OR total_distance_nm >= 0
    )
);

CREATE TABLE route_waypoints (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    voyage_id           UUID NOT NULL REFERENCES voyages (id) ON DELETE CASCADE,
    sequence_order      INTEGER NOT NULL,
    location            GEOGRAPHY(POINT, 4326) NOT NULL,
    name                VARCHAR(128),
    eta_at_waypoint     TIMESTAMPTZ,
    vessel_heading_deg  NUMERIC(6, 2),
    distance_from_prev_nm NUMERIC(10, 2),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT route_waypoints_sequence_positive CHECK (sequence_order >= 0),
    CONSTRAINT route_waypoints_heading_range CHECK (
        vessel_heading_deg IS NULL
        OR (vessel_heading_deg >= 0 AND vessel_heading_deg < 360)
    ),
    CONSTRAINT route_waypoints_unique_sequence UNIQUE (voyage_id, sequence_order)
);
