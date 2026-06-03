from pydantic import BaseModel, Field, field_validator


class Coordinate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)


class WaypointInput(BaseModel):
    sequence_order: int = Field(..., ge=0)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    name: str | None = None
    vessel_heading_deg: float | None = Field(None, ge=0, lt=360)

    @field_validator("sequence_order")
    @classmethod
    def validate_sequence(cls, value: int) -> int:
        return value


class WeatherConditions(BaseModel):
    wind_speed_knots: float = Field(..., ge=0)
    wind_direction_deg: float = Field(..., ge=0, lt=360)
    wave_height_m: float = Field(..., ge=0)
    current_speed_knots: float = Field(..., ge=0)
    current_direction_deg: float = Field(..., ge=0, lt=360)
