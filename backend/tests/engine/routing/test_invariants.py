from store_emulator.domain.customer import CustomerResult, TimelineEvent
from store_emulator.domain.types import Action, Face, Weekday
from store_emulator.engine.routing.invariants import check_buy_consistency


def _result(events: list[TimelineEvent]) -> CustomerResult:
    return CustomerResult(
        persona_id="p1", day=Weekday.FRI, arrival_time="10:00:00", timeline=events,
    )


def _buy(*, target_rack: str, face: Face | None, sku: str, name: str = "B item", price: int = 200) -> TimelineEvent:
    return TimelineEvent(
        elapsed_sec=1, x=1, y=0, action=Action.BUY, target_rack=target_rack,
        face=face, product_sku=sku, product_name=name, price=price,
    )


def test_clean_run_reports_no_violations(collision_store):
    # sku-b lives on rack B's W face at price 200.
    results = [_result([_buy(target_rack="B", face=Face.W, sku="sku-b", name="B item", price=200)])]
    assert check_buy_consistency(collision_store, results) == []


def test_unknown_rack(collision_store):
    results = [_result([_buy(target_rack="ZZ", face=Face.W, sku="sku-b")])]
    v = check_buy_consistency(collision_store, results)
    assert [x.kind for x in v] == ["unknown_rack"]


def test_sku_not_in_store(collision_store):
    results = [_result([_buy(target_rack="B", face=Face.W, sku="sku-missing")])]
    v = check_buy_consistency(collision_store, results)
    assert [x.kind for x in v] == ["sku_not_in_store"]


def test_face_none(collision_store):
    results = [_result([_buy(target_rack="B", face=None, sku="sku-b")])]
    v = check_buy_consistency(collision_store, results)
    assert [x.kind for x in v] == ["face_none"]


def test_sku_not_on_face(collision_store):
    # sku-b exists on rack B but on face W; claim face E.
    results = [_result([_buy(target_rack="B", face=Face.E, sku="sku-b")])]
    v = check_buy_consistency(collision_store, results)
    assert [x.kind for x in v] == ["sku_not_on_face"]


def test_name_and_price_mismatch(collision_store):
    results = [_result([_buy(
        target_rack="B", face=Face.W, sku="sku-b",
        name="Wrong name", price=999,
    )])]
    v = check_buy_consistency(collision_store, results)
    assert sorted(x.kind for x in v) == ["name_mismatch", "price_mismatch"]


def test_multiple_personas_aggregate(collision_store):
    bad = _buy(target_rack="B", face=Face.E, sku="sku-b")
    good = _buy(target_rack="B", face=Face.W, sku="sku-b", name="B item", price=200)
    results = [
        CustomerResult(persona_id="p1", day=Weekday.FRI, arrival_time="10:00:00", timeline=[bad]),
        CustomerResult(persona_id="p2", day=Weekday.FRI, arrival_time="10:00:00", timeline=[good]),
    ]
    v = check_buy_consistency(collision_store, results)
    assert len(v) == 1
    assert v[0].persona_id == "p1"
    assert v[0].kind == "sku_not_on_face"
