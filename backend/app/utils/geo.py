import math
from typing import Sequence


def haversine_nm(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_nm = 3440.065
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius_nm * math.asin(min(1.0, math.sqrt(a)))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(
        d_lambda
    )
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def angle_diff_deg(a: float, b: float) -> float:
    diff = abs(a - b) % 360
    return diff if diff <= 180 else 360 - diff


def linestring_length_nm(coords: Sequence[tuple[float, float]]) -> float:
    total = 0.0
    for i in range(1, len(coords)):
        total += haversine_nm(coords[i - 1][0], coords[i - 1][1], coords[i][0], coords[i][1])
    return total


def offset_coordinate(lat: float, lon: float, bearing: float, distance_nm: float) -> tuple[float, float]:
    bearing_rad = math.radians(bearing)
    dlat = (distance_nm / 60.0) * math.cos(bearing_rad)
    dlon = (distance_nm / 60.0) * math.sin(bearing_rad) / max(
        math.cos(math.radians(lat)), 0.01
    )
    return lat + dlat, lon + dlon
