from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.vessel import Vessel
from app.schemas.common import WeatherConditions, WaypointInput
from app.schemas.cost import CalculateCostRequest
from app.schemas.fuel import PredictFuelRequest
from app.schemas.risk import PredictRiskRequest
from app.schemas.route import (
    AnalyzeRouteRequest,
    AnalyzeRouteResponse,
    WaypointAnalysis,
)
from app.schemas.speed import PredictSpeedRequest
from app.services.cost.engine import calculate_cost
from app.services.fuel.predictor import predict_fuel
from app.services.laycan.analyzer import analyze_laycan
from app.services.persistence import persist_route_analysis
from app.services.risk.predictor import predict_risk
from app.services.speed.predictor import predict_speed
from app.services.weather.engine import get_weather_for_waypoint
from app.utils.geo import bearing_deg, haversine_nm


def _resolve_vessel(db: Session | None, request: AnalyzeRouteRequest) -> Vessel | None:
    if db is None:
        return None
    if request.vessel.vessel_id:
        vessel = db.get(Vessel, request.vessel.vessel_id)
        if vessel is None:
            raise NotFoundError("Vessel not found")
        return vessel
    vessel = Vessel(
        name=request.vessel.name,
        default_stw_knots=request.vessel.default_stw_knots,
        base_fuel_rate_mt_per_day=request.vessel.base_fuel_rate_mt_per_day,
    )
    db.add(vessel)
    db.flush()
    return vessel


def analyze_route(
    request: AnalyzeRouteRequest, db: Session | None = None
) -> AnalyzeRouteResponse:
    sorted_wps = sorted(request.waypoints, key=lambda w: w.sequence_order)
    stw = request.vessel.default_stw_knots
    base_fuel = request.vessel.base_fuel_rate_mt_per_day

    analyses: list[WaypointAnalysis] = []
    alerts: list[str] = []
    total_distance = 0.0
    total_fuel = 0.0
    total_delay = 0.0
    max_risk = 0.0
    prev: WaypointInput | None = None

    for wp in sorted_wps:
        if prev is not None:
            leg_nm = haversine_nm(prev.lat, prev.lon, wp.lat, wp.lon)
        else:
            leg_nm = 0.0
        total_distance += leg_nm

        heading = wp.vessel_heading_deg
        if heading is None and prev is not None:
            heading = bearing_deg(prev.lat, prev.lon, wp.lat, wp.lon)
        elif heading is None:
            heading = 0.0

        weather = get_weather_for_waypoint(wp.sequence_order, wp.lat, wp.lon)
        conditions = WeatherConditions(
            wind_speed_knots=weather.wind_speed_knots,
            wind_direction_deg=weather.wind_direction_deg,
            wave_height_m=weather.wave_height_m,
            current_speed_knots=weather.current_speed_knots,
            current_direction_deg=weather.current_direction_deg,
        )
        risk = predict_risk(
            PredictRiskRequest(weather=conditions, vessel_heading_deg=heading)
        )
        speed = predict_speed(
            PredictSpeedRequest(
                stw_knots=stw,
                weather=conditions,
                vessel_heading_deg=heading,
                distance_nm=leg_nm if leg_nm > 0 else 0.01,
            )
        )
        fuel = predict_fuel(
            PredictFuelRequest(
                stw_knots=stw,
                distance_nm=leg_nm if leg_nm > 0 else 0.01,
                weather=conditions,
                base_fuel_rate_mt_per_day=base_fuel,
            )
        )

        max_risk = max(max_risk, risk.risk_score)
        total_fuel += fuel.fuel_consumption_mt
        total_delay += speed.delay_hours
        if risk.risk_level.value == "dangerous":
            alerts.append(
                f"Dangerous weather at waypoint {wp.sequence_order} "
                f"({wp.lat:.2f}, {wp.lon:.2f})"
            )
        elif risk.risk_level.value == "moderate":
            alerts.append(
                f"Moderate risk at waypoint {wp.sequence_order}"
            )

        analyses.append(
            WaypointAnalysis(
                sequence_order=wp.sequence_order,
                lat=wp.lat,
                lon=wp.lon,
                weather=weather,
                risk=risk,
                speed=speed,
                fuel=fuel,
            )
        )
        prev = wp

    planned_eta_hours = total_distance / max(stw, 0.1) + total_delay
    cost = calculate_cost(
        CalculateCostRequest(
            fuel_consumption_mt=total_fuel,
            distance_nm=total_distance,
            canal_cost_usd=request.canal_cost_usd,
        )
    )

    laycan_result = None
    if request.laycan:
        laycan_result = analyze_laycan(request.laycan)

    voyage_id = None
    if request.save_to_db and db is not None:
        vessel = _resolve_vessel(db, request)
        voyage_id = persist_route_analysis(
            db=db,
            vessel=vessel,
            request=request,
            analyses=analyses,
            total_distance=total_distance,
            total_fuel=total_fuel,
            laycan_result=laycan_result,
            planned_eta_hours=planned_eta_hours,
        )
        db.commit()

    return AnalyzeRouteResponse(
        voyage_id=voyage_id,
        total_distance_nm=round(total_distance, 2),
        waypoints=analyses,
        aggregate_fuel_mt=round(total_fuel, 4),
        aggregate_delay_hours=round(total_delay, 2),
        planned_eta_hours=round(planned_eta_hours, 2),
        cost=cost,
        laycan=laycan_result,
        weather_alerts=alerts,
        max_risk_score=round(max_risk, 2),
    )
