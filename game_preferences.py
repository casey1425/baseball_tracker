"""Local favorite-team preferences and stable game selection."""
import json
from pathlib import Path

TEAMS = ("선택 안 함", "KIA", "삼성", "LG", "두산", "KT", "SSG", "롯데", "한화", "NC", "키움")
PREFERENCES_PATH = Path(__file__).resolve().parent / ".streamlit" / "preferences.json"


def load_favorite(path=None):
    try:
        data = json.loads(Path(path or PREFERENCES_PATH).read_text(encoding="utf-8"))
        team = data.get("favorite_team") if isinstance(data, dict) else None
        return team if team in TEAMS else TEAMS[0]
    except (OSError, ValueError):
        return TEAMS[0]


def save_favorite(team, path=None):
    if team not in TEAMS:
        raise ValueError("지원하지 않는 구단입니다.")
    target = Path(path or PREFERENCES_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps({"favorite_team": team}, ensure_ascii=False), encoding="utf-8")
    temporary.replace(target)


def is_favorite(game, team):
    def normalize(name):
        return str(name).upper().replace("기아", "KIA")
    return team != TEAMS[0] and normalize(team) in (normalize(game["home"]), normalize(game["away"]))


def ordered_games(games, team):
    return sorted(games, key=lambda game: not is_favorite(game, team))


def choose_game(games, team, previous=None):
    ordered = ordered_games(games, team)
    ids = [game["game_id"] for game in ordered]
    return previous if previous in ids else (ids[0] if ids else None)
