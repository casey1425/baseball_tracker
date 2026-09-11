"""Build a compact live at-bat view from Naver relay payloads."""

import re


UNAVAILABLE_STATUS_CODES = {
    "BEFORE", "READY", "SCHEDULED", "POSTPONED", "CANCEL", "CANCELED",
}
FINISHED_STATUS_CODES = {"RESULT", "ENDED", "FINAL"}


def relay_is_available(game):
    status_code = str(game.get("statusCode") or "").upper()
    return not bool(game.get("cancel")) and status_code not in UNAVAILABLE_STATUS_CODES


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _player_name(lineups, role, code):
    if not code:
        return "-"
    for lineup in lineups:
        for player in lineup.get(role) or []:
            if str(player.get("pcode")) == str(code):
                return player.get("name") or "-"
    return "-"


def _is_plate_appearance(entry):
    title = (entry.get("title") or "").strip()
    return bool(title and "타자" in title and "====" not in title)


def _has_pitches(entry):
    return any(option.get("type") == 1 for option in entry.get("textOptions") or [])


def _entry_number(entry):
    return _to_int(entry.get("no"))


def _select_plate_appearance(text_relays, finished):
    candidates = sorted(
        (entry for entry in text_relays if _is_plate_appearance(entry)),
        key=_entry_number,
        reverse=True,
    )
    if finished:
        return next((entry for entry in candidates if _has_pitches(entry)), candidates[0] if candidates else {})
    return candidates[0] if candidates else {}


def _latest_state(relay, plate):
    state = relay.get("current_state") or {}
    if state:
        return state
    for option in reversed(plate.get("textOptions") or []):
        if option.get("currentGameState"):
            return option["currentGameState"]
    return {}


def _batter_from_title(title):
    match = re.search(r"(?:\d+번)?타자\s+(.+)", title or "")
    return match.group(1).strip() if match else "-"


def build_live_situation(game, relay):
    """Normalize the latest relay response for the web dashboard."""
    status_code = str(game.get("statusCode") or "").upper()
    finished = status_code in FINISHED_STATUS_CODES
    if not relay_is_available(game):
        return {
            "available": False,
            "phase": "scheduled",
            "message": "경기 시작 후 실시간 타석 상황이 표시됩니다.",
        }

    text_relays = relay.get("text_relays") or []
    plate = _select_plate_appearance(text_relays, finished)
    state = _latest_state(relay, plate)
    lineups = [relay.get("home_lineup") or {}, relay.get("away_lineup") or {}]
    pitcher_name = _player_name(lineups, "pitcher", state.get("pitcher"))
    batter_name = _player_name(lineups, "batter", state.get("batter"))
    if finished or batter_name == "-":
        batter_name = _batter_from_title(plate.get("title"))

    pitches = []
    for index, option in enumerate(plate.get("textOptions") or [], start=1):
        if option.get("type") != 1:
            continue
        pitches.append({
            "number": _to_int(option.get("pitchNum")) or len(pitches) + 1,
            "text": (option.get("text") or "").strip(),
            "pitch_type": (option.get("stuff") or "").strip() or "구종 정보 없음",
            "speed": str(option.get("speed") or "").strip(),
            "result_code": option.get("pitchResult") or "",
        })

    meaningful = [
        (option.get("text") or "").strip()
        for option in plate.get("textOptions") or []
        if option.get("type") not in {0, 1, 8, 99} and (option.get("text") or "").strip()
    ]
    latest_pitch = pitches[-1]["text"] if pitches else ""
    inning = plate.get("inn") or game.get("currentInning") or "-"
    half = "말" if str(plate.get("homeOrAway")) == "1" else "초"
    home_team = game.get("homeTeamName") or "홈"
    away_team = game.get("awayTeamName") or "원정"
    offense_team = home_team if str(plate.get("homeOrAway")) == "1" else away_team

    return {
        "available": bool(plate or state),
        "phase": "final" if finished else "live",
        "message": "경기 종료 · 마지막 타석" if finished else "실시간 타석",
        "inning": f"{inning}회{half}" if str(inning).isdigit() else str(inning),
        "offense_team": offense_team,
        "pitcher": {"code": str(state.get("pitcher") or ""), "name": pitcher_name},
        "batter": {"code": str(state.get("batter") or ""), "name": batter_name},
        "count": {
            "balls": min(_to_int(state.get("ball")), 3),
            "strikes": min(_to_int(state.get("strike")), 2),
            "outs": min(_to_int(state.get("out")), 2),
        },
        "bases": {
            "first": str(state.get("base1") or "0") not in {"0", ""},
            "second": str(state.get("base2") or "0") not in {"0", ""},
            "third": str(state.get("base3") or "0") not in {"0", ""},
        },
        "recent_pitches": pitches[-5:],
        "last_result": meaningful[-1] if meaningful else latest_pitch or (plate.get("title") or ""),
        "matchup": relay.get("pitcher_vs_batter") or "",
    }
