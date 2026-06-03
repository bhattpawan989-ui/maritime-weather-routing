from dataclasses import dataclass

from app.schemas.diversion import WeatherRiskZone
from app.services.diversion.risk_map import point_risk
from app.utils.geo import haversine_nm, linestring_length_nm


@dataclass(frozen=True)
class RouteScore:
    distance_nm: float
    average_risk: float
    exposure_index: float
    composite_score: float


def _sample_points(
    coords: list[tuple[float, float]], sample_spacing_nm: float = 10.0
) -> list[tuple[float, float]]:
    if len(coords) < 2:
        return list(coords)
    samples: list[tuple[float, float]] = [coords[0]]
    for i in range(1, len(coords)):
        lat1, lon1 = coords[i - 1]
        lat2, lon2 = coords[i]
        leg_nm = haversine_nm(lat1, lon1, lat2, lon2)
        if leg_nm <= 0:
            continue
        steps = max(1, int(leg_nm / sample_spacing_nm))
        for step in range(1, steps + 1):
            fraction = step / steps
            samples.append(
                (
                    lat1 + (lat2 - lat1) * fraction,
                    lon1 + (lon2 - lon1) * fraction,
                )
            )
    return samples


def score_route(
    coords: list[tuple[float, float]],
    zones: list[WeatherRiskZone],
    sample_spacing_nm: float = 10.0,
) -> RouteScore:
    if not coords:
        return RouteScore(0.0, 0.0, 0.0, 0.0)

    distance = linestring_length_nm(coords)
    samples = _sample_points(coords, sample_spacing_nm)
    if not samples:
        return RouteScore(distance, 0.0, 0.0, 0.0)

    risks = [point_risk(lat, lon, zones) for lat, lon in samples]
    average_risk = sum(risks) / len(risks)
    exposure_index = sum(risks) * (distance / len(samples))
    composite = distance * (1.0 + average_risk / 100.0) + exposure_index * 0.05
    return RouteScore(
        distance_nm=round(distance, 2),
        average_risk=round(average_risk, 2),
        exposure_index=round(exposure_index, 2),
        composite_score=round(composite, 2),
    )


def risk_reduction_score(original: RouteScore, alternative: RouteScore) -> float:
    if original.exposure_index <= 0:
        return 100.0 if alternative.exposure_index <= 0 else 0.0
    reduction = (original.exposure_index - alternative.exposure_index) / original.exposure_index
    return round(max(0.0, min(100.0, reduction * 100.0)), 2)
