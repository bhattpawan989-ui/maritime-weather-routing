from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import WaypointInput
from app.schemas.cost import CalculateCostResponse
from app.schemas.laycan import LaycanAnalysisResult, LaycanInput
from app.schemas.risk import PredictRiskResponse
from app.schemas.fuel import PredictFuelResponse
from app.schemas.speed import PredictSpeedResponse
from app.schemas.weather import WaypointWeather


class VesselInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    vessel_id: UUID | None = None
    default_stw_knots: float = Field(default=12.0, gt=0)
    base_fuel_rate_mt_per_day: float = Field(default=25.0, gt=0)


class AnalyzeRouteRequest(BaseModel):
    vessel: VesselInput
    departure_port: str = Field(..., min_length=1)
    destination_port: str = Field(..., min_length=1)
    waypoints: list[WaypointInput] = Field(..., min_length=2)
    laycan: LaycanInput | None = None
    canal_cost_usd: float = Field(default=0.0, ge=0)
    save_to_db: bool = False

    @model_validator(mode="after")
    def validate_waypoint_sequence(self) -> "AnalyzeRouteRequest":
        orders = [wp.sequence_order for wp in self.waypoints]
        if len(orders) != len(set(orders)):
            raise ValueError("waypoint sequence_order values must be unique")
        return self


class WaypointAnalysis(BaseModel):
    sequence_order: int
    lat: float
    lon: float
    weather: WaypointWeather
    risk: PredictRiskResponse
    speed: PredictSpeedResponse
    fuel: PredictFuelResponse


class AnalyzeRouteResponse(BaseModel):
    voyage_id: UUID | None = None
    total_distance_nm: float
    waypoints: list[WaypointAnalysis]
    aggregate_fuel_mt: float
    aggregate_delay_hours: float
    planned_eta_hours: float
    cost: CalculateCostResponse
    laycan: LaycanAnalysisResult | None = None
    weather_alerts: list[str]
    max_risk_score: float
