from app.ml.inference import InferenceService
from app.schemas.common import WeatherConditions
from app.schemas.fuel import PredictFuelRequest
from app.schemas.risk import PredictRiskRequest
from app.schemas.speed import PredictSpeedRequest


def test_risk_model_inference(inference_service: InferenceService):
    payload = PredictRiskRequest(
        weather=WeatherConditions(
            wind_speed_knots=25,
            wind_direction_deg=180,
            wave_height_m=3.5,
            current_speed_knots=1.2,
            current_direction_deg=90,
        ),
        vessel_heading_deg=0,
    )
    result = inference_service.risk.predict(payload)
    assert 0 <= result.risk_score <= 100
    assert result.risk_level.value in {"safe", "moderate", "dangerous"}


def test_speed_model_inference(inference_service: InferenceService):
    payload = PredictSpeedRequest(
        stw_knots=12,
        weather=WeatherConditions(
            wind_speed_knots=20,
            wind_direction_deg=200,
            wave_height_m=2.5,
            current_speed_knots=1.0,
            current_direction_deg=45,
        ),
        vessel_heading_deg=90,
        distance_nm=300,
    )
    result = inference_service.speed.predict(payload)
    assert result.effective_sog_knots > 0
    assert result.delay_hours >= 0


def test_fuel_model_inference(inference_service: InferenceService):
    payload = PredictFuelRequest(
        stw_knots=14,
        distance_nm=500,
        weather=WeatherConditions(
            wind_speed_knots=18,
            wind_direction_deg=270,
            wave_height_m=2.0,
            current_speed_knots=0.5,
            current_direction_deg=180,
        ),
        base_fuel_rate_mt_per_day=28,
    )
    result = inference_service.fuel.predict(payload)
    assert result.fuel_consumption_mt > 0
    assert result.fuel_cost_usd > 0
