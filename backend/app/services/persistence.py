import uuid
from datetime import datetime, timedelta, timezone

from geoalchemy2.shape import from_shape
from shapely.geometry import LineString, Point
from sqlalchemy.orm import Session

from app.models.enums import RiskLevel, VoyageStatus
from app.models.fuel import FuelPrediction
from app.models.laycan import LaycanAnalysis
from app.models.vessel import Vessel
from app.models.voyage import Voyage
from app.models.waypoint import RouteWaypoint
from app.models.weather import WeatherData, WeatherRisk
from app.schemas.laycan import LaycanAnalysisResult
from app.schemas.route import AnalyzeRouteRequest, WaypointAnalysis
from app.services.risk.predictor import get_risk_model_version, risk_level_to_enum


def persist_route_analysis(
    db: Session,
    vessel: Vessel,
    request: AnalyzeRouteRequest,
    analyses: list[WaypointAnalysis],
    total_distance: float,
    total_fuel: float,
    laycan_result: LaycanAnalysisResult | None,
    planned_eta_hours: float,
) -> uuid.UUID:
    sorted_wps = sorted(request.waypoints, key=lambda w: w.sequence_order)
    first, last = sorted_wps[0], sorted_wps[-1]
    now = datetime.now(timezone.utc)

    voyage = Voyage(
        vessel_id=vessel.id,
        departure_port=request.departure_port,
        destination_port=request.destination_port,
        departure_point=from_shape(Point(first.lon, first.lat), srid=4326),
        destination_point=from_shape(Point(last.lon, last.lat), srid=4326),
        route_line=from_shape(
            LineString([(wp.lon, wp.lat) for wp in sorted_wps]), srid=4326
        ),
        laycan_start=request.laycan.laycan_start if request.laycan else None,
        laycan_end=request.laycan.laycan_end if request.laycan else None,
        planned_departure=now,
        planned_eta=now + timedelta(hours=planned_eta_hours),
        status=VoyageStatus.PLANNED,
        total_distance_nm=total_distance,
    )
    db.add(voyage)
    db.flush()

    for wp_input, analysis in zip(sorted_wps, analyses, strict=True):
        waypoint = RouteWaypoint(
            voyage_id=voyage.id,
            sequence_order=wp_input.sequence_order,
            location=from_shape(Point(wp_input.lon, wp_input.lat), srid=4326),
            name=wp_input.name,
            vessel_heading_deg=wp_input.vessel_heading_deg,
        )
        db.add(waypoint)
        db.flush()

        w = analysis.weather
        db.add(
            WeatherData(
                waypoint_id=waypoint.id,
                wind_speed_knots=w.wind_speed_knots,
                wind_direction_deg=w.wind_direction_deg,
                wave_height_m=w.wave_height_m,
                current_speed_knots=w.current_speed_knots,
                current_direction_deg=w.current_direction_deg,
            )
        )
        db.add(
            WeatherRisk(
                waypoint_id=waypoint.id,
                risk_score=analysis.risk.risk_score,
                risk_level=risk_level_to_enum(analysis.risk.risk_level),
                relative_heading_deg=analysis.risk.relative_heading_deg,
                model_version=get_risk_model_version(),
            )
        )
        db.add(
            FuelPrediction(
                voyage_id=voyage.id,
                waypoint_id=waypoint.id,
                stw_knots=request.vessel.default_stw_knots,
                effective_sog_knots=analysis.speed.effective_sog_knots,
                fuel_consumption_mt=analysis.fuel.fuel_consumption_mt,
                fuel_cost_usd=analysis.fuel.fuel_cost_usd,
                delay_hours=analysis.speed.delay_hours,
            )
        )

    db.add(
        FuelPrediction(
            voyage_id=voyage.id,
            stw_knots=request.vessel.default_stw_knots,
            effective_sog_knots=request.vessel.default_stw_knots,
            distance_nm=total_distance,
            fuel_consumption_mt=total_fuel,
            delay_hours=sum(a.speed.delay_hours for a in analyses),
        )
    )

    if laycan_result and request.laycan:
        db.add(
            LaycanAnalysis(
                voyage_id=voyage.id,
                laycan_start=request.laycan.laycan_start,
                laycan_end=request.laycan.laycan_end,
                eta=request.laycan.eta,
                laycan_risk_pct=laycan_result.laycan_risk_pct,
                missed_laycan_warning=laycan_result.missed_laycan_warning,
            )
        )

    return voyage.id
