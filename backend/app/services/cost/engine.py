from app.core.config import settings
from app.schemas.cost import CalculateCostRequest, CalculateCostResponse


def calculate_cost(payload: CalculateCostRequest) -> CalculateCostResponse:
    fuel_price = payload.fuel_price_usd_per_mt or settings.fuel_price_usd_per_mt
    co2_factor = payload.co2_kg_per_mt_fuel or settings.co2_kg_per_mt_fuel
    weather_multiplier = 1.0
    if payload.weather:
        weather_multiplier += min(payload.weather.wave_height_m / 6.0, 1.0) * 0.05

    fuel_cost = payload.fuel_consumption_mt * fuel_price * weather_multiplier
    co2_kg = payload.fuel_consumption_mt * co2_factor
    co2_cost = co2_kg * 0.05
    canal = payload.canal_cost_usd
    total = fuel_cost + co2_cost + canal
    return CalculateCostResponse(
        fuel_cost_usd=round(fuel_cost, 2),
        co2_cost_usd=round(co2_cost, 2),
        canal_cost_usd=round(canal, 2),
        total_voyage_cost_usd=round(total, 2),
        co2_emissions_kg=round(co2_kg, 2),
    )
