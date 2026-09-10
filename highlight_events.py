"""Extract and classify highlight events from Naver KBO relay data."""

EVENT_META = {
    "홈런": {"icon": "🔥", "color": "#E53935", "tag_bg": "#FFEBEE"},
    "득점": {"icon": "⚾", "color": "#1E88E5", "tag_bg": "#E3F2FD"},
    "안타/장타": {"icon": "🏏", "color": "#00897B", "tag_bg": "#E0F2F1"},
    "선수교체": {"icon": "🔄", "color": "#8E24AA", "tag_bg": "#F3E5F5"},
    "승부처": {"icon": "⚠️", "color": "#FB8C00", "tag_bg": "#FFF3E0"},
    "삼진": {"icon": "⚡", "color": "#546E7A", "tag_bg": "#ECEFF1"},
    "경기결과": {"icon": "🏁", "color": "#43A047", "tag_bg": "#E8F5E9"},
}


def classify_highlight(text, option_type=None):
    """Classify one relay message by its text.

    Naver's type 23 is used for hits that produce runner advances, not only
    home runs, so hit outcomes must be classified from the actual message.
    """
    if "홈런" in text:
        return "홈런"
    if any(keyword in text for keyword in ("득점", "적시타", "밀어내기", "홈인", "희생플라이")):
        return "득점"
    if any(keyword in text for keyword in ("1루타", "2루타", "3루타", "안타")):
        return "안타/장타"
    if option_type == 2 or "교체" in text or "수비위치 변경" in text:
        return "선수교체"
    if any(keyword in text for keyword in ("병살타", "삼중살", "낫아웃")):
        return "승부처"
    if "삼진" in text:
        return "삼진"
    if "승리투수" in text or "종료" in text:
        return "경기결과"
    return None


def extract_highlights(text_relays, home_name="홈", away_name="원정"):
    """Return highlight messages in chronological sequence-number order."""
    highlights = []
    seen_no = set()

    for at_bat in text_relays:
        no = at_bat.get("no")
        if no is not None and no in seen_no:
            continue
        if no is not None:
            seen_no.add(no)

        inning = at_bat.get("inn", "-")
        half = "말" if str(at_bat.get("homeOrAway")) == "1" else "초"
        inning_label = f"{inning}회{half}"

        for option_index, option in enumerate(at_bat.get("textOptions") or []):
            message = (option.get("text") or "").strip()
            if not message or "==" in message or "공격" in message:
                continue

            event_type = classify_highlight(message, option.get("type"))
            if event_type is None:
                continue

            state = option.get("currentGameState") or {}
            home_score = state.get("homeScore")
            away_score = state.get("awayScore")
            score = ""
            if home_score is not None and away_score is not None:
                score = f"{away_name} {away_score} : {home_score} {home_name}"

            meta = EVENT_META[event_type]
            highlights.append({
                "inning": inning_label,
                "event_type": event_type,
                "icon": meta["icon"],
                "color": meta["color"],
                "tag_bg": meta["tag_bg"],
                "text": message,
                "score": score,
                "seqno": option.get("seqno"),
                "fallback_order": (str(inning), str(no), option_index),
            })

    highlights.sort(key=lambda item: (
        item["seqno"] is None,
        item["seqno"] if item["seqno"] is not None else item["fallback_order"],
    ))
    for item in highlights:
        item.pop("fallback_order", None)
    return highlights
