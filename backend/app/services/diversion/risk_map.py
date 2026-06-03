import math

from app.schemas.diversion import WeatherRiskZone
from app.schemas.risk import RiskLevelLabel
from app.utils.geo import haversine_nm

RISK_LEVEL_SCORES: dict[RiskLevelLabel, float] = {
    RiskLevelLabel.SAFE: 20.0,
    RiskLevelLabel.MODERATE: 55.0,
    RiskLevelLabel.DANGEROUS: 85.0,
}


def zone_peak_risk(zone: WeatherRiskZone) -> float:
    if zone.risk_score is not None:
        return zone.risk_score
    return RISK_LEVEL_SCORES[zone.min_risk_level]


def point_risk(lat: float, lon: float, zones: list[WeatherRiskZone]) -> float:
    if not zones:
        return 0.0
    peak = 0.0
    for zone in zones:
        distance_nm = haversine_nm(lat, lon, zone.center.lat, zone.center.lon)
        if distance_nm >= zone.radius_nm:
            continue
        center_risk = zone_peak_risk(zone)
        if zone.radius_nm <= 0:
            local = center_risk
        else:
            falloff = 1.0 - (distance_nm / zone.radius_nm)
            local = center_risk * max(0.0, falloff**1.5)
        peak = max(peak, local)
    return min(100.0, peak)


def traversal_cost_multiplier(risk: float, blocked_threshold: float) -> float | None:
    if risk >= blocked_threshold:
        return None
    return 1.0 + (risk / 100.0) * 4.0


def is_blocked(lat: float, lon: float, zones: list[WeatherRiskZone], threshold: float) -> bool:
    return point_risk(lat, lon, zones) >= threshold
