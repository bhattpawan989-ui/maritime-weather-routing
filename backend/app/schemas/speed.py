from pydantic import BaseModel, Field

from app.schemas.common import WeatherConditions


class PredictSpeedRequest(BaseModel):
    stw_knots: float = Field(..., gt=0)
    weather: WeatherConditions
    vessel_heading_deg: float = Field(..., ge=0, lt=360)
    distance_nm: float = Field(..., ge=0)


class PredictSpeedResponse(BaseModel):
    effective_sog_knots: float = Field(..., ge=0)
    delay_hours: float = Field(..., ge=0)
