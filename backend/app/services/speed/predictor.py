import math

from app.core.config import settings
from app.schemas.speed import PredictSpeedRequest, PredictSpeedResponse
from app.utils.geo import angle_diff_deg


def _predict_speed_heuristic(payload: PredictSpeedRequest) -> PredictSpeedResponse:
    weather = payload.weather
    current_angle = angle_diff_deg(
        weather.current_direction_deg, payload.vessel_heading_deg
    )
    current_component = weather.current_speed_knots * math.cos(math.radians(current_angle))
    weather_penalty = (
        min(weather.wind_speed_knots / 40.0, 1.0) * 0.5
        + min(weather.wave_height_m / 6.0, 1.0) * 0.8
    )
    effective_sog = max(0.1, payload.stw_knots + current_component - weather_penalty)
    baseline_hours = payload.distance_nm / max(payload.stw_knots, 0.1)
    actual_hours = payload.distance_nm / effective_sog
    delay_hours = max(0.0, actual_hours - baseline_hours)
    return PredictSpeedResponse(
        effective_sog_knots=round(effective_sog, 2),
        delay_hours=round(delay_hours, 2),
    )


def predict_speed(payload: PredictSpeedRequest) -> PredictSpeedResponse:
    if settings.ml_enabled:
        from app.ml.inference import get_inference_service

        service = get_inference_service()
        if service.speed_available:
            return service.speed.predict(payload)
    if settings.ml_fallback_to_heuristic:
        return _predict_speed_heuristic(payload)
    raise RuntimeError("Speed ML model unavailable and heuristic fallback is disabled")
