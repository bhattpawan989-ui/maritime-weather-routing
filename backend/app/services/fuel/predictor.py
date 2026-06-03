from app.core.config import settings
from app.schemas.fuel import PredictFuelRequest, PredictFuelResponse


def predict_fuel(payload: PredictFuelRequest) -> PredictFuelResponse:
    price = payload.fuel_price_usd_per_mt or settings.fuel_price_usd_per_mt
    weather_factor = 1.0 + min(payload.weather.wave_height_m / 5.0, 1.0) * 0.15
    weather_factor += min(payload.weather.wind_speed_knots / 40.0, 1.0) * 0.1
    speed_factor = (payload.stw_knots / 12.0) ** 2
    hours = payload.distance_nm / max(payload.stw_knots, 0.1)
    days = hours / 24.0
    fuel_mt = payload.base_fuel_rate_mt_per_day * days * speed_factor * weather_factor
    return PredictFuelResponse(
        fuel_consumption_mt=round(fuel_mt, 4),
        fuel_cost_usd=round(fuel_mt * price, 2),
    )
