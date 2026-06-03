from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def build_regressor(n_estimators: int = 250) -> GradientBoostingRegressor:
    return GradientBoostingRegressor(
        n_estimators=n_estimators,
        learning_rate=0.08,
        max_depth=5,
        random_state=42,
    )


def train_regression_pipeline(
    df: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
    test_size: float = 0.2,
    n_estimators: int = 250,
) -> tuple[Pipeline, dict[str, float]]:
    x_train, x_test, y_train, y_test = train_test_split(
        df[feature_columns],
        df[target_column],
        test_size=test_size,
        random_state=42,
    )
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("model", build_regressor(n_estimators=n_estimators)),
        ]
    )
    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test)
    metrics = {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "r2": float(r2_score(y_test, predictions)),
    }
    return pipeline, metrics
