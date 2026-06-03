from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import get_settings
from app.ml.inference import InferenceService, get_inference_service


@pytest.fixture(autouse=True)
def _reset_cached_singletons() -> None:
    get_settings.cache_clear()
    get_inference_service.cache_clear()
    yield
    get_settings.cache_clear()
    get_inference_service.cache_clear()


@pytest.fixture
def artifacts_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("ML_ARTIFACTS_DIR", str(tmp_path))
    get_settings.cache_clear()
    assert get_settings().ml_artifacts_dir.resolve() == tmp_path.resolve()
    return tmp_path


@pytest.fixture
def trained_models(artifacts_dir: Path) -> Path:
    from app.ml.fuel.train import train_fuel_model
    from app.ml.risk.train import train_risk_model
    from app.ml.speed.train import train_speed_model

    train_risk_model(n_samples=1500)
    train_speed_model(n_samples=1500)
    train_fuel_model(n_samples=1500)
    return artifacts_dir


@pytest.fixture
def inference_service(trained_models: Path) -> InferenceService:
    get_settings.cache_clear()
    service = InferenceService()
    service.initialize()
    return service
