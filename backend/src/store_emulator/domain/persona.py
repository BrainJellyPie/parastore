from typing import Literal

from pydantic import BaseModel

from .types import Weekday

type AgeGroup = Literal["10s", "20s", "30s", "40s", "50s", "60s+"]
type Gender = Literal["Male", "Female"]

AGE_GROUPS: list[AgeGroup] = ["10s", "20s", "30s", "40s", "50s", "60s+"]
GENDERS: list[Gender] = ["Male", "Female"]


class Persona(BaseModel):
    id: str
    day: Weekday = Weekday.MON
    identity: str
    age_group: AgeGroup
    gender: Gender
    description: str
    intent: str
    purpose: str
    arrival_hour: int = 12  # 0–23 (not enforced by a Field constraint)
    preferred_categories: list[str] = []
    budget_min: int = 0  # unit: US cents
    budget_max: int = 0  # unit: US cents
    behavior_tendency: str = ""

    @property
    def budget_label(self) -> str:
        return f"{self.budget_min}¢~{self.budget_max}¢"
