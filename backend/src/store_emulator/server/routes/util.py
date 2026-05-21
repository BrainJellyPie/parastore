from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from store_emulator.domain.store import Store
from store_emulator.engine.validation import list_blocked_faces
from store_emulator.server.schemas import BlockedSlotFaceInfo

router = APIRouter(prefix="/api/util", tags=["util"])


class BlockedFacesRequest(BaseModel):
    store: Store


@router.post("/blocked-faces", summary="Compute unreachable faces (stateless)")
async def compute_blocked_faces(req: BlockedFacesRequest) -> list[BlockedSlotFaceInfo]:
    """Compute the unreachable (rack_id, block, face) list from the supplied store JSON.

    Use this for stores not yet persisted to a setup (in-editor state, pre-validation, etc.).
    Same rules as `GET /api/projects/{pid}/setups/{sid}/slots/blocked`, but exposed without requiring a setup.

    **Errors:** 400 (no entrances — reachability cannot be computed).
    **Response:** `BlockedSlotFaceInfo[]` — each item `{rack_id, block, face, reason: "blocked"}`.
    """
    if not req.store.entrances:
        raise HTTPException(400, "cannot compute reachability without an entrance.")
    return [BlockedSlotFaceInfo.from_detail(d) for d in list_blocked_faces(req.store)]
