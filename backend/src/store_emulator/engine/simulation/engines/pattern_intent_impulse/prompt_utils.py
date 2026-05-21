from store_emulator.domain.behavior import BehaviorCue


def format_cue_prompt(cue: BehaviorCue) -> str:
    parts: list[str] = []
    if cue.state:
        parts.append(f"컨디션: {cue.state}")
    if cue.purse:
        parts.append(f"소비심리: {cue.purse}")
    if cue.emotion:
        parts.append(f"기분: {cue.emotion}")
    if cue.company:
        parts.append(f"동행: {cue.company}")
    return ", ".join(parts) if parts else "특이사항 없음"
