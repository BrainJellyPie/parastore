import random

from store_emulator.domain.behavior import BehaviorCue, BehaviorPattern

PURPOSEFUL = BehaviorPattern(
    id="purposeful",
    name="목적구매형",
    description="명확한 구매 목적을 가지고 입장. 필요한 상품을 찾아 구매 후 퇴장.",
    grammar="""\
이 고객은 명확한 구매 목적이 있습니다.
흐름: 입장 → 목표 rack로 이동 → browse(둘러보기) → buy(구매) → 카운터에서 pay → 퇴장
- 필요한 상품이 있는 rack를 찾아가 browse 후 buy
- browse → buy 쌍을 반복하며 필요한 것을 모두 구매
- 쇼핑이 끝나면 카운터로 이동하여 결제""",
    browse_required_before_buy=True,
    max_products=5,
    allow_no_purchase=False,
)

HABITUAL = BehaviorPattern(
    id="habitual",
    name="습관형",
    description="매일 같은 상품을 사는 단골. 매장 구조를 잘 알아 바로 이동.",
    grammar="""\
이 고객은 매장 단골로 어디에 뭐가 있는지 잘 압니다.
흐름: 입장 → 알고 있는 위치로 바로 move_to → buy → 카운터에서 pay → 퇴장
- browse 없이 바로 buy 가능 (이미 상품을 잘 알고 있음)
- 빠르게 이동하며 dwell 시간이 짧음
- 여러 목표 상품을 순차적으로 방문""",
    browse_required_before_buy=False,
    max_products=5,
    allow_no_purchase=False,
)

ROUTINE_REFILL = BehaviorPattern(
    id="routine_refill",
    name="정기보충형",
    description="정해진 품목을 여러 개 보충 구매. 효율적 동선.",
    grammar="""\
이 고객은 여러 품목을 정기적으로 보충하러 왔습니다.
흐름: 입장 → [move_to → buy]+ → 카운터에서 pay → 퇴장
- 여러 rack를 순차적으로 방문하며 필요한 품목을 구매
- browse 없이 바로 buy 가능 (이미 알고 있는 상품)
- 효율적 동선으로 이동, 불필요한 배회 없음""",
    browse_required_before_buy=False,
    max_products=5,
    allow_no_purchase=False,
)

URGENT = BehaviorPattern(
    id="urgent",
    name="급한구매형",
    description="시간이 없어 최대한 빨리 하나만 사서 나감.",
    grammar="""\
이 고객은 매우 급합니다. 최단 시간 내에 구매를 끝내야 합니다.
흐름: 입장 → 가장 가까운 목표로 move_to → buy → 카운터에서 pay → 퇴장
- 1~2개 품목만 구매
- dwell 시간 최소 (5초 이하)
- 입구에서 가장 가까운 상품 우선
- wander나 여유로운 browse 없음""",
    browse_required_before_buy=False,
    max_products=2,
    allow_no_purchase=False,
)

QUICK_SNACK = BehaviorPattern(
    id="quick_snack",
    name="간식하나형",
    description="간식이나 음료 딱 하나만 빠르게 사서 나감.",
    grammar="""\
이 고객은 간식이나 음료 하나만 사러 왔습니다.
흐름: 입장 → move_to → buy(1개) → 카운터에서 pay → 퇴장
- 단일 품목만 구매
- 빠른 이동, 짧은 체류
- 입구에서 가까운 간식/음료 코너 우선""",
    browse_required_before_buy=False,
    max_products=1,
    allow_no_purchase=False,
)

EXPLORATORY = BehaviorPattern(
    id="exploratory",
    name="탐색형",
    description="뭐가 있나 둘러보러 입장. 마음에 드는 게 있으면 구매할 수도.",
    grammar="""\
이 고객은 특별한 목적 없이 매장을 둘러보러 왔습니다.
흐름: 입장 → wander(배회) → [browse → 마음에 들면 buy]* → [카운터에서 pay] → 퇴장
- 먼저 매장을 배회하며 어떤 상품이 있는지 살펴봄
- 흥미로운 rack를 발견하면 browse
- 마음에 들면 buy, 아니면 다음으로 이동
- 아무것도 안 사고 나갈 수도 있음""",
    browse_required_before_buy=False,
    max_products=4,
    allow_no_purchase=True,
)

