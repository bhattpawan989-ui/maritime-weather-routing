from __future__ import annotations

import pandas as pd

import math

from app.ml.base import SavedModel, load_model, model_path
from app.schemas.speed import PredictSpeedRequest, PredictSpeedResponse
from app.utils.geo import angle_diff_deg

MODEL_KEY = "speed"
FEATURE_COLUMNS = [
    "stw_knots",
    "wind_speed_knots",
    "wave_height_m",
    "current_speed_knots",
    "current_direction_deg",
    "vessel_heading_deg",
    "distance_nm",
    "current_component_knots",
    "weather_penalty_knots",
]


class SpeedPredictionModel:
    def __init__(self) -> None:
        self._saved: SavedModel | None = None

    @property
    def is_loaded(self) -> bool:
        return self._saved is not None

    def load(self) -> bool:
        self._saved = load_model(MODEL_KEY)
        return self._saved is not None

    def predict(self, payload: PredictSpeedRequest) -> PredictSpeedResponse:
        if self._saved is None and not self.load():
            raise RuntimeError(f"Speed model not found at {model_path(MODEL_KEY)}")

        weather = payload.weather
        current_angle = angle_diff_deg(
            weather.current_direction_deg, payload.vessel_heading_deg
        )
        current_component = weather.current_speed_knots * math.cos(
            math.radians(current_angle)
        )
        weather_penalty = (
            min(weather.wind_speed_knots / 40.0, 1.0) * 0.5
            + min(weather.wave_height_m / 6.0, 1.0) * 0.8
        )
        features = pd.DataFrame(
            [
                {
                    "stw_knots": payload.stw_knots,
                    "wind_speed_knots": weather.wind_speed_knots,
                    "wave_height_m": weather.wave_height_m,
                    "current_speed_knots": weather.current_speed_knots,
                    "current_direction_deg": weather.current_direction_deg,
                    "vessel_heading_deg": payload.vessel_heading_deg,
                    "distance_nm": payload.distance_nm,
                    "current_component_knots": current_component,
                    "weather_penalty_knots": weather_penalty,
                }
            ]
        )
        delay_hours = max(0.0, float(self._saved.pipeline.predict(features)[0]))
        stw = max(payload.stw_knots, 0.1)
        baseline_hours = payload.distance_nm / stw if payload.distance_nm > 0 else 0.0
        effective_sog = (
            payload.distance_nm / max(baseline_hours + delay_hours, 1e-6)
            if payload.distance_nm > 0
            else stw
        )
        effective_sog = max(0.1, effective_sog)
        return PredictSpeedResponse(
            effective_sog_knots=round(effective_sog, 2),
            delay_hours=round(delay_hours, 2),
        )
