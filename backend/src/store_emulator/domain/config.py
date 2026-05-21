from enum import StrEnum

from pydantic import BaseModel

from .rack import RackType


class EngineType(StrEnum):
    PATTERN_INTENT_IMPULSE = "pattern_intent_impulse"


class LLMConfig(BaseModel):
    model: str = "gemini/gemini-3.1-pro-preview"
    temperature: float = 1.0
    max_tokens: int = 65535


class DwellRange(BaseModel):
    min: int
    max: int


_DWELL_DEFAULTS: dict[RackType, DwellRange] = {
    RackType.SHELF:   DwellRange(min=2,  max=10),
    RackType.FRIDGE:  DwellRange(min=2,  max=8),
    RackType.COUNTER: DwellRange(min=5,  max=30),
}


class PatternIntentImpulseConfig(BaseModel):
    llm: LLMConfig | None = None  # None falls back to SimulationConfig.llm


class EngineConfigs(BaseModel):
    pattern_intent_impulse: PatternIntentImpulseConfig = PatternIntentImpulseConfig()


class SimulationConfig(BaseModel):
    block_move_sec: int = 1
    max_grid_size: int = 30
    dwell: dict[RackType, DwellRange] = dict(_DWELL_DEFAULTS)
    engine_type: EngineType = EngineType.PATTERN_INTENT_IMPULSE
    llm: LLMConfig = LLMConfig()
    engines: EngineConfigs = EngineConfigs()

    def dwell_for(self, rack_type: RackType) -> DwellRange:
        return self.dwell.get(rack_type, DwellRange(min=5, max=30))

    def llm_for(self, engine_type: EngineType) -> LLMConfig:
        if engine_type == EngineType.PATTERN_INTENT_IMPULSE:
            return self.engines.pattern_intent_impulse.llm or self.llm
        return self.llm
