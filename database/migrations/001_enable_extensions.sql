-- Maritime Weather Routing: enable required extensions
-- Run against PostgreSQL 14+ with PostGIS available

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
