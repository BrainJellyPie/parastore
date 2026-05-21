import random

from pydantic import BaseModel

from store_emulator.domain.persona import Persona
from store_emulator.domain.types import Weekday


class CustomerEntry(BaseModel):
    persona_id: str
    day: Weekday
    arrival_time: str  # "HH:MM:SS"
    hour: int


def generate_customers(personas: list[Persona], seed: int | None = None) -> list[CustomerEntry]:
    if seed is not None:
        random.seed(seed)

    entries: list[CustomerEntry] = []
    for persona in personas:
        hour = persona.arrival_hour
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        entries.append(CustomerEntry(
            persona_id=persona.id,
            day=persona.day,
            arrival_time=f"{hour:02d}:{minute:02d}:{second:02d}",
            hour=hour,
        ))

    entries.sort(key=lambda e: (e.day, e.arrival_time))
    return entries
