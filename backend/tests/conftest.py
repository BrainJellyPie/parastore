import pytest

from store_emulator.domain.rack import Rack, RackType, Slot, SlotItem
from store_emulator.domain.store import Store
from store_emulator.domain.types import Face


@pytest.fixture
def collision_store() -> Store:
    """Two product racks sharing access tile (1, 0), plus a Counter sitting
    at the end of the aisle, plus a separate entrance and exit.

    In the domain model `ENTRANCE` and `EXIT` are independent `Rack` types
    in `PASSTHROUGH_TYPES`. Real stores can place them on separate tiles
    (separate doors) or stack them on the same tile (one doorway used for
    both flows). This fixture keeps them on separate tiles for clarity;
    overlap is allowed but not required.

    Layout (5x3 grid; "[X]" = rack body, "EN"/"EX" = entrance/exit,
    "." = floor):
        x:  0    1    2    3    4
        y0  [A]  .    [B]  .    [Co]
        y1  .    .    .    .    .
        y2  EN   .    .    .    EX

    Rack A at (0, 0), shelf, slot face E → access tile (1, 0).
    Rack B at (2, 0), shelf, slot face W → access tile (1, 0). Also access
                                            tiles (3, 0) [E] and (2, 1) [S].
    Counter at (4, 0), no slots → access tiles (4, 1) [S] and (3, 0) [W].
                                            id is literally "Counter" so
                                            the `!= "Counter"` regression
                                            assertion lands on a real string.
    Entrance at (0, 2), Exit at (4, 2): PASSTHROUGH, kept walkable.

    Order in `store.racks` is [A, B, Counter, entrance, exit], so
    coordinate-only first-match on (1, 0) returns A and on (4, 1) returns
    Counter (the only owner of that tile).
    """
    rack_a = Rack(
        id="A",
        type=RackType.SHELF,
        shape=[[1]],
        position=(0, 0),
        slots=[
            Slot(block=0, face=Face.E, level=1, items=[SlotItem(sku="sku-a", name="A item", price=100)]),
        ],
    )
    rack_b = Rack(
        id="B",
        type=RackType.SHELF,
        shape=[[1]],
        position=(2, 0),
        slots=[
            Slot(block=0, face=Face.W, level=1, items=[SlotItem(sku="sku-b", name="B item", price=200)]),
        ],
    )
    counter = Rack(
        id="Counter",
        type=RackType.COUNTER,
        shape=[[1]],
        position=(4, 0),
        slots=[],
    )
    entrance = Rack(
        id="entrance",
        type=RackType.ENTRANCE,
        shape=[[1]],
        position=(0, 2),
    )
    exit_rack = Rack(
        id="exit",
        type=RackType.EXIT,
        shape=[[1]],
        position=(4, 2),
    )
    return Store(
        id="store-collision",
        name="collision-test",
        type="convenience",
        grid_size=(5, 3),
        racks=[rack_a, rack_b, counter, entrance, exit_rack],
    )


@pytest.fixture
def multi_placement_store() -> Store:
    """`sku-x` lives on BOTH rack P and rack Q. Used to test that BUY
    resolution picks the rack the customer actually reached (via target+face).

    Tile (3, 0) is reachable from Q only, used by the target-only-narrowing
    test below.
    """
    rack_p = Rack(
        id="P",
        type=RackType.SHELF,
        shape=[[1]],
        position=(0, 0),
        slots=[
            Slot(block=0, face=Face.E, level=1, items=[SlotItem(sku="sku-x", name="X item", price=300)]),
        ],
    )
    rack_q = Rack(
        id="Q",
        type=RackType.SHELF,
        shape=[[1]],
        position=(2, 0),
        slots=[
            Slot(block=0, face=Face.W, level=1, items=[SlotItem(sku="sku-x", name="X item", price=300)]),
        ],
    )
    entrance = Rack(
        id="entrance",
        type=RackType.ENTRANCE,
        shape=[[1]],
        position=(0, 2),
    )
    exit_rack = Rack(
        id="exit",
        type=RackType.EXIT,
        shape=[[1]],
        position=(4, 2),
    )
    return Store(
        id="store-multi",
        name="multi-placement-test",
        type="convenience",
        grid_size=(5, 3),
        racks=[rack_p, rack_q, entrance, exit_rack],
    )
