from enum import IntEnum, StrEnum
from typing import Protocol

from pydantic import BaseModel

type Position = tuple[int, int]
type Shape = list[list[int]]

CARDINAL_DIRECTIONS: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]


class Weekday(IntEnum):
    MON = 1
    TUE = 2
    WED = 3
    THU = 4
    FRI = 5
    SAT = 6
    SUN = 7


WEEKDAY_LABELS: dict[Weekday, str] = {
    Weekday.MON: "월요일",
    Weekday.TUE: "화요일",
    Weekday.WED: "수요일",
    Weekday.THU: "목요일",
    Weekday.FRI: "금요일",
    Weekday.SAT: "토요일",
    Weekday.SUN: "일요일",
}


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __iadd__(self, other: "TokenUsage") -> "TokenUsage":
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        return self


class Face(StrEnum):
    N = "N"
    S = "S"
    E = "E"
    W = "W"


class Action(StrEnum):
    ENTER = "enter"
    MOVE = "move"
    BROWSE = "browse"
    BUY = "buy"
    PAY = "pay"
    WANDER = "wander"
    EXIT = "exit"


class AsyncLLMClient(Protocol):
    async def generate_structured_async[T: BaseModel](self, response_model: type[T], system_prompt: str, user_prompt: str, *, max_retries: int = 1) -> T: ...
    async def generate_text_async(self, system_prompt: str, user_prompt: str, *, enable_search: bool = False) -> str: ...


class PathFinder(Protocol):
    def find_path(self, walkable_grid: list[list[bool]], start: Position, end: Position) -> list[Position]: ...
