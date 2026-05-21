from collections import Counter

from store_emulator.domain.customer import CustomerResult
from store_emulator.domain.persona import Persona
from store_emulator.domain.store import Store

from store_emulator.domain.result import AggregatedResult, SimulationSummary


def aggregate(
    store: Store,
    results: list[CustomerResult],
    personas: list[Persona],
    pathcalc_heatmap: list[list[float]],
) -> AggregatedResult:
    persona_map = {p.id: p for p in personas}

    product_revenue: Counter[str] = Counter()
    for cr in results:
        for event in cr.purchases:
            product_revenue[event.product_name] += event.price
    top_products = [name for name, _ in product_revenue.most_common(10)]

    w, h = store.grid_size
    behavioral: list[list[int]] = [[0] * w for _ in range(h)]
    for cr in results:
        for event in cr.timeline:
            if 0 <= event.x < w and 0 <= event.y < h:
                behavioral[event.y][event.x] += 1

    by_purpose: Counter[str] = Counter()
    by_identity: Counter[str] = Counter()
    by_age: Counter[str] = Counter()
    by_gender: Counter[str] = Counter()
    for cr in results:
        p = persona_map.get(cr.persona_id)
        if not p:
            continue
        by_purpose[p.purpose] += 1
        by_identity[p.identity] += 1
        by_age[p.age_group] += 1
        by_gender[p.gender] += 1

    summary = SimulationSummary(
        store_id=store.id,
        total_customers=len(results),
        total_revenue=sum(cr.total_spent for cr in results),
        top_products=top_products,
        by_purpose=dict(by_purpose),
        by_identity=dict(by_identity),
        by_age=dict(by_age),
        by_gender=dict(by_gender),
    )

    return AggregatedResult(
        summary=summary,
        pathcalc_heatmap=pathcalc_heatmap,
        persona_heatmap=behavioral,
    )
