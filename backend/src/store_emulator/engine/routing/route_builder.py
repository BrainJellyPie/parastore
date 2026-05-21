from pydantic import BaseModel

from store_emulator.domain.action import CustomerAction
from store_emulator.domain.rack import Rack, RackType, Slot
from store_emulator.domain.types import Action, CARDINAL_DIRECTIONS, Face, PathFinder, Position
from store_emulator.domain.store import Store
from .store_lookup import rack_id_at, resolve_buy_placement


class JourneyStep(BaseModel):
    action: CustomerAction
    path: list[Position] = []


def build_journey(
    store: Store,
    actions: list[CustomerAction],
    pathfinder: PathFinder,
    block_move_sec: int = 1,
) -> list[JourneyStep]:
    grid = store.walkable_grid()
    w, h = store.grid_size
    current = entrance_position(store)
    journey: list[JourneyStep] = []

    for raw_action in actions:
        action = _sanitize_action(raw_action, grid, w, h, store)
        path = _calculate_path(store, grid, pathfinder, current, action, block_move_sec)
        journey.append(JourneyStep(action=action, path=path))
        if path:
            current = path[-1]

    return journey


def integrate_actions(
    store: Store,
    intent_actions: list[CustomerAction],
    impulse_actions: list[CustomerAction],
) -> list[CustomerAction]:
    """Merge intent + impulse actions and order visits via greedy nearest-neighbor.

    Manhattan distance ordering. BUY is only eligible after a BROWSE on the same rack.
    """
    enter: CustomerAction | None = None
    exit_action: CustomerAction | None = None
    pay: CustomerAction | None = None
    middle: list[CustomerAction] = []

    for a in intent_actions:
        if a.nav == "leave":
            exit_action = a
        elif a.action == Action.PAY:
            pay = a
        elif a.action == Action.ENTER:
            enter = a
        else:
            middle.append(a)

    middle.extend(impulse_actions)

    if not middle:
        result: list[CustomerAction] = []
        if enter:
            result.append(enter)
        if pay:
            result.append(pay)
        if exit_action:
            result.append(exit_action)
        return result

    current = entrance_position(store)
    ordered: list[CustomerAction] = []
    remaining = list(middle)
    browsed_racks: set[str] = set()

    while remaining:
        best_idx = -1
        best_dist = 9999

        for i, a in enumerate(remaining):
            # Precedence: BUY is eligible only after BROWSE on the same rack is complete.
            if a.action == Action.BUY and _has_pending_browse(a, remaining, browsed_racks, store):
                continue
            dist = _manhattan(current, _action_position(a, store))
            if dist < best_dist:
                best_dist = dist
                best_idx = i

        if best_idx == -1:
            # All remaining actions are blocked — force the first to break the deadlock.
            best_idx = 0

        picked = remaining.pop(best_idx)
        ordered.append(picked)
        current = _action_position(picked, store)

        if picked.action == Action.BROWSE and picked.target is not None:
            rack_id = rack_id_at(store, picked.target, picked.face)
            if rack_id:
                browsed_racks.add(rack_id)

    result: list[CustomerAction] = []
    if enter:
        result.append(enter)
    result.extend(ordered)
    if pay:
        result.append(pay)
    if exit_action:
        result.append(exit_action)
    return result


def find_exposed_products(
    store: Store,
    journey: list[JourneyStep],
) -> list[tuple[Rack, Slot, str]]:
    path_tiles: set[Position] = set()
    for step in journey:
        for pos in step.path:
            path_tiles.add(pos)

    exposed: list[tuple[Rack, Slot, str]] = []
    seen_skus: set[str] = set()
    for f in store.product_racks:
        if not f.access_tiles(store.grid_size) & path_tiles:
            continue
        for slot in f.slots:
            for item in slot.items:
                if item.sku in seen_skus:
                    continue
                exposed.append((f, slot, item.sku))
                seen_skus.add(item.sku)
    return exposed


