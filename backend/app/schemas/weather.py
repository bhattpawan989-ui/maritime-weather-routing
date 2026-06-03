from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Coordinate


class WaypointWeather(BaseModel):
    sequence_order: int
    lat: float
    lon: float
    wind_speed_knots: float
    wind_direction_deg: float
    wave_height_m: float
    current_speed_knots: float
    current_direction_deg: float
    forecast_time: datetime | None = None


class WeatherAtPointRequest(BaseModel):
    coordinate: Coordinate
