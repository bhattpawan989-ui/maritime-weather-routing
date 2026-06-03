from app.core.config import settings
from app.core.exceptions import AppError
from app.schemas.common import WaypointInput
from app.schemas.diversion import (
    RecommendRouteRequest,
    RecommendRouteResponse,
    RouteScoreBreakdown,
    WeatherRiskZone,
)
from app.services.diversion.astar import AStarPathfinder
from app.services.diversion.grid import NavigationGrid, build_grid_bounds
from app.services.diversion.scoring import (
    RouteScore,
    risk_reduction_score,
    score_route,
)
from app.utils.geo import bearing_deg, haversine_nm

BLOCK_THRESHOLDS = (88.0, 75.0, 60.0)
MAX_GRID_DIMENSION = 120


def _score_to_breakdown(score: RouteScore) -> RouteScoreBreakdown:
    return RouteScoreBreakdown(
        distance_nm=score.distance_nm,
        average_risk=score.average_risk,
        exposure_index=score.exposure_index,
        composite_score=score.composite_score,
    )


def _fuel_for_distance(
    distance_nm: float,
    stw_knots: float,
    base_fuel_rate_mt_per_day: float,
    average_risk: float,
) -> float:
    hours = distance_nm / max(stw_knots, 0.1)
    days = hours / 24.0
    speed_factor = (stw_knots / 12.0) ** 2
    weather_factor = 1.0 + (average_risk / 100.0) * 0.2
    return base_fuel_rate_mt_per_day * days * speed_factor * weather_factor


def _simplify_coords(
    coords: list[tuple[float, float]], min_leg_nm: float = 8.0
) -> list[tuple[float, float]]:
    if len(coords) <= 2:
        return coords
    simplified = [coords[0]]
    for point in coords[1:-1]:
        if haversine_nm(simplified[-1][0], simplified[-1][1], point[0], point[1]) >= min_leg_nm:
            simplified.append(point)
    if simplified[-1] != coords[-1]:
        simplified.append(coords[-1])
    return simplified


def _find_segment(
    grid: NavigationGrid,
    start: tuple[float, float],
    goal: tuple[float, float],
) -> list[tuple[int, int]] | None:
    pathfinder = AStarPathfinder(grid)
    start_cell = grid.latlon_to_cell(*start)
    goal_cell = grid.latlon_to_cell(*goal)
    return pathfinder.find_path(start_cell, goal_cell)


def _create_grid(
    bounds,
    cell_size_nm: float,
    zones: list[WeatherRiskZone],
    threshold: float,
) -> NavigationGrid:
    grid = NavigationGrid(bounds, cell_size_nm, zones, blocked_threshold=threshold)
    if max(grid.n_rows, grid.n_cols) > MAX_GRID_DIMENSION:
        return NavigationGrid(
            bounds,
            cell_size_nm * 1.5,
            zones,
            blocked_threshold=threshold,
        )
    return grid


def _resolve_navigation_grid(
    leg_coords: list[tuple[float, float]],
    zones: list[WeatherRiskZone],
    cell_size_nm: float,
) -> NavigationGrid:
    bounds = build_grid_bounds(leg_coords, zones)
    for threshold in BLOCK_THRESHOLDS:
        grid = _create_grid(bounds, cell_size_nm, zones, threshold)
        if all(
            _find_segment(grid, leg_coords[i], leg_coords[i + 1]) is not None
            for i in range(len(leg_coords) - 1)
        ):
            return grid
    raise AppError(
        "Unable to compute a feasible diversion path for the provided route and risk zones",
        status_code=422,
    )


def _build_path(
    leg_coords: list[tuple[float, float]],
    zones: list[WeatherRiskZone],
    cell_size_nm: float,
) -> list[tuple[float, float]]:
    grid = _resolve_navigation_grid(leg_coords, zones, cell_size_nm)
    merged_cells: list[tuple[int, int]] = []

    for idx in range(len(leg_coords) - 1):
        segment = _find_segment(grid, leg_coords[idx], leg_coords[idx + 1])
        if segment is None:
            raise AppError(
                f"No feasible diversion path between waypoint {idx} and {idx + 1}",
                status_code=422,
            )
        if merged_cells:
            segment = segment[1:]
        merged_cells.extend(segment)

    coords = [grid.cell_to_latlon(row, col) for row, col in merged_cells]
    return _simplify_coords(coords)


def _coords_to_waypoints(coords: list[tuple[float, float]]) -> list[WaypointInput]:
    waypoints: list[WaypointInput] = []
    for index, (lat, lon) in enumerate(coords):
        heading = None
        if index < len(coords) - 1:
            nlat, nlon = coords[index + 1]
            heading = bearing_deg(lat, lon, nlat, nlon)
        waypoints.append(
            WaypointInput(
                sequence_order=index,
                lat=round(lat, 6),
                lon=round(lon, 6),
                vessel_heading_deg=heading,
            )
        )
    return waypoints


def recommend_route(payload: RecommendRouteRequest) -> RecommendRouteResponse:
    sorted_wps = sorted(payload.waypoints, key=lambda w: w.sequence_order)
    leg_coords = [(wp.lat, wp.lon) for wp in sorted_wps]
    zones = payload.weather_risk_zones
    stw = payload.vessel_speed_knots

    original_score = score_route(leg_coords, zones)
    alt_coords = _build_path(leg_coords, zones, payload.grid_cell_size_nm)
    alternative_score = score_route(alt_coords, zones)

    extra_distance = max(0.0, alternative_score.distance_nm - original_score.distance_nm)
    original_hours = original_score.distance_nm / stw
    alternative_hours = alternative_score.distance_nm / stw
    eta_difference = max(0.0, alternative_hours - original_hours)

    original_fuel = _fuel_for_distance(
        original_score.distance_nm,
        stw,
        payload.base_fuel_rate_mt_per_day,
        original_score.average_risk,
    )
    alternative_fuel = _fuel_for_distance(
        alternative_score.distance_nm,
        stw,
        payload.base_fuel_rate_mt_per_day,
        alternative_score.average_risk,
    )
    fuel_difference = max(0.0, alternative_fuel - original_fuel)
    fuel_cost_difference = fuel_difference * settings.fuel_price_usd_per_mt

    return RecommendRouteResponse(
        alternative_waypoints=_coords_to_waypoints(alt_coords),
        extra_distance_nm=round(extra_distance, 2),
        eta_difference_hours=round(eta_difference, 2),
        fuel_difference_mt=round(fuel_difference, 4),
        fuel_difference_cost_usd=round(fuel_cost_difference, 2),
        risk_reduction_score=risk_reduction_score(original_score, alternative_score),
        original_route_score=_score_to_breakdown(original_score),
        recommended_route_score=_score_to_breakdown(alternative_score),
    )
