from __future__ import annotations


def review_pilot(*, title: str, declared_claim: str, duration_s: float, character_count: int, location_count: int, shot_count: int, has_cold_open: bool, has_reversal: bool, has_cliffhanger: bool) -> dict:
    issues = []
    if not 30 <= duration_s <= 45:
        issues.append("Pilot duration must be 30–45 seconds.")
    if character_count > 3:
        issues.append("Too many characters for a consistency pilot.")
    if location_count > 2:
        issues.append("Too many locations for a bounded pilot.")
    if not 8 <= shot_count <= 14:
        issues.append("Shot count should stay between 8 and 14.")
    if not has_cold_open:
        issues.append("Missing cold-open danger or conflict.")
    if not has_reversal:
        issues.append("Missing visible reversal.")
    if not has_cliffhanger:
        issues.append("Missing end hook.")
    popularity = "unverified" if "最火" in declared_claim else "not_claimed"
    notes = []
    if popularity == "unverified":
        notes.append("不能声称该原创Pilot本身是当前市场最火；只能说明它采用高频穿越爽剧结构。")
    return {
        "title": title,
        "creative_fit": "pass" if not issues else "block",
        "market_claim": popularity,
        "issues": issues,
        "notes": notes,
    }