def _manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _has_pending_browse(
    buy_action: CustomerAction,
    remaining: list[CustomerAction],
    browsed_racks: set[str],
    store: Store,
) -> bool:
    """True if a BROWSE for the BUY's rack is still pending in remaining."""
    if buy_action.target is None:
        return False
    rack_id = ""
    if buy_action.product_sku:
        placement = resolve_buy_placement(
            store,
            target=buy_action.target,
            face=buy_action.face,
            sku=buy_action.product_sku,
        )
        if placement is not None:
            rack_id = placement[0].id
    if not rack_id:
        rack_id = rack_id_at(store, buy_action.target, buy_action.face)
    if not rack_id or rack_id in browsed_racks:
        return False
    return any(
        a.action == Action.BROWSE
        and a.target is not None
        and rack_id_at(store, a.target, a.face) == rack_id
        for a in remaining
    )


def _action_position(action: CustomerAction, store: Store) -> Position:
    """Resolve an action's destination tile. wander → area center; leave → exit."""
    if action.target:
        return action.target
    if action.nav == "area" and action.area:
        x1, y1, x2, y2 = action.area
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    if action.nav == "leave":
        return _exit_position(store)
    return entrance_position(store)


def _sanitize_action(
    action: CustomerAction,
    grid: list[list[bool]],
    w: int,
    h: int,
    store: Store,
) -> CustomerAction:
    """Snap action.target to a walkable tile; prefer the rack's access_tile when target sits on a rack."""
    if action.target is None:
        return action
    tx, ty = action.target
    cx = max(0, min(tx, w - 1))
    cy = max(0, min(ty, h - 1))

    # PAY: snap into a counter's service_access_tiles.
    if action.action == Action.PAY:
        for counter in store.counters:
            service = [t for t in counter.service_access_tiles(store.grid_size) if grid[t[1]][t[0]]]
            if service:
                if (cx, cy) in service:
                    return action if (cx, cy) == action.target else action.model_copy(update={"target": (cx, cy)})
                return action.model_copy(update={"target": service[0]})

    # BUY: re-anchor target + face against the SKU's actual placement so the
    # persona walks to the face that actually carries the product. Skips when
    # the SKU is empty or resolves to nothing — falls through to generic logic.
    if action.action == Action.BUY and action.product_sku:
        placement = resolve_buy_placement(
            store, target=action.target, face=action.face, sku=action.product_sku,
        )
        if placement is not None:
            rack, slot = placement
            snapped = _face_access_tile(rack, slot.face, store.grid_size, grid)
            if snapped is not None:
                updates: dict[str, object] = {"target": snapped}
                if action.face != slot.face:
                    updates["face"] = slot.face
                return action.model_copy(update=updates)

    if grid[cy][cx]:
        if (cx, cy) == action.target:
            return action
        return action.model_copy(update={"target": (cx, cy)})
    for rack in store.racks:
        if (cx, cy) in set(rack.occupied_positions):
            access = [t for t in rack.access_tiles(store.grid_size) if grid[t[1]][t[0]]]
            if access:
                return action.model_copy(update={"target": access[0]})
            break
    clamped = _clamp_to_walkable(action.target, grid, w, h)
    if clamped == action.target:
        return action
    return action.model_copy(update={"target": clamped})


def _calculate_path(
    store: Store,
    grid: list[list[bool]],
    pathfinder: PathFinder,
    current: Position,
    action: CustomerAction,
    block_move_sec: int = 1,
) -> list[Position]:
    if action.nav == "leave":
        return pathfinder.find_path(grid, current, _exit_position(store))
    if action.nav == "area" and action.area:
        return _wander_path(store, grid, pathfinder, current, action.area, action.dwell, block_move_sec)
    if action.nav == "path" and action.target:
        return pathfinder.find_path(grid, current, action.target)
    return []


def _face_access_tile(
    rack: Rack, face: Face, grid_size: tuple[int, int], grid: list[list[bool]],
) -> Position | None:
    """First walkable access tile of `rack` on `face`, or None when unavailable."""
    for tile in rack.access_tiles(grid_size):
        if rack.accepts_face_at(tile, face, grid_size) and grid[tile[1]][tile[0]]:
            return tile
    return None


