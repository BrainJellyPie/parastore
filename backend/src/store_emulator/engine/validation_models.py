from typing import Literal

from pydantic import BaseModel, Field

from store_emulator.domain.types import Face


type BlockReason = Literal["locked", "out_of_bounds", "occupied", "unreachable", "occluded"]


class BlockedFaceDetail(BaseModel):
    rack_id: str
    block: int
    face: Face
    reasons: list[BlockReason]


class ClearedSlot(BaseModel):
    rack_id: str
    block: int
    face: Face
    level: int
    cleared_skus: list[str]
    name: str
    reasons: list[BlockReason]

    @property
    def description(self) -> str:
        sku_str = ", ".join(self.cleared_skus) if self.cleared_skus else "(empty)"
        return f"{self.rack_id} block{self.block}/{self.face} L{self.level}: {self.name} ({sku_str})"


class Issue(BaseModel):
    """Single validation result. severity defaults to 'error' (rev 4 §4.1)."""
    code: str
    message: str
    severity: Literal["warning", "error"] = "error"
    details: dict[str, object] = Field(default_factory=lambda: dict[str, object]())
