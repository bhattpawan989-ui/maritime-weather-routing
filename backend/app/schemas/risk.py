from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import WeatherConditions


class RiskLevelLabel(str, Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"


class PredictRiskRequest(BaseModel):
    weather: WeatherConditions
    vessel_heading_deg: float = Field(..., ge=0, lt=360)


class PredictRiskResponse(BaseModel):
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevelLabel
    relative_heading_deg: float
