from __future__ import annotations

import pandas as pd

from app.ml.base import SavedModel, load_model, model_path
from app.schemas.risk import PredictRiskRequest, PredictRiskResponse, RiskLevelLabel
from app.utils.geo import angle_diff_deg

MODEL_KEY = "risk"
FEATURE_COLUMNS = [
    "wind_speed_knots",
    "wind_direction_deg",
    "wave_height_m",
    "current_speed_knots",
    "current_direction_deg",
    "relative_heading_deg",
]


def _score_to_level(score: float) -> RiskLevelLabel:
    if score < 33:
        return RiskLevelLabel.SAFE
    if score < 66:
        return RiskLevelLabel.MODERATE
    return RiskLevelLabel.DANGEROUS


class RiskPredictionModel:
    def __init__(self) -> None:
        self._saved: SavedModel | None = None

    @property
    def is_loaded(self) -> bool:
        return self._saved is not None

    def load(self) -> bool:
        self._saved = load_model(MODEL_KEY)
        return self._saved is not None

    def predict(self, payload: PredictRiskRequest) -> PredictRiskResponse:
        if self._saved is None and not self.load():
            raise RuntimeError(f"Risk model not found at {model_path(MODEL_KEY)}")

        weather = payload.weather
        relative = angle_diff_deg(
            weather.wind_direction_deg, payload.vessel_heading_deg
        )
        features = pd.DataFrame(
            [
                {
                    "wind_speed_knots": weather.wind_speed_knots,
                    "wind_direction_deg": weather.wind_direction_deg,
                    "wave_height_m": weather.wave_height_m,
                    "current_speed_knots": weather.current_speed_knots,
                    "current_direction_deg": weather.current_direction_deg,
                    "relative_heading_deg": relative,
                }
            ]
        )
        score = float(self._saved.pipeline.predict(features)[0])
        score = max(0.0, min(100.0, score))
        return PredictRiskResponse(
            risk_score=round(score, 2),
            risk_level=_score_to_level(score),
            relative_heading_deg=round(relative, 2),
        )

    @property
    def version(self) -> str:
        if self._saved:
            return self._saved.metadata.version
        return "unloaded"
