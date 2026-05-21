from store_emulator.domain.store import Store
from store_emulator.domain.types import Position
from .pathfinder import AStarPathFinder


def compute_pathcalc_heatmap(store: Store) -> list[list[float]]:
    grid = store.walkable_grid()
    w, h = store.grid_size

    access_points: set[Position] = set()
    for entrance in store.entrances:
        for pos in entrance.occupied_positions:
            access_points.add(pos)
    for ex in store.exits:
        for pos in ex.occupied_positions:
            access_points.add(pos)
    for f in store.product_racks:
        access_points |= f.access_tiles(store.grid_size)
    for counter in store.counters:
        access_points |= counter.service_access_tiles(store.grid_size)

    points = [p for p in access_points if grid[p[1]][p[0]]]

    counts = [[0] * w for _ in range(h)]
    pf = AStarPathFinder()
    for i, src in enumerate(points):
        for dst in points[i + 1:]:
            for x, y in pf.find_path(grid, src, dst):
                counts[y][x] += 1

    max_count = max((counts[y][x] for y in range(h) for x in range(w)), default=1) or 1
    return [[counts[y][x] / max_count for x in range(w)] for y in range(h)]
