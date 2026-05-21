from typing import Any

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from store_emulator.application import simulation as sim_service
from store_emulator.application.async_executor import executor
from store_emulator.application.errors import AppError
from store_emulator.domain.persona import Persona
from store_emulator.server.schemas import SimulationStartResponse
from ..deps import get_config

router = APIRouter(prefix="/api/projects", tags=["simulate"])


class SimulateRequest(BaseModel):
    """Simulation run request. Executed against the server-stored setup."""
    setup_id: str = Field(description="Setup ID")
    run_id: str | None = Field(default=None, description="run ID (auto-generated if omitted)")


@router.get("/{pid}/runs", summary="Simulation run history")
async def list_runs(
    pid: str,
    setup_id: str | None = Query(default=None, description="filter by setup"),
) -> list[dict[str, Any]]:
    """List simulation runs for the project.

    **Filter:** `?setup_id=xxx` to scope to a single setup.
    **Sort:** `created_at` descending.
    **Response fields:** `run_id`, `status`, `setup_id`, `created_at`, `summary` (when completed)."""
    return sim_service.list_runs(pid, setup_id)


@router.post("/{pid}/runs", summary="Start simulation", response_model=SimulationStartResponse)
async def start_simulation(pid: str, req: SimulateRequest) -> SimulationStartResponse:
    """Run a simulation asynchronously. Returns immediately; work runs in the background.

    **Engine:** runs on the `pattern_intent_impulse` engine.

    **Preconditions (setup readiness must pass):**
    - `setup.store` exists
    - At least one product is placed in slots (registered via `PUT /setups/{sid}/slots`)
    - At least one project persona exists
    - No layout/persona generation is in progress

    **Setup lock:** the same setup cannot run concurrently. A running setup is in `running` state.
    **On completion:** the setup transitions to `locked` and `runId` is recorded.
    **On failure:** the setup reverts to `draft`.

    **Errors:** 400 (no layout / no personas), 404 (setup not found), 409 (locked / running / readiness not met / duplicate run_id)"""
    try:
        run_id, store, personas, address, customer_profile = sim_service.prepare_simulation(
            pid, req.setup_id, req.run_id,
        )
    except AppError as e:
        raise HTTPException(e.status_code, str(e))

    config = get_config()
    executor.submit(
        sim_service.run_simulation_background,
        pid, run_id, req.setup_id, store, personas,
        config, address, customer_profile,
    )

    return SimulationStartResponse(project_id=pid, run_id=run_id, setup_id=req.setup_id)


@router.get("/{pid}/runs/{run_id}/status", summary="Get simulation status")
async def get_status(pid: str, run_id: str) -> dict[str, Any]:
    """Poll simulation progress.

    **Common response:** `{ status, error, created_at, setup_id, total_customers }`.
    **status values:** `"pending"` → `"running"` → `"completed"` | `"failed"`.
    When `failed`, `error` carries the exception message.
    """
    try:
        return sim_service.get_run_status(pid, run_id)
    except FileNotFoundError:
        raise HTTPException(404, "run result not found")


@router.get("/{pid}/runs/{run_id}/summary", summary="Simulation summary + personas")
async def get_summary(pid: str, run_id: str) -> dict[str, Any]:
    """Aggregated simulation result and the personas used.

    **Response:** `{ summary: SimulationSummary, personas: { id: Persona } }`.
    **Note:** `personas` is a `persona_id → Persona` map, not an array.
    **summary fields:** total_customers, total_revenue, top_products, by_purpose/identity/age/gender.
    `by_*` distributions depend on persona attributes — some engines may leave them empty or weakly meaningful."""
    try:
        return {
            "summary": sim_service.get_run_output(pid, run_id, "summary.json"),
            "personas": sim_service.get_run_output(pid, run_id, "personas.json"),
        }
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/{pid}/runs/{run_id}/heatmap", summary="Heatmap data")
async def get_heatmap(pid: str, run_id: str) -> dict[str, Any]:
    """Customer-flow heatmaps.

    **Response:**
    - `pathcalc_heatmap`: float[][] — per-cell movement frequency
    - `persona_heatmap`: int[][] — per-cell unique customer count
    - size = grid_size [height][width]"""
    try:
        return {
            "pathcalc_heatmap": sim_service.get_run_output(pid, run_id, "pathcalc_heatmap.json"),
            "persona_heatmap": sim_service.get_run_output(pid, run_id, "persona_heatmap.json"),
        }
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/{pid}/runs/{run_id}/timeline", summary="Per-customer timeline")
async def get_timeline(pid: str, run_id: str) -> Any:
    """Behavior timeline for every customer.

    **Response:** `CustomerResult[]` — chronologically ordered events per customer. The `engine_type` field identifies which engine produced the result.
    Each event: elapsed_sec, x, y, action (enter/move/browse/buy/pay/exit), duration, product_sku, etc.
    **If the file has not been generated yet, returns an empty array** (not 404)."""
    try:
        return sim_service.get_run_output(pid, run_id, "timeline.json")
    except FileNotFoundError:
        return []


@router.get("/{pid}/runs/{run_id}/store", summary="Store at simulation time")
async def get_run_store(pid: str, run_id: str) -> dict[str, Any]:
    """Store layout (Store object) at the time of the simulation run."""
    try:
        return sim_service.get_run_input(pid, run_id, "store.json")
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))


@router.get("/{pid}/runs/{run_id}/personas", summary="Simulation personas",
            response_model=dict[str, Persona])
async def get_run_personas(pid: str, run_id: str) -> dict[str, Persona]:
    """Personas used in the simulation. **`persona_id → Persona` map** (not an array).

    Returns `output/personas.json` as-is. Shape differs from `input/personas.json` (which is an array).
    """
    try:
        raw = sim_service.get_run_output(pid, run_id, "personas.json")
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {pid_: Persona.model_validate(p) for pid_, p in raw.items()}


