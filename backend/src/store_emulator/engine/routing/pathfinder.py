from pathfinding.core.diagonal_movement import DiagonalMovement  # type: ignore[reportMissingTypeStubs]
from pathfinding.core.grid import Grid  # type: ignore[reportMissingTypeStubs]
from pathfinding.finder.a_star import AStarFinder  # type: ignore[reportMissingTypeStubs]

from store_emulator.domain.types import Position


class AStarPathFinder:
    def __init__(self) -> None:
        self._finder = AStarFinder(  # type: ignore[reportUnknownMemberType]
            diagonal_movement=DiagonalMovement.never,
        )

    def find_path(
        self,
        walkable_grid: list[list[bool]],
        start: Position,
        end: Position,
    ) -> list[Position]:
        matrix = [[int(cell) for cell in row] for row in walkable_grid]
        grid = Grid(matrix=matrix)  # type: ignore[reportUnknownMemberType]
        start_node = grid.node(start[0], start[1])  # type: ignore[reportUnknownMemberType]
        end_node = grid.node(end[0], end[1])  # type: ignore[reportUnknownMemberType]
        path_nodes, _ = self._finder.find_path(start_node, end_node, grid)  # type: ignore[reportUnknownMemberType]
        return [(node.x, node.y) for node in path_nodes]  # type: ignore[reportUnknownMemberType]
