from __future__ import annotations

from app.ml.base import ModelMetadata, save_model, utc_now_iso
from app.ml.speed.model import FEATURE_COLUMNS, MODEL_KEY
from app.ml.synthetic_data import generate_speed_dataset
from app.ml.training import train_regression_pipeline


def train_speed_model(n_samples: int = 8000) -> str:
    df = generate_speed_dataset(n_samples)
    pipeline, metrics = train_regression_pipeline(
        df, FEATURE_COLUMNS, "delay_hours", n_estimators=400
    )
    metadata = ModelMetadata(
        model_name="gradient_boosting_speed",
        version="1.0.0",
        target="delay_hours",
        features=FEATURE_COLUMNS,
        metrics=metrics,
        trained_at=utc_now_iso(),
        n_samples=n_samples,
    )
    path = save_model(MODEL_KEY, pipeline, metadata)
    return str(path)


if __name__ == "__main__":
    trained_path = train_speed_model()
    print(f"Speed model saved to {trained_path}")
