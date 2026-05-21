from store_emulator.domain.types import Face
from store_emulator.engine.routing.store_lookup import find_racks_by_sku, resolve_buy_placement


def test_accepts_face_at_matches_face_for_shared_access_tile(collision_store):
    rack_a = next(r for r in collision_store.racks if r.id == "A")
    rack_b = next(r for r in collision_store.racks if r.id == "B")
    grid = collision_store.grid_size

    assert rack_a.accepts_face_at((1, 0), Face.E, grid) is True
    assert rack_a.accepts_face_at((1, 0), Face.W, grid) is False
    assert rack_b.accepts_face_at((1, 0), Face.W, grid) is True
    assert rack_b.accepts_face_at((1, 0), Face.E, grid) is False


def test_accepts_face_at_returns_false_for_non_access_tile(collision_store):
    rack_a = next(r for r in collision_store.racks if r.id == "A")
    grid = collision_store.grid_size
    # (3, 2) is a plain floor tile — far from rack A on every face.
    assert rack_a.accepts_face_at((3, 2), Face.E, grid) is False


def test_find_racks_by_sku_returns_all_placements(multi_placement_store):
    found = find_racks_by_sku(multi_placement_store, "sku-x")
    ids = sorted(rack.id for rack, _ in found)
    assert ids == ["P", "Q"]


def test_find_racks_by_sku_returns_empty_for_unknown(collision_store):
    assert find_racks_by_sku(collision_store, "missing") == []


def test_resolve_buy_placement_picks_stance_match(multi_placement_store):
    # Customer at the shared access tile facing W → only Q accepts (1, 0) on W.
    placement = resolve_buy_placement(
        multi_placement_store, target=(1, 0), face=Face.W, sku="sku-x"
    )
    assert placement is not None
    rack, _slot = placement
    assert rack.id == "Q"

    # Same tile, face E → only P accepts (1, 0) on E.
    placement = resolve_buy_placement(
        multi_placement_store, target=(1, 0), face=Face.E, sku="sku-x"
    )
    assert placement is not None
    assert placement[0].id == "P"


def test_resolve_buy_placement_falls_back_to_first_when_stance_does_not_narrow(multi_placement_store):
    # face=None and target is a shared tile → both P and Q accept; first wins.
    placement = resolve_buy_placement(
        multi_placement_store, target=(1, 0), face=None, sku="sku-x"
    )
    assert placement is not None
    assert placement[0].id == "P"


def test_resolve_buy_placement_uses_target_only_when_face_wrong(multi_placement_store):
    # target=(3, 0) is in Q's access tiles only (P doesn't reach (3, 0)).
    # The customer's face N matches neither P nor Q at (3, 0) (both N candidates
    # land on y=-1 / out-of-bounds). Without the target-only fallback the
    # resolver would default to candidates[0]=P. With it we correctly land on Q.
    placement = resolve_buy_placement(
        multi_placement_store, target=(3, 0), face=Face.N, sku="sku-x"
    )
    assert placement is not None
    assert placement[0].id == "Q"


def test_resolve_buy_placement_falls_back_to_any_sku_holder_when_stance_unreachable(multi_placement_store):
    # Target tile is nowhere near either rack's access tiles. SKU resolution
    # is still better than nothing → return first SKU holder.
    placement = resolve_buy_placement(
        multi_placement_store, target=(4, 2), face=Face.N, sku="sku-x"
    )
    assert placement is not None
    assert placement[0].id == "P"


def test_resolve_buy_placement_returns_none_for_unknown_sku(collision_store):
    assert resolve_buy_placement(
        collision_store, target=(1, 0), face=Face.W, sku="missing"
    ) is None


from store_emulator.engine.routing.store_lookup import rack_id_at


def test_rack_id_at_first_match_when_face_not_given(collision_store):
    # Preserves current behavior — A comes first in store.racks.
    assert rack_id_at(collision_store, (1, 0)) == "A"


def test_rack_id_at_disambiguates_by_face(collision_store):
    assert rack_id_at(collision_store, (1, 0), face=Face.W) == "B"
    assert rack_id_at(collision_store, (1, 0), face=Face.E) == "A"


def test_rack_id_at_falls_back_when_face_matches_no_candidate(collision_store):
    # N matches neither rack at (1, 0). Caller still gets a non-empty answer.
    assert rack_id_at(collision_store, (1, 0), face=Face.N) == "A"


def test_rack_id_at_returns_empty_when_no_rack_owns_tile(collision_store):
    # (1, 1) is a plain floor tile — no rack body and no rack's access tile
    # touches it. With face supplied or not, the lookup must return "".
    assert rack_id_at(collision_store, (1, 1)) == ""
    assert rack_id_at(collision_store, (1, 1), face=Face.S) == ""


def test_rack_id_at_returns_body_rack_when_target_is_occupied(collision_store):
    # Rack A occupies (0, 0). Body check wins regardless of face.
    assert rack_id_at(collision_store, (0, 0)) == "A"
    assert rack_id_at(collision_store, (0, 0), face=Face.W) == "A"
