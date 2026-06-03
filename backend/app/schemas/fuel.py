from pydantic import BaseModel, Field

from app.schemas.common import WeatherConditions


class PredictFuelRequest(BaseModel):
    stw_knots: float = Field(..., gt=0)
    distance_nm: float = Field(..., ge=0)
    weather: WeatherConditions
    base_fuel_rate_mt_per_day: float = Field(default=25.0, gt=0)
    fuel_price_usd_per_mt: float | None = Field(None, gt=0)


class PredictFuelResponse(BaseModel):
    fuel_consumption_mt: float = Field(..., ge=0)
    fuel_cost_usd: float = Field(..., ge=0)
