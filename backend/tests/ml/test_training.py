from pathlib import Path

from app.ml.base import load_model, metadata_path, model_path
from app.ml.fuel.train import train_fuel_model
from app.ml.risk.train import train_risk_model
from app.ml.speed.train import train_speed_model
from app.ml.synthetic_data import (
    generate_fuel_dataset,
    generate_risk_dataset,
    generate_speed_dataset,
)


def test_synthetic_datasets_have_expected_columns():
    risk_df = generate_risk_dataset(100)
    assert "risk_score" in risk_df.columns
    speed_df = generate_speed_dataset(100)
    assert "delay_hours" in speed_df.columns
    fuel_df = generate_fuel_dataset(100)
    assert "fuel_consumption_mt" in fuel_df.columns


def test_train_and_persist_models(artifacts_dir: Path):
    train_risk_model(n_samples=5000)
    train_speed_model(n_samples=5000)
    train_fuel_model(n_samples=5000)

    for key in ("risk", "speed", "fuel"):
        assert model_path(key).resolve().parent.parent == artifacts_dir.resolve()
        assert metadata_path(key).exists()
        saved = load_model(key)
        assert saved is not None
        assert saved.metadata.metrics["r2"] > 0.9
        assert saved.metadata.metrics["mae"] < 5.0
