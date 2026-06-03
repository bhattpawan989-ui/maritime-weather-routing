import math
from dataclasses import dataclass

from app.schemas.diversion import WeatherRiskZone
from app.services.diversion.risk_map import point_risk, traversal_cost_multiplier
from app.utils.geo import haversine_nm


@dataclass(frozen=True)
class GridBounds:
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float


class NavigationGrid:
    def __init__(
        self,
        bounds: GridBounds,
        cell_size_nm: float,
        zones: list[WeatherRiskZone],
        blocked_threshold: float = 88.0,
    ) -> None:
        self.bounds = bounds
        self.cell_size_nm = cell_size_nm
        self.zones = zones
        self.blocked_threshold = blocked_threshold

        lat_span_nm = haversine_nm(bounds.min_lat, bounds.min_lon, bounds.max_lat, bounds.min_lon)
        lon_span_nm = haversine_nm(bounds.min_lat, bounds.min_lon, bounds.min_lat, bounds.max_lon)
        self.n_rows = max(3, int(math.ceil(lat_span_nm / cell_size_nm)) + 1)
        self.n_cols = max(3, int(math.ceil(lon_span_nm / cell_size_nm)) + 1)

        self._cost: list[list[float | None]] = []
        self._build_cost_matrix()

    def _build_cost_matrix(self) -> None:
        self._cost = []
        for row in range(self.n_rows):
            row_costs: list[float | None] = []
            for col in range(self.n_cols):
                lat, lon = self.cell_to_latlon(row, col)
                risk = point_risk(lat, lon, self.zones)
                multiplier = traversal_cost_multiplier(risk, self.blocked_threshold)
                row_costs.append(multiplier)
            self._cost.append(row_costs)

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.n_rows and 0 <= col < self.n_cols

    def is_passable(self, row: int, col: int) -> bool:
        if not self.in_bounds(row, col):
            return False
        return self._cost[row][col] is not None

    def movement_cost(self, row: int, col: int) -> float:
        value = self._cost[row][col]
        return 1.0 if value is None else value

    def cell_to_latlon(self, row: int, col: int) -> tuple[float, float]:
        lat_step = (self.bounds.max_lat - self.bounds.min_lat) / max(self.n_rows - 1, 1)
        lon_step = (self.bounds.max_lon - self.bounds.min_lon) / max(self.n_cols - 1, 1)
        lat = self.bounds.min_lat + row * lat_step
        lon = self.bounds.min_lon + col * lon_step
        return lat, lon

    def latlon_to_cell(self, lat: float, lon: float) -> tuple[int, int]:
        lat_step = (self.bounds.max_lat - self.bounds.min_lat) / max(self.n_rows - 1, 1)
        lon_step = (self.bounds.max_lon - self.bounds.min_lon) / max(self.n_cols - 1, 1)
        if lat_step == 0:
            row = self.n_rows // 2
        else:
            row = int(round((lat - self.bounds.min_lat) / lat_step))
        if lon_step == 0:
            col = self.n_cols // 2
        else:
            col = int(round((lon - self.bounds.min_lon) / lon_step))
        row = min(max(row, 0), self.n_rows - 1)
        col = min(max(col, 0), self.n_cols - 1)
        return row, col

    def nearest_passable(self, row: int, col: int) -> tuple[int, int] | None:
        if self.is_passable(row, col):
            return row, col
        max_radius = max(self.n_rows, self.n_cols)
        for radius in range(1, max_radius):
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    nr, nc = row + dr, col + dc
                    if self.is_passable(nr, nc):
                        return nr, nc
        return None


def build_grid_bounds(
    coords: list[tuple[float, float]],
    zones: list[WeatherRiskZone],
    padding_nm: float = 30.0,
) -> GridBounds:
    lats = [lat for lat, _ in coords]
    lons = [lon for _, lon in coords]
    for zone in zones:
        pad_lat = padding_nm / 60.0
        pad_lon = padding_nm / (60.0 * max(math.cos(math.radians(zone.center.lat)), 0.01))
        zone_pad_lat = zone.radius_nm / 60.0
        zone_pad_lon = zone.radius_nm / (
            60.0 * max(math.cos(math.radians(zone.center.lat)), 0.01)
        )
        lats.extend(
            [
                zone.center.lat - pad_lat - zone_pad_lat,
                zone.center.lat + pad_lat + zone_pad_lat,
            ]
        )
        lons.extend(
            [
                zone.center.lon - pad_lon - zone_pad_lon,
                zone.center.lon + pad_lon + zone_pad_lon,
            ]
        )
    return GridBounds(
        min_lat=min(lats),
        max_lat=max(lats),
        min_lon=min(lons),
        max_lon=max(lons),
    )
