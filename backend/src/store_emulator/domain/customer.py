from pydantic import BaseModel

from .types import Action, Face, Weekday


class TimelineEvent(BaseModel):
    elapsed_sec: int
    x: int
    y: int
    action: Action
    duration: int = 0
    target_rack: str = ""
    face: Face | None = None
    description: str = ""
    product_sku: str = ""
    product_name: str = ""
    price: int = 0  # unit: US cents


class CustomerResult(BaseModel):
    persona_id: str
    day: Weekday
    arrival_time: str  # "HH:MM:SS"
    leave_time: str = ""
    timeline: list[TimelineEvent] = []
    total_spent: int = 0  # unit: US cents
    engine_type: str = ""

    @property
    def purchases(self) -> list[TimelineEvent]:
        return [e for e in self.timeline if e.action == Action.BUY]
