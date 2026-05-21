import asyncio
import logging
import traceback
import uuid
from pathlib import Path
from typing import Any, cast

from store_emulator.domain.config import SimulationConfig
from store_emulator.domain.customer import CustomerResult
from store_emulator.domain.persona import Persona
from store_emulator.domain.result import AggregatedResult
from store_emulator.domain.runner import SimulationRunner
from store_emulator.domain.store import Store
from store_emulator.application.presets.behavior import BEHAVIOR_PATTERNS
from store_emulator.application.runner import build_runner
from store_emulator.application.storage.io import DATA_DIR, read_json, write_json, now_iso
from store_emulator.application.storage.setups import (
    read_setup, write_setup, personas_path, metadata_path,
)
from store_emulator.application.storage.runs import save_run

from store_emulator.application.errors import AppError

logger = logging.getLogger(__name__)


async def run_simulation(
    config: SimulationConfig,
    store: Store,
    personas: list[Persona],
    max_concurrent: int = 20,
    address: str = "",
    customer_profile: str = "",
) -> tuple[AggregatedResult, list[CustomerResult], SimulationRunner]:
    """Run a simulation and return (aggregated, per-customer results, runner).

    Caller uses the runner to extract engine-specific metadata via
    ``get_engine_metadata()``.
    """
    runner = build_runner(config)
    aggregated, customers = await runner.run(
        store, personas,
        max_concurrent=max_concurrent,
        address=address, customer_profile=customer_profile,
    )
    return aggregated, customers, runner


def prepare_simulation(
    pid: str, setup_id: str, run_id: str | None = None,
) -> tuple[str, Store, list[Persona], str, str]:
    """Validate, load inputs, and transition state before running. AppError on failure.

    Three-phase helper pipeline: _validate → _load_inputs → _mark_running.
    Returns (run_id, store, personas, address, customer_profile).
    """
    setup = _validate_simulation(pid, setup_id)
    rid, store, personas, address, customer_profile = _load_simulation_inputs(
        pid, setup, run_id,
    )
    _mark_simulation_running(pid, setup_id, rid)
    return rid, store, personas, address, customer_profile


def _validate_simulation(pid: str, setup_id: str) -> dict[str, Any]:
    """Single setup load + status/readiness check. Returns setup dict (with readiness)."""
    from store_emulator.application.setups import get_setup as _get_setup
    try:
        setup = _get_setup(pid, setup_id)
    except AppError:
        raise

    if setup["status"] == "locked":
        raise AppError("this setup is finalized. Branch it to run again.", 409)
    if setup["status"] == "running":
        raise AppError("this setup is already running.", 409)

    readiness = cast(dict[str, Any], setup.get("readiness") or {})
    if not readiness.get("ready", True):
        reasons = cast(list[str], readiness.get("reasons", []))
        raise AppError(f"cannot start simulation: {', '.join(reasons)}", 409)
    return setup


def _load_simulation_inputs(
    pid: str, setup: dict[str, Any], run_id: str | None,
) -> tuple[str, Store, list[Persona], str, str]:
    """Loads Store / Persona / metadata and pre-checks run_id collision."""
    if not setup.get("store"):
        raise AppError("no store layout.")
    store = Store.model_validate(setup["store"])

    p_path = personas_path(pid)
    if not p_path.exists():
        raise AppError("no personas.")
    personas = [Persona.model_validate(p) for p in read_json(p_path)]
    if not personas:
        raise AppError("no personas.")

    rid = run_id or f"run_{uuid.uuid4().hex[:6]}"
    if _status_path(pid, rid).exists():
        raise AppError(f"run ID already exists: {rid}", 409)

    meta_file = metadata_path(pid)
    meta: dict[str, Any] = read_json(meta_file) if meta_file.exists() else {}
    address = str(meta.get("address", ""))
    customer_profile = str(meta.get("customer_profile", ""))
    return rid, store, personas, address, customer_profile


