from pydantic import BaseModel, Field, model_validator

from app.schemas.common import Coordinate, WaypointInput
from app.schemas.risk import RiskLevelLabel


class WeatherRiskZone(BaseModel):
    center: Coordinate
    radius_nm: float = Field(..., gt=0)
    risk_score: float | None = Field(None, ge=0, le=100)
    min_risk_level: RiskLevelLabel = RiskLevelLabel.MODERATE


class DangerZone(WeatherRiskZone):
    """Backward-compatible alias for weather risk zones."""


class RecommendRouteRequest(BaseModel):
    waypoints: list[WaypointInput] = Field(..., min_length=2)
    weather_risk_zones: list[WeatherRiskZone] = Field(default_factory=list)
    danger_zones: list[DangerZone] = Field(default_factory=list)
    vessel_speed_knots: float = Field(..., gt=0, description="STW in knots")
    vessel_heading_deg: float = Field(default=0.0, ge=0, lt=360)
    base_fuel_rate_mt_per_day: float = Field(default=25.0, gt=0)
    grid_cell_size_nm: float = Field(default=15.0, gt=0, le=100)

    @model_validator(mode="before")
    @classmethod
    def merge_risk_zones(cls, data: object) -> object:
        if not isinstance(data, dict):
            return data
        primary = list(data.get("weather_risk_zones") or [])
        legacy = list(data.get("danger_zones") or [])
        if legacy:
            data["weather_risk_zones"] = primary + legacy
        return data


class RouteScoreBreakdown(BaseModel):
    distance_nm: float
    average_risk: float
    exposure_index: float
    composite_score: float


class RecommendRouteResponse(BaseModel):
    alternative_waypoints: list[WaypointInput]
    extra_distance_nm: float
    eta_difference_hours: float
    fuel_difference_mt: float
    fuel_difference_cost_usd: float
    risk_reduction_score: float = Field(..., ge=0, le=100)
    original_route_score: RouteScoreBreakdown
    recommended_route_score: RouteScoreBreakdown
