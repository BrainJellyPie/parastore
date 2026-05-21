from pydantic import BaseModel

from store_emulator.domain.types import TokenUsage


class SimulationSummary(BaseModel):
    store_id: str
    currency: str = "USD_CENTS"
    total_customers: int = 0
    total_revenue: int = 0  # unit: US cents
    top_products: list[str] = []
    by_purpose: dict[str, int] = {}
    by_identity: dict[str, int] = {}
    by_age: dict[str, int] = {}
    by_gender: dict[str, int] = {}


class AggregatedResult(BaseModel):
    summary: SimulationSummary
    pathcalc_heatmap: list[list[float]]
    persona_heatmap: list[list[int]]
    token_usage: TokenUsage = TokenUsage()
