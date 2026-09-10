"""Normalize KBO standings and recent-form API responses for display."""

from datetime import datetime


TEAM_ALIASES = {
    "KIA": "KIA", "기아": "KIA", "HT": "KIA",
    "삼성": "삼성", "SS": "삼성",
    "LG": "LG",
    "두산": "두산", "OB": "두산",
    "KT": "KT", "kt": "KT",
    "SSG": "SSG", "SK": "SSG",
    "롯데": "롯데", "LT": "롯데",
    "한화": "한화", "HH": "한화",
    "NC": "NC",
    "키움": "키움", "WO": "키움",
}


def normalize_team(value):
    return TEAM_ALIASES.get(str(value), str(value))


def _integer(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _float(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _next_game(team):
    game_id = str(team.get("nextScheduleGameId") or "")
    opponent = team.get("opposingTeamName") or "미정"
    if len(game_id) < 12 or not game_id[:8].isdigit():
        return {"date": "일정 미정", "opponent": opponent, "location": ""}

    game_date = datetime.strptime(game_id[:8], "%Y%m%d").strftime("%m월 %d일")
    away_code = normalize_team(game_id[8:10])
    location = "원정" if normalize_team(team.get("teamId")) == away_code else "홈"
    return {"date": game_date, "opponent": opponent, "location": location, "game_id": game_id}


def build_standings(team_stats, recent_stats, favorite_team="선택 안 함"):
    """Merge season standings with last-ten-game aggregates."""
    recent_by_id = {str(item.get("teamId")): item for item in recent_stats}
    ordered = sorted(team_stats, key=lambda item: _integer(item.get("ranking")) or 999)
    fifth = next((item for item in ordered if _integer(item.get("ranking")) == 5), None)
    fifth_behind = _float((fifth or {}).get("gameBehind"))
    favorite = normalize_team(favorite_team)
    rows = []
    favorite_next_game = None

    for team in ordered:
        rank = _integer(team.get("ranking"))
        team_id = str(team.get("teamId") or "")
        name = normalize_team(team.get("teamName") or team_id)
        recent = recent_by_id.get(team_id, {})
        runs_for = _integer(team.get("offenseRun"))
        runs_against = _integer(team.get("defenseR"))
        game_behind = _float(team.get("gameBehind"))
        is_favorite = favorite_team != "선택 안 함" and name == favorite

        if rank < 5:
            fifth_gap = f"5위에 {max(0.0, fifth_behind - game_behind):.1f}G 앞"
        elif rank == 5:
            fifth_gap = "5위"
        else:
            fifth_gap = f"5위와 {max(0.0, game_behind - fifth_behind):.1f}G"

        next_game = _next_game(team)
        if is_favorite:
            favorite_next_game = next_game

        rows.append({
            "응원": "⭐" if is_favorite else "",
            "순위": rank,
            "팀": name,
            "경기": _integer(team.get("gameCount")),
            "승": _integer(team.get("winGameCount")),
            "무": _integer(team.get("drawnGameCount")),
            "패": _integer(team.get("loseGameCount")),
            "승률": _float(team.get("wra")),
            "최근 10경기": recent.get("lastTenGameResult") or "자료 없음",
            "연속": team.get("continuousGameResult") or "-",
            "득실차": runs_for - runs_against,
            "1위 차": game_behind,
            "5위 차": fifth_gap,
        })

    return rows, favorite_next_game
