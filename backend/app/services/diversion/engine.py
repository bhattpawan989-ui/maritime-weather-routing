from app.core.config import settings
from app.schemas.common import WaypointInput
from app.schemas.diversion import DangerZone, RecommendRouteRequest, RecommendRouteResponse
from app.utils.geo import haversine_nm, linestring_length_nm, offset_coordinate


def _point_in_zone(lat: float, lon: float, zone: DangerZone) -> bool:
    distance = haversine_nm(lat, lon, zone.center.lat, zone.center.lon)
    return distance <= zone.radius_nm


def recommend_route(payload: RecommendRouteRequest) -> RecommendRouteResponse:
    sorted_wps = sorted(payload.waypoints, key=lambda w: w.sequence_order)
    original_coords = [(wp.lat, wp.lon) for wp in sorted_wps]
    original_distance = linestring_length_nm(original_coords)

    alternative: list[WaypointInput] = []
    offset_nm = 25.0
    for wp in sorted_wps:
        lat, lon = wp.lat, wp.lon
        in_danger = any(_point_in_zone(lat, lon, zone) for zone in payload.danger_zones)
        if in_danger:
            lat, lon = offset_coordinate(lat, lon, payload.vessel_heading_deg + 90, offset_nm)
        alternative.append(
            WaypointInput(
                sequence_order=wp.sequence_order,
                lat=round(lat, 6),
                lon=round(lon, 6),
                name=wp.name,
                vessel_heading_deg=wp.vessel_heading_deg,
            )
        )

    alt_coords = [(wp.lat, wp.lon) for wp in alternative]
    alt_distance = linestring_length_nm(alt_coords)
    extra_distance = max(0.0, alt_distance - original_distance)
    stw = 12.0
    eta_diff = extra_distance / max(stw, 0.1)
    fuel_diff = (extra_distance / max(stw, 0.1) / 24.0) * 25.0 * 1.1
    fuel_cost_diff = fuel_diff * settings.fuel_price_usd_per_mt

    return RecommendRouteResponse(
        alternative_waypoints=alternative,
        extra_distance_nm=round(extra_distance, 2),
        eta_difference_hours=round(eta_diff, 2),
        fuel_difference_mt=round(fuel_diff, 4),
        fuel_difference_cost_usd=round(fuel_cost_diff, 2),
    )
