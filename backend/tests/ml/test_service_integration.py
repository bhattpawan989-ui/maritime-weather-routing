from app.core.config import get_settings
from app.ml.inference import get_inference_service
from app.schemas.common import WeatherConditions
from app.schemas.fuel import PredictFuelRequest
from app.schemas.risk import PredictRiskRequest
from app.schemas.speed import PredictSpeedRequest
from app.services.fuel.predictor import predict_fuel
from app.services.risk.predictor import get_risk_model_version, predict_risk
from app.services.speed.predictor import predict_speed


def test_services_use_ml_when_models_available(trained_models):
    get_settings.cache_clear()
    get_inference_service.cache_clear()

    risk = predict_risk(
        PredictRiskRequest(
            weather=WeatherConditions(
                wind_speed_knots=30,
                wind_direction_deg=120,
                wave_height_m=4,
                current_speed_knots=1.5,
                current_direction_deg=200,
            ),
            vessel_heading_deg=45,
        )
    )
    assert risk.risk_score >= 0
    assert get_risk_model_version() != "heuristic-v1"

    speed = predict_speed(
        PredictSpeedRequest(
            stw_knots=12,
            weather=WeatherConditions(
                wind_speed_knots=22,
                wind_direction_deg=180,
                wave_height_m=3,
                current_speed_knots=1.0,
                current_direction_deg=90,
            ),
            vessel_heading_deg=0,
            distance_nm=200,
        )
    )
    assert speed.delay_hours >= 0

    fuel = predict_fuel(
        PredictFuelRequest(
            stw_knots=13,
            distance_nm=400,
            weather=WeatherConditions(
                wind_speed_knots=15,
                wind_direction_deg=90,
                wave_height_m=2,
                current_speed_knots=0.8,
                current_direction_deg=270,
            ),
            base_fuel_rate_mt_per_day=26,
        )
    )
    assert fuel.fuel_consumption_mt > 0
