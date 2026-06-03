-- Apply all migrations in order (psql example)
-- psql -U postgres -d maritime_routing -f database/migrations/run_migrations.sql

\ir 001_enable_extensions.sql
\ir 002_create_enums.sql
\ir 003_create_vessels_voyages_waypoints.sql
\ir 004_create_weather_risk_fuel.sql
\ir 005_create_recommendations_laycan.sql
\ir 006_indexes_and_triggers.sql
