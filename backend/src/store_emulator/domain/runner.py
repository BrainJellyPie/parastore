"""Simulation runner interface. Output contract is identical across engine paradigms (per-customer / aggregate)."""

from typing import Protocol

from .customer import CustomerResult
from .persona import Persona
from .result import AggregatedResult
from .store import Store


class SimulationRunner(Protocol):
    async def run(
        self,
        store: Store,
        personas: list[Persona],
        *,
        max_concurrent: int = 5,
        address: str = "",
        customer_profile: str = "",
    ) -> tuple[AggregatedResult, list[CustomerResult]]: ...

    def get_engine_metadata(self) -> dict[str, object]:
        ...
