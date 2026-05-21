import logging

from store_emulator.domain.customer import CustomerResult
from store_emulator.domain.engine import EngineDecision
from store_emulator.domain.store import Store
from store_emulator.domain.types import PathFinder, Weekday

from ..routing.route_builder import build_journey
from ..routing.timeline_builder import build_timeline

logger = logging.getLogger(__name__)


def execute_decision(
    store: Store,
    persona_id: str,
    day: Weekday,
    arrival_time: str,
    decision: EngineDecision,
    pathfinder: PathFinder,
    block_move_sec: int,
) -> CustomerResult:
    journey = build_journey(store, decision.actions, pathfinder, block_move_sec)
    result = build_timeline(
        persona_id, day, arrival_time,
        journey, store, block_move_sec=block_move_sec,
    )
    result.engine_type = decision.engine_type
    return result
