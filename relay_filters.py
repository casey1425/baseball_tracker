"""Filtering helpers for play-by-play relay entries."""

RESULT_FILTERS = (
    "홈런",
    "안타·장타",
    "득점",
    "삼진",
    "볼넷·사구",
    "아웃",
    "선수 교체",
)

RESULT_KEYWORDS = {
    "홈런": ("홈런",),
    "안타·장타": ("1루타", "2루타", "3루타", "안타"),
    "득점": ("득점", "홈인", "적시타", "타점", "끝내기", "희생플라이", "밀어내기"),
    "삼진": ("삼진",),
    "볼넷·사구": ("볼넷", "사구", "몸에 맞는",),
    "아웃": ("아웃", "병살", "플라이", "땅볼",),
    "선수 교체": ("교체", "대타", "대주자", "투수 변경",),
}


def matches_result_type(text, result_type):
    """Match a result without folding home runs into hits or strikeouts into outs."""
    if result_type == "안타·장타" and "홈런" in text:
        return False
    if result_type == "아웃" and any(keyword in text for keyword in ("삼진", "낫아웃")):
        return False
    return any(keyword in text for keyword in RESULT_KEYWORDS[result_type])


def relay_text(entry):
    """Return all searchable text in a relay entry."""
    parts = [entry.get("title") or ""]
    parts.extend(option.get("text") or "" for option in (entry.get("textOptions") or []))
    return " ".join(parts)


def available_innings(entries):
    """Return inning numbers in numeric order, followed by non-numeric values."""
    values = {str(entry.get("inn")) for entry in entries if entry.get("inn") not in (None, "")}
    return sorted(values, key=lambda value: (not value.isdigit(), int(value) if value.isdigit() else value))


def filter_relays(entries, query="", inning="전체", result_types=None):
    """Filter relay entries with AND across controls and OR across result types."""
    normalized_query = " ".join(query.casefold().split())
    selected_types = tuple(result_types or ())
    filtered = []

    for entry in entries:
        text = relay_text(entry)
        normalized_text = " ".join(text.casefold().split())
        if normalized_query and normalized_query not in normalized_text:
            continue
        if inning != "전체" and str(entry.get("inn")) != str(inning):
            continue
        if selected_types and not any(matches_result_type(text, result_type) for result_type in selected_types):
            continue
        filtered.append(entry)

    return filtered
