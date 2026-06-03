import heapq
from dataclasses import dataclass, field

from app.services.diversion.grid import NavigationGrid
from app.utils.geo import haversine_nm

NEIGHBORS = (
    (-1, 0, 1.0),
    (1, 0, 1.0),
    (0, -1, 1.0),
    (0, 1, 1.0),
    (-1, -1, 1.414),
    (-1, 1, 1.414),
    (1, -1, 1.414),
    (1, 1, 1.414),
)


@dataclass(order=True)
class _QueueNode:
    f_score: float
    g_score: float = field(compare=False)
    row: int = field(compare=False)
    col: int = field(compare=False)


class AStarPathfinder:
    def __init__(self, grid: NavigationGrid) -> None:
        self.grid = grid

    def find_path(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> list[tuple[int, int]] | None:
        start_cell = self.grid.nearest_passable(*start)
        goal_cell = self.grid.nearest_passable(*goal)
        if start_cell is None or goal_cell is None:
            return None
        if start_cell == goal_cell:
            return [start_cell]

        open_heap: list[_QueueNode] = []
        heapq.heappush(open_heap, _QueueNode(0.0, 0.0, start_cell[0], start_cell[1]))
        came_from: dict[tuple[int, int], tuple[int, int] | None] = {start_cell: None}
        g_scores: dict[tuple[int, int], float] = {start_cell: 0.0}
        closed: set[tuple[int, int]] = set()

        while open_heap:
            current = heapq.heappop(open_heap)
            if (current.row, current.col) in closed:
                continue
            if (current.row, current.col) == goal_cell:
                return self._reconstruct(came_from, goal_cell)

            closed.add((current.row, current.col))
            for dr, dc, step_factor in NEIGHBORS:
                nr, nc = current.row + dr, current.col + dc
                if not self.grid.is_passable(nr, nc):
                    continue
                lat1, lon1 = self.grid.cell_to_latlon(current.row, current.col)
                lat2, lon2 = self.grid.cell_to_latlon(nr, nc)
                step_nm = haversine_nm(lat1, lon1, lat2, lon2)
                step_cost = (
                    step_nm
                    * step_factor
                    * self.grid.movement_cost(nr, nc)
                )
                tentative_g = g_scores[(current.row, current.col)] + step_cost
                neighbor = (nr, nc)
                if tentative_g >= g_scores.get(neighbor, float("inf")):
                    continue
                came_from[neighbor] = (current.row, current.col)
                g_scores[neighbor] = tentative_g
                h_score = self._heuristic(nr, nc, goal_cell[0], goal_cell[1])
                heapq.heappush(
                    open_heap,
                    _QueueNode(tentative_g + h_score, tentative_g, nr, nc),
                )
        return None

    def _heuristic(self, row: int, col: int, goal_row: int, goal_col: int) -> float:
        lat1, lon1 = self.grid.cell_to_latlon(row, col)
        lat2, lon2 = self.grid.cell_to_latlon(goal_row, goal_col)
        return haversine_nm(lat1, lon1, lat2, lon2)

    @staticmethod
    def _reconstruct(
        came_from: dict[tuple[int, int], tuple[int, int] | None],
        current: tuple[int, int],
    ) -> list[tuple[int, int]]:
        path = [current]
        while came_from[current] is not None:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
