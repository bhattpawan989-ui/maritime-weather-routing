"""Run from backend directory: python scripts/train_all_models.py"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.ml.fuel.train import train_fuel_model
from app.ml.risk.train import train_risk_model
from app.ml.speed.train import train_speed_model


def main() -> None:
    print("Training risk model...")
    print(train_risk_model())
    print("Training speed model...")
    print(train_speed_model())
    print("Training fuel model...")
    print(train_fuel_model())
    print("All models trained successfully.")


if __name__ == "__main__":
    main()
