from __future__ import annotations

from app.ml.base import ModelMetadata, save_model, utc_now_iso
from app.ml.fuel.model import FEATURE_COLUMNS, MODEL_KEY
from app.ml.synthetic_data import generate_fuel_dataset
from app.ml.training import train_regression_pipeline


def train_fuel_model(n_samples: int = 8000) -> str:
    df = generate_fuel_dataset(n_samples)
    pipeline, metrics = train_regression_pipeline(
        df, FEATURE_COLUMNS, "fuel_consumption_mt"
    )
    metadata = ModelMetadata(
        model_name="gradient_boosting_fuel",
        version="1.0.0",
        target="fuel_consumption_mt",
        features=FEATURE_COLUMNS,
        metrics=metrics,
        trained_at=utc_now_iso(),
        n_samples=n_samples,
    )
    path = save_model(MODEL_KEY, pipeline, metadata)
    return str(path)


if __name__ == "__main__":
    trained_path = train_fuel_model()
    print(f"Fuel model saved to {trained_path}")
