from store_emulator.domain.rack import Rack, Slot
from store_emulator.domain.store import Store
from store_emulator.domain.types import Face, Position


def rack_id_at(store: Store, target: Position, face: Face | None = None) -> str:
    """Return the rack ID at `target`.

    Lookup order:
    1. If a rack body occupies the tile, return its id. This precedence is
       intentional: a target *inside* a rack body is unambiguous, regardless
       of any face the LLM may have supplied. BROWSE/BUY routes are
       sanitized to access tiles upstream, so this branch normally only fires
       on a few legitimate cases (e.g., PAY at the counter).
    2. Otherwise, look for racks whose access tiles include `target`.
       - If `face` is given and at least one candidate accepts the tile on
         that face, return the first such candidate.
       - Otherwise, return the first candidate (preserves prior behavior).
    3. Return "" if no rack owns the tile.
    """
    rack = store.rack_at(target[0], target[1])
    if rack:
        return rack.id
    candidates = [r for r in store.racks if target in r.access_tiles(store.grid_size)]
    if not candidates:
        return ""
    if face is not None:
        for r in candidates:
            if r.accepts_face_at(target, face, store.grid_size):
                return r.id
    return candidates[0].id


def find_racks_by_sku(store: Store, sku: str) -> list[tuple[Rack, Slot]]:
    """Return one (rack, slot) pair per rack that carries `sku`.

    SKU is a product ID — the same SKU may legitimately appear on multiple
    racks within one store (e.g., main shelf + promo endcap). We collapse
    multiple slots-on-the-same-rack to a single representative slot because
    `target_rack` attribution only needs the owning rack. Callers narrow
    further via target/face if needed.
    """
    found: list[tuple[Rack, Slot]] = []
    for rack in store.racks:
        for slot in rack.slots:
            if sku in {i.sku for i in slot.items}:
                found.append((rack, slot))
                break  # one representative slot per rack is enough
    return found


def resolve_buy_placement(
    store: Store,
    *,
    target: Position | None,
    face: Face | None,
    sku: str,
) -> tuple[Rack, Slot] | None:
    """Pick the (rack, slot) the customer reached for a BUY action.

    Three-stage resolution — each later stage is strictly weaker, so we keep
    the most precise match available without ever throwing away the SKU
    information:

    1. **target + face match**: rack accepts `target` as an access tile AND
       the LLM-supplied `face` lines up with the rack's face at that tile.
       This is the strongest signal.
    2. **target-only match**: the rack accepts `target` as an access tile,
       regardless of face. Used when `face` is None *or* when the LLM gave
       a face that doesn't match any candidate (e.g., a careless hallucination).
       Better than abandoning target information entirely.
    3. **first SKU placement**: no spatial match at all — fall back to the
       first rack carrying the SKU. Item-level attribution stays correct
       even if the exact rack is uncertain. See Risk Notes.

    Returns None only when no rack carries the SKU.
    """
    candidates = find_racks_by_sku(store, sku)
    if not candidates:
        return None
    if target is not None:
        grid = store.grid_size
        target_matches = [
            (rack, slot)
            for rack, slot in candidates
            if target in rack.access_tiles(grid)
        ]
        if face is not None:
            for rack, slot in target_matches:
                if rack.accepts_face_at(target, face, grid):
                    return (rack, slot)
        if target_matches:
            return target_matches[0]
    return candidates[0]
