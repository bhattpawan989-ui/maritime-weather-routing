from __future__ import annotations

from functools import lru_cache

from app.core.config import settings
from app.ml.fuel.model import FuelPredictionModel
from app.ml.risk.model import RiskPredictionModel
from app.ml.speed.model import SpeedPredictionModel


class InferenceService:
    def __init__(self) -> None:
        self.risk = RiskPredictionModel()
        self.speed = SpeedPredictionModel()
        self.fuel = FuelPredictionModel()
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        if settings.ml_enabled:
            self.risk.load()
            self.speed.load()
            self.fuel.load()
        self._initialized = True

    @property
    def risk_available(self) -> bool:
        self.initialize()
        return self.risk.is_loaded

    @property
    def speed_available(self) -> bool:
        self.initialize()
        return self.speed.is_loaded

    @property
    def fuel_available(self) -> bool:
        self.initialize()
        return self.fuel.is_loaded


@lru_cache
def get_inference_service() -> InferenceService:
    service = InferenceService()
    service.initialize()
    return service
