from store_emulator.domain.config import SimulationConfig
from store_emulator.domain.runner import SimulationRunner

from store_emulator.application.presets.behavior import BEHAVIOR_PATTERNS, sample_cue
from store_emulator.engine.llm_client import LiteLLMClient
from store_emulator.engine.routing.pathfinder import AStarPathFinder
from store_emulator.engine.simulation.engines import ENGINES
from store_emulator.engine.simulation.factory import build_engine
from store_emulator.engine.simulation.simulator import PerCustomerSimulationRunner


def build_runner(config: SimulationConfig) -> SimulationRunner:
    pathfinder = AStarPathFinder()

    if config.engine_type not in ENGINES:
        raise ValueError(f"unsupported engine type: {config.engine_type}")

    needs_llm = ENGINES[config.engine_type][2]
    llm = LiteLLMClient(config.llm_for(config.engine_type)) if needs_llm else None
    engine = build_engine(config, llm=llm, pathfinder=pathfinder)
    return PerCustomerSimulationRunner(config, engine, pathfinder, sample_cue, BEHAVIOR_PATTERNS)