def _mark_simulation_running(pid: str, setup_id: str, run_id: str) -> None:
    """setup.status=running + run status=pending. Re-checks status/run_id at mark.

    A minimal CAS-style safeguard against load-vs-mark races — not fully atomic.
    recover_running_setups cleans residual running setups back to draft on restart.
    """
    fresh = read_setup(pid, setup_id)
    if fresh["status"] in ("running", "locked"):
        raise AppError("concurrent start detected: setup is already running or finalized.", 409)
    if _status_path(pid, run_id).exists():
        raise AppError(f"concurrent start detected: run ID already exists: {run_id}", 409)

    fresh["status"] = "running"
    write_setup(pid, setup_id, fresh)
    write_status(pid, run_id, "pending", setup_id=setup_id)


def _status_path(pid: str, run_id: str) -> Path:
    return Path(DATA_DIR) / pid / "runs" / run_id / "status.json"


def write_status(pid: str, run_id: str, status: str, error: str = "", **extra: object) -> None:
    path = _status_path(pid, run_id)
    existing: dict[str, object] = read_json(path) if path.exists() else {}
    data: dict[str, object] = {**existing, "status": status, "error": error, **extra}
    if "created_at" not in data:
        data["created_at"] = now_iso()
    write_json(path, data)


def run_simulation_background(
    pid: str, run_id: str, setup_id: str,
    store: Store, personas: list[Persona],
    config: SimulationConfig,
    address: str = "",
    customer_profile: str = "",
) -> None:
    try:
        write_status(pid, run_id, "running", total_customers=len(personas))
        aggregated, customers, runner = asyncio.run(
            run_simulation(config, store, personas,
                           address=address, customer_profile=customer_profile),
        )
        run_dir = save_run(
            DATA_DIR, pid, run_id,
            aggregated, customers, store, personas, config,
            BEHAVIOR_PATTERNS,
        )
        meta = runner.get_engine_metadata()
        if meta:
            write_json(run_dir / "output" / f"{config.engine_type}_meta.json", meta)
        write_status(pid, run_id, "completed")

        # Setup transitions to locked + runId. The run summary is the single
        # source of truth for KPIs.
        try:
            setup = read_setup(pid, setup_id)
            setup["status"] = "locked"
            setup["runId"] = run_id
            write_setup(pid, setup_id, setup)
        except Exception:
            pass  # Setup-file update failure must not lose the run data.

    except Exception as e:
        write_status(pid, run_id, "failed", f"{e}\n{traceback.format_exc()}")
        try:
            setup = read_setup(pid, setup_id)
            setup["status"] = "draft"
            write_setup(pid, setup_id, setup)
        except Exception:
            pass


def _run_base(pid: str, run_id: str) -> Path:
    return Path(DATA_DIR) / pid / "runs" / run_id


def get_run_output(pid: str, run_id: str, filename: str) -> Any:
    path = _run_base(pid, run_id) / "output" / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found")
    return read_json(path)


def get_run_input(pid: str, run_id: str, filename: str) -> Any:
    path = _run_base(pid, run_id) / "input" / filename
    if not path.exists():
        raise FileNotFoundError(f"{filename} not found")
    return read_json(path)


def get_run_status(pid: str, run_id: str) -> dict[str, Any]:
    path = _status_path(pid, run_id)
    if not path.exists():
        raise FileNotFoundError(f"Run not found: {run_id}")
    return read_json(path)


def list_runs(pid: str, setup_id: str | None = None) -> list[dict[str, Any]]:
    runs_dir = Path(DATA_DIR) / pid / "runs"
    if not runs_dir.exists():
        return []
    results: list[dict[str, Any]] = []
    for d in runs_dir.iterdir():
        if not d.is_dir():
            continue
        entry: dict[str, Any] = {"run_id": d.name}
        status_file = d / "status.json"
        if status_file.exists():
            entry.update(read_json(status_file))
        if setup_id and entry.get("setup_id") != setup_id:
            continue
        summary_file = d / "output" / "summary.json"
        if summary_file.exists():
            entry["summary"] = read_json(summary_file)
        results.append(entry)
    results.sort(key=lambda r: str(r.get("created_at", "")), reverse=True)
    return results
