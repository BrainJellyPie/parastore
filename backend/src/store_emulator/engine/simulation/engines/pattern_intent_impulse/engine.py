"""3-stage LLM pipeline engine. stage1 (pattern) → stage2 (intent) → stage3 (impulse)."""

import logging

from store_emulator.domain.action import CustomerAction
from store_emulator.domain.config import SimulationConfig
from store_emulator.domain.engine import PerCustomerContext, EngineDecision
from store_emulator.domain.store import Store
from store_emulator.domain.types import Action, PathFinder, TokenUsage, WEEKDAY_LABELS
from store_emulator.engine.llm_client import LiteLLMClient
from . import stage1_pattern, stage2_intent, stage3_impulse
from .stage2_intent import IntentResponse
from .stage3_impulse import ImpulseResponse
from store_emulator.engine.routing.route_builder import build_journey, find_exposed_products, integrate_actions

logger = logging.getLogger(__name__)


def _drop_invalid_buys(actions: list[CustomerAction], store: Store) -> list[CustomerAction]:
    """Drop buys whose product_sku does not exist in any slot (LLM hallucination guard).
    If only PAY remains afterwards, drop it too (no purchases → no payment).
    """
    valid_skus = {i.sku for r in store.racks for s in r.slots for i in s.items}
    kept: list[CustomerAction] = []
    for a in actions:
        if a.action == Action.BUY:
            if not a.product_sku or a.product_sku not in valid_skus:
                logger.info("[drop] LLM hallucinated buy sku=%r — dropped", a.product_sku)
                continue
        kept.append(a)
    has_buy = any(a.action == Action.BUY for a in kept)
    if not has_buy:
        kept = [a for a in kept if a.action != Action.PAY]
    return kept


class PatternIntentImpulseEngine:
    engine_type = "pattern_intent_impulse"

    def __init__(
        self,
        llm: LiteLLMClient,
        pathfinder: PathFinder,
        config: SimulationConfig,
    ):
        self._llm = llm
        self._pathfinder = pathfinder
        self._config = config

    def reset_usage(self) -> None:
        self._llm.reset_usage()

    def get_usage(self) -> TokenUsage:
        return self._llm.get_usage()

    async def decide_actions(
        self,
        context: PerCustomerContext,
    ) -> EngineDecision:
        patterns = context.behavior_patterns
        pattern_map = {p.id: p for p in patterns}
        fallback = patterns[0]
        day_of_week = WEEKDAY_LABELS[context.day]

        # Stage 1: pattern selection.
        stage1_system = stage1_pattern.build_system_prompt(patterns)
        stage1_user = stage1_pattern.build_user_prompt(
            context.persona, context.arrival_hour, context.store, day_of_week, context.cue,
            address=context.address, customer_profile=context.customer_profile,
        )
        selection = await self._llm.generate_structured_async(
            stage1_pattern.PatternSelectionResponse, stage1_system, stage1_user,
        )
        pattern = pattern_map.get(selection.pattern_id, fallback)
        grammar_override = selection.grammar_override

        # Stage 2: action-sequence generation.
        stage2_system = stage2_intent.build_system_prompt(pattern, grammar_override)
        stage2_user = stage2_intent.build_user_prompt(
            context.store, context.persona, context.arrival_hour, context.concurrent_visitors_in_hour,
            day_of_week, context.cue,
        )
        intent = await self._llm.generate_structured_async(IntentResponse, stage2_system, stage2_user)

        # Intermediate journey — used to compute exposed products for stage 3.
        journey = build_journey(
            context.store, intent.actions, self._pathfinder, self._config.block_move_sec,
        )
        exposed = find_exposed_products(context.store, journey)

        # Stage 3: impulse-purchase reactions.
        impulse: ImpulseResponse
        if exposed:
            existing_buys = sum(1 for a in intent.actions if a.action == Action.BUY)
            stage3_system = stage3_impulse.build_system_prompt(
                pattern.max_products, pattern.allow_no_purchase, existing_buys,
                pattern.browse_required_before_buy,
            )
            stage3_user = stage3_impulse.build_user_prompt(
                context.persona, intent, exposed, day_of_week,
                address=context.address, customer_profile=context.customer_profile,
                cue=context.cue, grid_size=context.store.grid_size,
            )
            impulse = await self._llm.generate_structured_async(ImpulseResponse, stage3_system, stage3_user)
        else:
            impulse = ImpulseResponse()

        merged = integrate_actions(context.store, intent.actions, impulse.actions)
        merged = _drop_invalid_buys(merged, context.store)

        return EngineDecision(
            actions=merged,
            engine_type=self.engine_type,
            trace={
                "stage1": selection.model_dump(),
                "stage2": intent.model_dump(),
                "stage3": impulse.model_dump(),
            },
        )
