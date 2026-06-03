from __future__ import annotations

import pandas as pd

from app.core.config import settings
from app.ml.base import SavedModel, load_model, model_path
from app.schemas.fuel import PredictFuelRequest, PredictFuelResponse

MODEL_KEY = "fuel"
FEATURE_COLUMNS = [
    "stw_knots",
    "distance_nm",
    "wind_speed_knots",
    "wave_height_m",
    "base_fuel_rate_mt_per_day",
]


class FuelPredictionModel:
    def __init__(self) -> None:
        self._saved: SavedModel | None = None

    @property
    def is_loaded(self) -> bool:
        return self._saved is not None

    def load(self) -> bool:
        self._saved = load_model(MODEL_KEY)
        return self._saved is not None

    def predict(self, payload: PredictFuelRequest) -> PredictFuelResponse:
        if self._saved is None and not self.load():
            raise RuntimeError(f"Fuel model not found at {model_path(MODEL_KEY)}")

        weather = payload.weather
        features = pd.DataFrame(
            [
                {
                    "stw_knots": payload.stw_knots,
                    "distance_nm": payload.distance_nm,
                    "wind_speed_knots": weather.wind_speed_knots,
                    "wave_height_m": weather.wave_height_m,
                    "base_fuel_rate_mt_per_day": payload.base_fuel_rate_mt_per_day,
                }
            ]
        )
        fuel_mt = max(0.01, float(self._saved.pipeline.predict(features)[0]))
        price = payload.fuel_price_usd_per_mt or settings.fuel_price_usd_per_mt
        return PredictFuelResponse(
            fuel_consumption_mt=round(fuel_mt, 4),
            fuel_cost_usd=round(fuel_mt * price, 2),
        )
