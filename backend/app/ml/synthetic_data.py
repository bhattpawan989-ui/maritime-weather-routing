"""Synthetic maritime datasets with physics-informed labels."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from app.utils.geo import angle_diff_deg

RNG = np.random.default_rng(42)


def _relative_heading(wind_dir: np.ndarray, heading: np.ndarray) -> np.ndarray:
    return np.vectorize(angle_diff_deg)(wind_dir, heading)


def generate_risk_dataset(n_samples: int = 8000) -> pd.DataFrame:
    wind_speed = RNG.uniform(0, 45, n_samples)
    wind_dir = RNG.uniform(0, 360, n_samples)
    wave_height = RNG.uniform(0.2, 8.0, n_samples)
    current_speed = RNG.uniform(0, 3.5, n_samples)
    current_dir = RNG.uniform(0, 360, n_samples)
    heading = RNG.uniform(0, 360, n_samples)
    relative = _relative_heading(wind_dir, heading)

    score = (
        np.minimum(wind_speed / 50.0, 1.0) * 40
        + np.minimum(wave_height / 8.0, 1.0) * 30
        + np.minimum(current_speed / 4.0, 1.0) * (relative / 180.0) * 20
        + (relative / 180.0) * 10
    )
    score = np.clip(score + RNG.normal(0, 2.5, n_samples), 0, 100)

    return pd.DataFrame(
        {
            "wind_speed_knots": wind_speed,
            "wind_direction_deg": wind_dir,
            "wave_height_m": wave_height,
            "current_speed_knots": current_speed,
            "current_direction_deg": current_dir,
            "vessel_heading_deg": heading,
            "relative_heading_deg": relative,
            "risk_score": score,
        }
    )


def generate_speed_dataset(n_samples: int = 8000) -> pd.DataFrame:
    stw = RNG.uniform(8, 18, n_samples)
    wind_speed = RNG.uniform(0, 40, n_samples)
    wave_height = RNG.uniform(0.2, 7.0, n_samples)
    current_speed = RNG.uniform(0, 3.0, n_samples)
    current_dir = RNG.uniform(0, 360, n_samples)
    heading = RNG.uniform(0, 360, n_samples)
    distance_nm = RNG.uniform(20, 800, n_samples)

    current_angle = _relative_heading(current_dir, heading)
    current_component = current_speed * np.cos(np.radians(current_angle))
    weather_penalty = (
        np.minimum(wind_speed / 40.0, 1.0) * 0.5
        + np.minimum(wave_height / 6.0, 1.0) * 0.8
    )
    sog = np.maximum(0.5, stw + current_component - weather_penalty)
    baseline_hours = distance_nm / np.maximum(stw, 0.1)
    actual_hours = distance_nm / sog
    delay_hours = np.maximum(0.0, actual_hours - baseline_hours)
    delay_hours = np.clip(delay_hours + RNG.normal(0, 0.02, n_samples), 0, None)

    return pd.DataFrame(
        {
            "stw_knots": stw,
            "wind_speed_knots": wind_speed,
            "wave_height_m": wave_height,
            "current_speed_knots": current_speed,
            "current_direction_deg": current_dir,
            "vessel_heading_deg": heading,
            "distance_nm": distance_nm,
            "current_component_knots": current_component,
            "weather_penalty_knots": weather_penalty,
            "effective_sog_knots": sog,
            "delay_hours": delay_hours,
        }
    )


def generate_fuel_dataset(n_samples: int = 8000) -> pd.DataFrame:
    stw = RNG.uniform(8, 18, n_samples)
    distance_nm = RNG.uniform(50, 2500, n_samples)
    wind_speed = RNG.uniform(0, 40, n_samples)
    wave_height = RNG.uniform(0.2, 7.0, n_samples)
    base_rate = RNG.uniform(18, 35, n_samples)

    weather_factor = 1.0 + np.minimum(wave_height / 5.0, 1.0) * 0.15
    weather_factor += np.minimum(wind_speed / 40.0, 1.0) * 0.1
    speed_factor = (stw / 12.0) ** 2
    hours = distance_nm / np.maximum(stw, 0.1)
    days = hours / 24.0
    fuel_mt = base_rate * days * speed_factor * weather_factor
    fuel_mt = np.clip(fuel_mt + RNG.normal(0, 0.2, n_samples), 0.1, None)

    return pd.DataFrame(
        {
            "stw_knots": stw,
            "distance_nm": distance_nm,
            "wind_speed_knots": wind_speed,
            "wave_height_m": wave_height,
            "base_fuel_rate_mt_per_day": base_rate,
            "fuel_consumption_mt": fuel_mt,
        }
    )
