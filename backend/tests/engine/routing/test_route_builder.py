from store_emulator.domain.action import CustomerAction
from store_emulator.domain.types import Action, Face
from store_emulator.engine.routing.route_builder import (
    _sanitize_action, integrate_actions,
)


def _sanitize(store, action):
    grid = store.walkable_grid()
    w, h = store.grid_size
    return _sanitize_action(action, grid, w, h, store)


def test_sanitize_buy_snaps_target_and_face_to_sku_placement(collision_store):
    # LLM-style mis-aligned action: target at rack A's east access tile (1, 0)
    # with face=W and sku=sku-b. sku-b actually lives on rack B's W face,
    # whose access tile is also (1, 0) — same coordinate, different rack/face.
    # Sanitize must snap to rack B's W-face access tile (1, 0) with face=W.
    misaligned = CustomerAction(
        nav="path", action=Action.BUY, target=(1, 0), face=Face.E,
        product_sku="sku-b", dwell=5,
    )
    out = _sanitize(collision_store, misaligned)
    # rack B's W-face access tile is (1, 0); confirmed by collision_store fixture.
    assert out.target == (1, 0)
    assert out.face == Face.W


def test_sanitize_buy_empty_sku_falls_through(collision_store):
    # No SKU — sanitize must not call resolve_buy_placement and must leave
    # target / face untouched (still walkable).
    action = CustomerAction(
        nav="path", action=Action.BUY, target=(1, 0), face=Face.E,
        product_sku="", dwell=5,
    )
    out = _sanitize(collision_store, action)
    assert out.target == (1, 0)
    assert out.face == Face.E


def test_integrate_actions_does_not_gate_buy_with_unrelated_browse(collision_store):
    """The decisive ordering test: pre-fix the BUY is incorrectly gated by
    an unrelated BROWSE; post-fix the BUY is free to fire first.

    Scenario:
    - BROWSE at (1, 0) face=E → post-fix rack A. Pre-fix rack_id_at((1, 0)) → A.
    - BUY at (1, 0) face=W, sku=sku-b → post-fix rack B (SKU override).
      Pre-fix rack_id_at((1, 0)) → A (no SKU override exists yet).
    - We feed BUY in `intent_actions` and BROWSE in `impulse_actions`, so
      `integrate_actions` builds middle = [BUY, BROWSE] (intent middles
      first). With ties broken by list order, whichever action is *eligible*
      first wins the iteration.

    Pre-fix behavior:
      `_has_pending_browse(BUY)` resolves BUY.rack via the coordinate-only
      `rack_id_at((1, 0))` → A. Pending BROWSE has rack=A too. Match →
      BUY is gated (skipped). BROWSE is picked first. Then BUY.
      Resulting middle order: [BROWSE, BUY].

    Post-fix behavior:
      `_has_pending_browse(BUY)` resolves BUY.rack via SKU → B. Pending
      BROWSE rack via face=E → A. No match → BUY is NOT gated. BUY is at
      index 0 in remaining, distance ties with BROWSE; iteration picks BUY
      first (strict `<` comparison keeps the earlier index).
      Resulting middle order: [BUY, BROWSE].

    The assertion catches the behavior change. Pre-fix this FAILS.
    """
    enter = CustomerAction(nav="path", action=Action.ENTER, target=(0, 2), dwell=0)
    exit_ = CustomerAction(nav="leave", dwell=0)
    buy = CustomerAction(
        nav="path", action=Action.BUY, target=(1, 0), face=Face.W,
        product_sku="sku-b", dwell=5,
    )
    browse = CustomerAction(
        nav="path", action=Action.BROWSE, target=(1, 0), face=Face.E, dwell=5,
    )

    ordered = integrate_actions(collision_store, [enter, buy, exit_], [browse])
    middle = [a for a in ordered if a.action in {Action.BROWSE, Action.BUY}]
    assert [a.action for a in middle] == [Action.BUY, Action.BROWSE]


def test_integrate_actions_still_orders_browse_before_buy_when_face_agrees(collision_store):
    """Sanity check for the matched-rack ordering. BROWSE and BUY both
    target rack B (BROWSE via face=W, BUY via sku-b). `_has_pending_browse`
    must still report a pending browse → BUY waits behind BROWSE.

    Passes both pre-fix and post-fix (regression guard for the
    matched-rack precondition itself, not for the bug fix). We feed BUY
    first into intent so that any future change that breaks the gating
    would surface as a flipped order here.
    """
    enter = CustomerAction(nav="path", action=Action.ENTER, target=(0, 2), dwell=0)
    exit_ = CustomerAction(nav="leave", dwell=0)
    buy = CustomerAction(
        nav="path", action=Action.BUY, target=(1, 0), face=Face.W,
        product_sku="sku-b", dwell=5,
    )
    browse = CustomerAction(
        nav="path", action=Action.BROWSE, target=(1, 0), face=Face.W, dwell=5,
    )

    ordered = integrate_actions(collision_store, [enter, buy, exit_], [browse])
    middle = [a for a in ordered if a.action in {Action.BROWSE, Action.BUY}]
    assert [a.action for a in middle] == [Action.BROWSE, Action.BUY]
