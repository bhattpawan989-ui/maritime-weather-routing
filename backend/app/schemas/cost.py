from pydantic import BaseModel, Field

from app.schemas.common import WeatherConditions


class CalculateCostRequest(BaseModel):
    fuel_consumption_mt: float = Field(..., ge=0)
    distance_nm: float = Field(..., ge=0)
    weather: WeatherConditions | None = None
    canal_cost_usd: float = Field(default=0.0, ge=0)
    fuel_price_usd_per_mt: float | None = Field(None, gt=0)
    co2_kg_per_mt_fuel: float | None = Field(None, gt=0)


class CalculateCostResponse(BaseModel):
    fuel_cost_usd: float
    co2_cost_usd: float
    canal_cost_usd: float
    total_voyage_cost_usd: float
    co2_emissions_kg: float