HUNGRY_WANDERING = BehaviorPattern(
    id="hungry_wandering",
    name="배고픈방황형",
    description="배고프지만 뭘 먹을지 모르겠어서 둘러보는 중.",
    grammar="""\
이 고객은 배가 고파서 들어왔지만 뭘 살지 정하지 못했습니다.
흐름: 입장 → wander(음식 코너 위주 배회) → [browse → 고민 후 buy]* → 카운터에서 pay → 퇴장
- 도시락, 삼각김밥, 빵 등 식사류 rack 위주로 배회
- 여러 옵션을 browse하며 비교
- 결국 하나를 선택하여 buy
- 음료도 추가 구매할 수 있음""",
    browse_required_before_buy=False,
    max_products=3,
    allow_no_purchase=True,
)

LEISURELY = BehaviorPattern(
    id="leisurely",
    name="여유산책형",
    description="시간이 많아 천천히 매장을 둘러보며 쇼핑을 즐김.",
    grammar="""\
이 고객은 시간 여유가 많아 느긋하게 쇼핑합니다.
흐름: 입장 → [wander → browse]* → [마음에 들면 buy]* → [카운터에서 pay] → 퇴장
- 천천히 매장 전체를 둘러봄 (긴 dwell 시간)
- 여러 rack를 순서 없이 방문
- 흥미로운 상품을 발견하면 오래 살펴봄
- 구매는 선택적""",
    browse_required_before_buy=False,
    max_products=5,
    allow_no_purchase=True,
)

SOCIAL_BROWSING = BehaviorPattern(
    id="social_browsing",
    name="사교둘러보기형",
    description="친구와 함께 와서 대화하며 둘러보고 간식을 고름.",
    grammar="""\
이 고객은 일행과 함께 와서 대화하며 둘러봅니다.
흐름: 입장 → [wander|browse]* → [buy]* → 카운터에서 pay → 퇴장
- 대화하며 여유롭게 배회 (긴 wander)
- 이것저것 구경하며 서로 추천
- 충동적으로 구매 결정
- 체류 시간이 길고 wander가 많음""",
    browse_required_before_buy=False,
    max_products=5,
    allow_no_purchase=True,
)

IMPULSE_HEAVY = BehaviorPattern(
    id="impulse_heavy",
    name="충동구매형",
    description="딱히 목적 없이 왔지만 보이는 대로 담는 타입.",
    grammar="""\
이 고객은 충동구매 성향이 강합니다.
흐름: 입장 → wander → [browse → buy]* → 카운터에서 pay → 퇴장
- 매장을 돌아다니다가 눈에 띄는 상품마다 browse → buy
- 프로모션이나 신제품에 특히 반응
- 계획에 없던 상품도 많이 구매
- buy 전에 반드시 browse (잠깐이라도 살펴봄)""",
    browse_required_before_buy=True,
    max_products=5,
    allow_no_purchase=False,
)

WINDOW_SHOPPING = BehaviorPattern(
    id="window_shopping",
    name="구경형",
    description="살 생각 없이 구경만 하다 나감. 시간 때우기.",
    grammar="""\
이 고객은 구매 의사가 거의 없이 구경만 합니다.
흐름: 입장 → [wander → browse]* → 퇴장
- 매장을 천천히 돌아다니며 상품을 구경
- 여러 rack에서 browse하지만 buy하지 않음
- pay 없이 바로 퇴장
- 신제품이나 프로모션 확인 목적""",
    browse_required_before_buy=False,
    max_products=0,
    allow_no_purchase=True,
)

