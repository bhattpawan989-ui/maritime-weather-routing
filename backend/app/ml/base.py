from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from sklearn.pipeline import Pipeline

from app.core.config import get_settings


@dataclass(frozen=True)
class ModelMetadata:
    model_name: str
    version: str
    target: str
    features: list[str]
    metrics: dict[str, float]
    trained_at: str
    n_samples: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SavedModel:
    pipeline: Pipeline
    metadata: ModelMetadata


def artifact_dir(model_key: str) -> Path:
    path = get_settings().ml_artifacts_dir / model_key
    path.mkdir(parents=True, exist_ok=True)
    return path


def model_path(model_key: str) -> Path:
    return artifact_dir(model_key) / "model.pkl"


def metadata_path(model_key: str) -> Path:
    return artifact_dir(model_key) / "metadata.json"


def save_model(model_key: str, pipeline: Pipeline, metadata: ModelMetadata) -> Path:
    target = model_path(model_key)
    joblib.dump(pipeline, target)
    meta_file = metadata_path(model_key)
    meta_file.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
    return target


def load_model(model_key: str) -> SavedModel | None:
    target = model_path(model_key)
    meta_file = metadata_path(model_key)
    if not target.exists():
        return None
    pipeline: Pipeline = joblib.load(target)
    metadata_dict: dict[str, Any] = {}
    if meta_file.exists():
        metadata_dict = json.loads(meta_file.read_text(encoding="utf-8"))
    metadata = ModelMetadata(
        model_name=metadata_dict.get("model_name", model_key),
        version=metadata_dict.get("version", "unknown"),
        target=metadata_dict.get("target", ""),
        features=metadata_dict.get("features", []),
        metrics=metadata_dict.get("metrics", {}),
        trained_at=metadata_dict.get(
            "trained_at", datetime.now(timezone.utc).isoformat()
        ),
        n_samples=int(metadata_dict.get("n_samples", 0)),
    )
    return SavedModel(pipeline=pipeline, metadata=metadata)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
