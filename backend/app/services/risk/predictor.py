from app.models.enums import RiskLevel
from app.schemas.common import WeatherConditions
from app.schemas.risk import PredictRiskRequest, PredictRiskResponse, RiskLevelLabel
from app.utils.geo import angle_diff_deg


def _score_to_level(score: float) -> RiskLevelLabel:
    if score < 33:
        return RiskLevelLabel.SAFE
    if score < 66:
        return RiskLevelLabel.MODERATE
    return RiskLevelLabel.DANGEROUS


def risk_level_to_enum(level: RiskLevelLabel) -> RiskLevel:
    return RiskLevel(level.value)


def predict_risk(payload: PredictRiskRequest) -> PredictRiskResponse:
    weather = payload.weather
    relative = angle_diff_deg(weather.wind_direction_deg, payload.vessel_heading_deg)
    wind_factor = min(weather.wind_speed_knots / 50.0, 1.0) * 40
    wave_factor = min(weather.wave_height_m / 8.0, 1.0) * 30
    current_factor = (
        min(weather.current_speed_knots / 4.0, 1.0)
        * (relative / 180.0)
        * 20
    )
    heading_penalty = (relative / 180.0) * 10
    score = min(100.0, wind_factor + wave_factor + current_factor + heading_penalty)
    return PredictRiskResponse(
        risk_score=round(score, 2),
        risk_level=_score_to_level(score),
        relative_heading_deg=round(relative, 2),
    )
