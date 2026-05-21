from typing import Protocol

from pydantic import BaseModel

from .action import CustomerAction
from .behavior import BehaviorCue, BehaviorPattern
from .persona import Persona
from .store import Store
from .types import TokenUsage, Weekday


class PerCustomerContext(BaseModel):
    store: Store
    persona: Persona
    day: Weekday
    arrival_hour: int
    concurrent_visitors_in_hour: int
    cue: BehaviorCue
    behavior_patterns: list[BehaviorPattern]
    address: str = ""
    customer_profile: str = ""


class EngineDecision(BaseModel):
    actions: list[CustomerAction]
    engine_type: str
    trace: dict[str, object] = {}


class CustomerBehaviorEngine(Protocol):
    engine_type: str

    async def decide_actions(
        self,
        context: PerCustomerContext,
    ) -> EngineDecision: ...

    def reset_usage(self) -> None: ...
    def get_usage(self) -> TokenUsage: ...
