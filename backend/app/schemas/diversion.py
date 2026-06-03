from pydantic import BaseModel, Field

from app.schemas.common import Coordinate, WaypointInput
from app.schemas.risk import RiskLevelLabel


class DangerZone(BaseModel):
    center: Coordinate
    radius_nm: float = Field(..., gt=0)
    min_risk_level: RiskLevelLabel = RiskLevelLabel.MODERATE


class RecommendRouteRequest(BaseModel):
    waypoints: list[WaypointInput] = Field(..., min_length=2)
    danger_zones: list[DangerZone] = Field(default_factory=list)
    vessel_heading_deg: float = Field(default=0.0, ge=0, lt=360)


class RecommendRouteResponse(BaseModel):
    alternative_waypoints: list[WaypointInput]
    extra_distance_nm: float
    eta_difference_hours: float
    fuel_difference_mt: float
    fuel_difference_cost_usd: float
