from pathlib import Path

from store_emulator.domain.behavior import BehaviorPattern
from store_emulator.domain.config import SimulationConfig
from store_emulator.domain.customer import CustomerResult
from store_emulator.domain.persona import Persona
from store_emulator.domain.result import AggregatedResult
from store_emulator.domain.store import Store

from store_emulator.application.storage.io import write_json


def save_run(
    data_dir: str,
    project_id: str,
    run_id: str,
    result: AggregatedResult,
    customer_results: list[CustomerResult],
    store: Store,
    personas: list[Persona],
    config: SimulationConfig,
    patterns: list[BehaviorPattern] | None = None,
) -> Path:
    base = Path(data_dir) / project_id / "runs" / run_id
    _save_input(base, store, personas, config, patterns)
    _save_output(base, result, customer_results, personas)
    return base


def _save_input(
    base: Path,
    store: Store,
    personas: list[Persona],
    config: SimulationConfig,
    patterns: list[BehaviorPattern] | None,
) -> None:
    d = base / "input"
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "store.json", store.model_dump())
    write_json(d / "personas.json", [p.model_dump() for p in personas])
    write_json(d / "config.json", config.model_dump())
    if patterns:
        write_json(d / "behavior_patterns.json", [p.model_dump() for p in patterns])


def _save_output(
    base: Path,
    result: AggregatedResult,
    customer_results: list[CustomerResult],
    personas: list[Persona],
) -> None:
    d = base / "output"
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "summary.json", result.summary.model_dump())
    write_json(d / "pathcalc_heatmap.json", result.pathcalc_heatmap)
    write_json(d / "persona_heatmap.json", result.persona_heatmap)
    write_json(d / "timeline.json", [cr.model_dump() for cr in customer_results])
    write_json(d / "personas.json", {p.id: p.model_dump() for p in personas})
    write_json(d / "token_usage.json", result.token_usage.model_dump())
