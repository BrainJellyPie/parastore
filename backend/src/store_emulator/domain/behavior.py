from pydantic import BaseModel, ConfigDict


class BehaviorPattern(BaseModel):
    id: str
    name: str
    description: str
    grammar: str
    browse_required_before_buy: bool
    max_products: int = 5
    allow_no_purchase: bool = False


class BehaviorCue(BaseModel):
    """Per-customer behavior variation seed: state / purse / emotion / company."""

    model_config = ConfigDict(frozen=True)

    state: str | None = None
    purse: str | None = None
    emotion: str | None = None
    company: str | None = None