def _clamp_to_walkable(pos: Position, grid: list[list[bool]], w: int, h: int) -> Position:
    x = max(0, min(pos[0], w - 1))
    y = max(0, min(pos[1], h - 1))
    if grid[y][x]:
        return (x, y)
    for dx, dy in CARDINAL_DIRECTIONS:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and grid[ny][nx]:
            return (nx, ny)
    return (x, y)


def entrance_position(store: Store) -> Position:
    if store.entrances and store.entrances[0].occupied_positions:
        return store.entrances[0].occupied_positions[0]
    return (0, 0)


def _exit_position(store: Store) -> Position:
    if store.exits and store.exits[0].occupied_positions:
        return store.exits[0].occupied_positions[0]
    return entrance_position(store)


def _wander_path(
    store: Store,
    grid: list[list[bool]],
    pathfinder: PathFinder,
    start: Position,
    area: tuple[int, int, int, int],
    dwell: int,
    block_move_sec: int = 1,
) -> list[Position]:
    """Build a wander path visiting rack access tiles inside `area` as waypoints.

    Generates a generous path, then trims it via a dwell-budget simulation to the
    estimated reach. Precise time accounting (pause insertion) belongs to timeline_builder.
    """
    waypoints = _collect_waypoints(store, grid, area)
    if not waypoints:
        return [start]

    generous_limit = max(8, dwell // max(1, block_move_sec) * 2)
    ordered = _order_nearest(start, waypoints)

    path: list[Position] = [start]
    current = start
    for wp in ordered:
        segment = pathfinder.find_path(grid, current, wp)
        if len(segment) < 2:
            continue
        path.extend(segment[1:])
        current = wp
        if len(path) >= generous_limit:
            break

    skip_types = {RackType.ENTRANCE, RackType.EXIT}
    rack_access: set[Position] = set()
    for rack in store.racks:
        if rack.type not in skip_types:
            rack_access |= rack.access_tiles(store.grid_size)

    budget = dwell
    _PAUSE_ESTIMATE = 2  # Conservative estimate of timeline_builder pause duration (actual: 2–4s).
    for i, pos in enumerate(path[1:], 1):
        budget -= block_move_sec
        if pos in rack_access:
            budget -= _PAUSE_ESTIMATE
        if budget <= 0:
            return path[:i + 1]

    return path


def _collect_waypoints(
    store: Store,
    grid: list[list[bool]],
    area: tuple[int, int, int, int],
) -> list[Position]:
    """Collect rack access tiles inside area; backfill from walkable tiles if too few."""
    x1, y1, x2, y2 = area
    skip_types = {RackType.ENTRANCE, RackType.EXIT}

    access_tiles: list[Position] = []
    for rack in store.racks:
        if rack.type in skip_types:
            continue
        for tile in rack.access_tiles(store.grid_size):
            if x1 <= tile[0] <= x2 and y1 <= tile[1] <= y2 and grid[tile[1]][tile[0]]:
                access_tiles.append(tile)
                break  # One tile per rack.

    if len(access_tiles) >= 2:
        return access_tiles

    walkable: list[Position] = []
    height = len(grid)
    width = len(grid[0]) if height > 0 else 0
    for y in range(max(0, y1), min(height, y2 + 1)):
        for x in range(max(0, x1), min(width, x2 + 1)):
            if grid[y][x]:
                walkable.append((x, y))

    if not walkable:
        return access_tiles

    count = min(5, len(walkable))
    step = max(1, len(walkable) // count)
    sampled = [walkable[i * step] for i in range(count)]
    return access_tiles + [t for t in sampled if t not in set(access_tiles)]


def _order_nearest(start: Position, points: list[Position]) -> list[Position]:
    remaining = list(points)
    ordered: list[Position] = []
    current = start
    while remaining:
        best_idx = min(range(len(remaining)), key=lambda i: _manhattan(current, remaining[i]))
        picked = remaining.pop(best_idx)
        ordered.append(picked)
        current = picked
    return ordered
