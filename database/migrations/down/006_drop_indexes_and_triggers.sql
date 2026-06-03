DROP TRIGGER IF EXISTS trg_route_recommendations_updated_at ON route_recommendations;
DROP TRIGGER IF EXISTS trg_voyages_updated_at ON voyages;
DROP TRIGGER IF EXISTS trg_vessels_updated_at ON vessels;
DROP FUNCTION IF EXISTS set_updated_at();
