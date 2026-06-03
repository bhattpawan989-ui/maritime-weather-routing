import math
from datetime import datetime, timezone

from app.schemas.common import Coordinate
from app.schemas.weather import WaypointWeather


def _pseudo_noise(lat: float, lon: float, seed: int) -> float:
    value = math.sin(lat * 12.9898 + lon * 78.233 + seed) * 43758.5453
    return value - math.floor(value)


def get_weather_at_point(coordinate: Coordinate) -> WaypointWeather:
    lat, lon = coordinate.lat, coordinate.lon
    wind_speed = 5 + _pseudo_noise(lat, lon, 1) * 30
    wind_dir = _pseudo_noise(lat, lon, 2) * 360
    wave_height = 0.5 + _pseudo_noise(lat, lon, 3) * 5.5
    current_speed = _pseudo_noise(lat, lon, 4) * 3
    current_dir = _pseudo_noise(lat, lon, 5) * 360
    return WaypointWeather(
        sequence_order=0,
        lat=lat,
        lon=lon,
        wind_speed_knots=round(wind_speed, 2),
        wind_direction_deg=round(wind_dir, 2),
        wave_height_m=round(wave_height, 2),
        current_speed_knots=round(current_speed, 2),
        current_direction_deg=round(current_dir, 2),
        forecast_time=datetime.now(timezone.utc),
    )


def get_weather_for_waypoint(
    sequence_order: int, lat: float, lon: float
) -> WaypointWeather:
    weather = get_weather_at_point(Coordinate(lat=lat, lon=lon))
    weather.sequence_order = sequence_order
    return weather