DEAL_HUNTING = BehaviorPattern(
    id="deal_hunting",
    name="할인사냥형",
    description="할인/프로모션 상품만 집중적으로 찾아다님.",
    grammar="""\
이 고객은 할인 상품과 프로모션만 찾습니다.
흐름: 입장 → [프로모션 rack로 이동 → browse(할인 확인)]* → [할인 상품 buy]* → [카운터에서 pay] → 퇴장
- 프로모션 표시가 있는 rack를 우선 방문
- [promo] 태그가 있는 상품 위주로 browse
- 할인율이 높은 상품만 buy
- 정가 상품은 browse만 하고 넘어감
- buy 전에 반드시 가격을 확인하는 browse""",
    browse_required_before_buy=True,
    max_products=5,
    allow_no_purchase=True,
)


BEHAVIOR_PATTERNS: list[BehaviorPattern] = [
    PURPOSEFUL, HABITUAL, ROUTINE_REFILL,
    URGENT, QUICK_SNACK,
    EXPLORATORY, HUNGRY_WANDERING, LEISURELY,
    SOCIAL_BROWSING, IMPULSE_HEAVY,
    WINDOW_SHOPPING, DEAL_HUNTING,
]


# SPEC word pools (per-customer behavior variation seeds).
# Tuples are (word, weight). Higher weight = chosen more often.
# None means "this dimension does not apply" for the sampled customer.

WeightedWord = tuple[str | None, int]

# S: State (condition) → influences category preference, urgency, dwell pattern.
STATE_POOL: list[WeightedWord] = [
    (None, 30),
    ("피곤함", 12),
    ("좀지침", 10),
    ("배고픔", 9),
    ("출출함", 7),
    ("목마름", 8),
    ("나른함", 7),
    ("졸림", 5),
    ("기력충만", 5),
    ("상쾌함", 4),
    ("발걸음가벼움", 3),
    ("몸이무거움", 4),
    ("에너지넘침", 3),
]

# P: Purse (spending mindset) → price sensitivity, impulse resistance, premium/discount preference.
PURSE_POOL: list[WeightedWord] = [
    (None, 25),
    ("가성비추구", 12),
    ("절약모드", 10),
    ("예산빠듯", 8),
    ("카드값걱정", 6),
    ("아끼는중", 7),
    ("월급직후", 5),
    ("자기보상", 5),
    ("여유있음", 5),
    ("프리미엄기분", 4),
    ("충동경계중", 4),
    ("플렉스모드", 3),
    ("무계획소비", 4),
    ("포인트소진", 3),
    ("이왕이면좋은걸", 4),
]

# E: Emotion (mood) → dwell time, impulse-buy probability, patience.
EMOTION_POOL: list[WeightedWord] = [
    (None, 20),
    ("무덤덤", 12),
    ("기분좋음", 10),
    ("콧노래흥얼", 5),
    ("느긋함", 8),
    ("심드렁", 6),
    ("짜증남", 5),
    ("신경날카로움", 4),
    ("스트레스만땅", 5),
    ("설렘", 4),
    ("들뜸", 3),
    ("울적함", 4),
    ("심심함", 5),
    ("초조함", 3),
    ("후련함", 3),
    ("허전함", 3),
]

# C: Company (companions) → speed, exploration breadth, item count, item choice.
COMPANY_POOL: list[WeightedWord] = [
    ("혼자", 40),
    ("친구랑", 10),
    ("연인과 같이 옴", 6),
    ("가족이랑", 8),
    ("아이데리고", 5),
    ("동료랑", 6),
    ("부모님이랑", 4),
    ("후배랑", 3),
    ("윗사람이랑", 2),
    ("이웃이랑", 2),
]


def _weighted_choice(rng: random.Random, pool: list[WeightedWord]) -> str | None:
    words, weights = zip(*pool, strict=True)
    return rng.choices(words, weights=weights, k=1)[0]


def sample_cue(rng: random.Random) -> BehaviorCue:
    return BehaviorCue(
        state=_weighted_choice(rng, STATE_POOL),
        purse=_weighted_choice(rng, PURSE_POOL),
        emotion=_weighted_choice(rng, EMOTION_POOL),
        company=_weighted_choice(rng, COMPANY_POOL),
    )
