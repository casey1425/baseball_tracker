"""Compact relay and lineup data for the Next.js game-detail tabs."""

from relay_filters import RESULT_FILTERS, matches_result_type, relay_text


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _inning_label(entry):
    inning = entry.get("inn", "-")
    half = "말" if str(entry.get("homeOrAway")) == "1" else "초"
    return f"{inning}회{half}"


def _score_from_options(options, away_name, home_name):
    for option in reversed(options):
        state = option.get("currentGameState") or {}
        away_score = state.get("awayScore")
        home_score = state.get("homeScore")
        if away_score is not None and home_score is not None:
            return f"{away_name} {away_score} : {home_score} {home_name}"
    return ""


def build_relay_entries(text_relays, home_name="홈", away_name="원정"):
    """Remove repeated player metadata and retain searchable play-by-play fields."""
    entries = []
    seen = set()
    for entry in text_relays:
        no = entry.get("no")
        if no is not None and no in seen:
            continue
        if no is not None:
            seen.add(no)

        title = (entry.get("title") or "").strip()
        if not title or "====" in title or "공격" in title:
            continue
        options = entry.get("textOptions") or []
        messages = [
            (option.get("text") or "").strip()
            for option in options
            if option.get("type") != 1
            and (option.get("text") or "").strip()
            and "====" not in (option.get("text") or "")
            and "공격" not in (option.get("text") or "")
        ]
        result = next((message for message in reversed(messages) if message != title), messages[-1] if messages else "")
        pitches = []
        for option in options:
            if option.get("type") != 1:
                continue
            state = option.get("currentGameState") or {}
            pitches.append({
                "number": _integer(option.get("pitchNum")) or len(pitches) + 1,
                "text": (option.get("text") or "").strip(),
                "pitch_type": (option.get("stuff") or "").strip() or "-",
                "speed": str(option.get("speed") or "").strip(),
                "ball": _integer(state.get("ball")),
                "strike": _integer(state.get("strike")),
                "out": _integer(state.get("out")),
            })
        searchable = relay_text(entry)
        categories = [name for name in RESULT_FILTERS if matches_result_type(searchable, name)]
        if not result and not pitches:
            continue
        entries.append({
            "id": str(no if no is not None else len(entries)),
            "inning_number": str(entry.get("inn") or "-"),
            "inning": _inning_label(entry),
            "title": title,
            "result": result or pitches[-1]["text"],
            "score": _score_from_options(options, away_name, home_name),
            "categories": categories,
            "pitches": pitches,
            "order": _integer(no),
        })
    return sorted(entries, key=lambda item: item["order"], reverse=True)


def _batters(lineup):
    rows = []
    for player in lineup.get("batter") or []:
        rows.append({
            "order": _integer(player.get("batOrder")),
            "name": player.get("name") or "-",
            "position": player.get("posName") or "-",
            "at_bats": _integer(player.get("ab")),
            "hits": _integer(player.get("hit")),
            "home_runs": _integer(player.get("hr")),
            "rbi": _integer(player.get("rbi")),
            "runs": _integer(player.get("run")),
            "walks": _integer(player.get("bb")) + _integer(player.get("hbp")),
            "strikeouts": _integer(player.get("so")),
            "season_average": _number(player.get("seasonHra")),
            "substitute": str(player.get("cin") or "").lower() == "true",
        })
    return rows


def _pitchers(lineup):
    rows = []
    for player in lineup.get("pitcher") or []:
        rows.append({
            "name": player.get("name") or "-",
            "innings": str(player.get("inn") or "0.0"),
            "pitch_count": _integer(player.get("ballCount")),
            "hits": _integer(player.get("hit")),
            "home_runs": _integer(player.get("hr")),
            "walks": _integer(player.get("bb")) + _integer(player.get("hbp")),
            "strikeouts": _integer(player.get("kk")),
            "runs": _integer(player.get("run")),
            "earned_runs": _integer(player.get("er")),
            "season_era": str(player.get("seasonEra") or "-"),
        })
    return rows


def build_boxscore(home_lineup, away_lineup, home_name="홈", away_name="원정"):
    return {
        "home": {"team": home_name, "batters": _batters(home_lineup), "pitchers": _pitchers(home_lineup)},
        "away": {"team": away_name, "batters": _batters(away_lineup), "pitchers": _pitchers(away_lineup)},
    }
