"""Stage 2: action-sequence generation. Produces the customer's in-store event sequence from the chosen pattern."""

from pydantic import BaseModel

from store_emulator.domain.action import CustomerAction
from store_emulator.domain.behavior import BehaviorCue, BehaviorPattern
from store_emulator.domain.rack import RackType
from store_emulator.domain.persona import Persona
from store_emulator.domain.store import Store
from .prompt_utils import format_cue_prompt

LEVEL_PREFERENCE_GUIDE = [
    "L3: 눈높이로 가장 먼저 인지되는 편",
    "L2: 허리 높이로 그 다음으로 잘 보이는 편",
    "L4: 상단이라 인지는 되지만 손이 덜 가는 편",
    "L1: 하단이라 목적 구매가 아니면 우선순위가 낮은 편",
]


class IntentResponse(BaseModel):
    reasoning: str = ""
    actions: list[CustomerAction] = []


def build_system_prompt(pattern: BehaviorPattern, grammar_override: str = "") -> str:
    grammar = grammar_override if grammar_override else pattern.grammar

    rules: list[str] = []
    if pattern.browse_required_before_buy:
        rules.append("- buy 직전에 반드시 같은 rack에서의 browse가 있어야 합니다")
    if pattern.allow_no_purchase:
        rules.append("- 구매 없이 퇴장도 가능합니다")

    rules_text = "\n".join(rules)

    return f"""당신은 매장 고객 행동 시뮬레이터입니다.
주어진 매장 정보와 고객 페르소나를 보고, 이 고객이 매장에서 어떤 행동을 할지 이벤트 시퀀스를 생성하세요.

## 이 고객의 행동 패턴: {pattern.name}
{grammar}

규칙:
{rules_text}
- pay는 카운터에서 딱 1회만 발생합니다 (구매 물건이 없으면 생략)
- 시퀀스 순서는 enter → 이동/browse/buy → pay → exit
- 한 고객의 구매 상품은 최대 {pattern.max_products}개
- 반드시 {{"nav": "leave"}} 으로 종료
- **buy 의 product_sku 는 위 진열대 목록의 sku 중 하나만 사용**
- **browse / buy 의 description 은 위 진열대 목록의 상품만 묘사**
- **buy 는 위 진열대 목록에 적합한 상품이 있을 때만 추가**

모든 가격과 예산은 US cents 단위입니다 (예: 549¢ = $5.49).

필드 설명:
- action: 행동 유형. enter / move / browse / buy / pay / wander / exit 중 하나
- target: 위에 제시된 rack 의 '접근 타일' 좌표 중 하나 [x, y]
- face: 고객이 바라보는 rack 면 (N/S/E/W)
- dwell: 해당 위치 머무는 시간 (초, 최대 120)
- product_sku: buy 시 위 진열대 목록의 sku 중 하나
- nav="area" 일 때 area: [x1, y1, x2, y2] 배회 영역
- description: 해당 행동 시점의 상황만 묘사. 위 진열대 목록의 상품만 다룬다.

## 언어
- 자유 서술 필드(`reasoning` 및 각 action의 `description`)의 값은 **영어로** 작성하세요.
- 구조적 필드(`action`, `target`, `face`, `dwell`, `product_sku`, `nav`, `area`)는 한국어 prompt 에서 정의된 그대로 유지합니다.
- 영어 표현은 자연스러운 콘텐츠 톤을 유지하세요."""


def build_user_prompt(
    store: Store,
    persona: Persona,
    arrival_hour: int,
    concurrent_visitors_in_hour: int,
    day_of_week: str = "",
    cue: BehaviorCue | None = None,
) -> str:
    lines: list[str] = []

    lines.append("## 매장 정보")
    lines.append(f"- 유형: {store.type}")
    lines.append(f"- 그리드 크기: {store.grid_size[0]}×{store.grid_size[1]}")
    lines.append("")

    lines.append("## rack 및 상품")
    lines.append("공통 진열 높이 기준:")
    for guide in LEVEL_PREFERENCE_GUIDE:
        lines.append(f"  - {guide}")
    lines.append("같은 카테고리의 대안이 여러 개면 진열 높이 차이를 약하게 참고하되, 명확한 목적 구매는 고객 의도를 우선하세요.")
    lines.append("")
    for f in store.racks:
        if f.type in {RackType.ENTRANCE, RackType.EXIT}:
            continue
        access = sorted(f.access_tiles(store.grid_size))
        label = f.rack_name or f.id
        lines.append(f"### {f.id} ({f.type}, {label})")
        if f.rack_desc:
            lines.append(f"  설명: {f.rack_desc}")
        if f.rack_decoration_desc:
            lines.append(f"  부착물: {f.rack_decoration_desc}")
        if access:
            lines.append(f"  접근 타일: {access[:6]}{'...' if len(access) > 6 else ''}")
        for slot in f.slots:
            for item in slot.items:
                promo = f" [{item.promo}]" if item.promo else ""
                lines.append(
                    f"  - block{slot.block}/{slot.face} level={slot.level}: {item.name} ({item.sku}) {item.price}¢{promo}"
                )
    lines.append("")

    lines.append("## 입구/출구")
    for e in store.entrances:
        lines.append(f"  입구: {e.occupied_positions}")
    for e in store.exits:
        lines.append(f"  출구: {e.occupied_positions}")
    for c in store.counters:
        label = c.rack_name or c.id
        lines.append(f"  카운터: {label}, 결제 타일: {sorted(c.service_access_tiles(store.grid_size))[:4]}")
    lines.append("")

    lines.append("## 현재 상황")
    lines.append(f"- 시간: {arrival_hour}시")
    lines.append(f"- 같은 시간대 방문자: 약 {concurrent_visitors_in_hour}명")
    if day_of_week:
        lines.append(f"- 요일: {day_of_week}")
    if cue:
        lines.append(f"- 고객 상태: {format_cue_prompt(cue)}")
    lines.append("")

    lines.append("## 고객 페르소나")
    lines.append(f"- 유형: {persona.identity} ({persona.age_group}, {persona.gender})")
    lines.append(f"- 설명: {persona.description}")
    lines.append(f"- 방문 목적: {persona.purpose}")
    lines.append(f"- 의도: {persona.intent}")
    lines.append(f"- 선호 카테고리: {', '.join(persona.preferred_categories)}")
    lines.append(f"- 예산: {persona.budget_label}")
    lines.append(f"- 행동 성향: {persona.behavior_tendency}")
    lines.append("")

    lines.append("이 고객의 매장 내 행동 이벤트 시퀀스를 생성하세요.")
    return "\n".join(lines)


