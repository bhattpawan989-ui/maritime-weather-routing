from app.schemas.common import Coordinate, WaypointInput
from app.schemas.diversion import RecommendRouteRequest, WeatherRiskZone
from app.schemas.risk import RiskLevelLabel
from app.services.diversion.engine import recommend_route
from app.services.diversion.scoring import score_route


def test_score_route_without_zones():
    coords = [(1.0, 103.0), (5.0, 110.0), (10.0, 120.0)]
    score = score_route(coords, [])
    assert score.distance_nm > 0
    assert score.average_risk == 0.0


def test_astar_avoids_high_risk_zone():
    request = RecommendRouteRequest(
        waypoints=[
            WaypointInput(sequence_order=0, lat=0.0, lon=0.0),
            WaypointInput(sequence_order=1, lat=0.0, lon=2.0),
        ],
        weather_risk_zones=[
            WeatherRiskZone(
                center=Coordinate(lat=0.0, lon=1.0),
                radius_nm=80.0,
                risk_score=95.0,
            )
        ],
        vessel_speed_knots=12.0,
        grid_cell_size_nm=20.0,
    )
    response = recommend_route(request)
    assert len(response.alternative_waypoints) >= 2
    assert response.risk_reduction_score >= 0.0
    assert response.recommended_route_score.average_risk <= response.original_route_score.average_risk


def test_recommend_route_returns_impact_metrics():
    request = RecommendRouteRequest(
        waypoints=[
            WaypointInput(sequence_order=0, lat=1.29, lon=103.85),
            WaypointInput(sequence_order=1, lat=10.0, lon=115.0),
        ],
        weather_risk_zones=[
            WeatherRiskZone(
                center=Coordinate(lat=5.0, lon=109.0),
                radius_nm=50.0,
                min_risk_level=RiskLevelLabel.DANGEROUS,
            )
        ],
        vessel_speed_knots=14.0,
        base_fuel_rate_mt_per_day=30.0,
    )
    response = recommend_route(request)
    assert response.extra_distance_nm >= 0.0
    assert response.eta_difference_hours >= 0.0
    assert response.fuel_difference_mt >= 0.0
    assert response.original_route_score.composite_score > 0
