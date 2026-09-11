"""HTTP routes exposing the existing KBO tracker features."""

import asyncio
import re
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from game_summary import build_game_summary, is_game_finished
from highlight_events import extract_highlights
from live_situation import build_live_situation, relay_is_available
from standings import build_standings, normalize_team
from win_probability import extract_win_probabilities

from .naver import NaverSportsClient, get_naver_client
from .schemas import (
    DashboardResponse,
    GameResponse,
    GamesResponse,
    HealthResponse,
    HighlightsResponse,
    NextGameResponse,
    RelayResponse,
    StandingsResponse,
    SummaryResponse,
    WinProbabilityResponse,
)


router = APIRouter()
KST = timezone(timedelta(hours=9))


def _total_innings(game):
    away = game.get("awayTeamScoreByInning") or []
    home = game.get("homeTeamScoreByInning") or []
    total = max(len(away), len(home), 9)
    current = str(game.get("currentInning") or game.get("statusInfo") or "")
    match = re.search(r"(\d+)회", current)
    return max(total, int(match.group(1))) if match else total


def _team_names(game):
    return (
        game.get("homeTeamFullName") or game.get("homeTeamName") or "홈",
        game.get("awayTeamFullName") or game.get("awayTeamName") or "원정",
    )


def _standings_response(rows, team_stats):
    images = {
        normalize_team(team.get("teamName") or team.get("teamId")): team.get("teamImageUrl")
        for team in team_stats
    }
    return [{
        "favorite": row["응원"] == "⭐",
        "rank": row["순위"],
        "team": row["팀"],
        "team_image_url": images.get(row["팀"]),
        "games": row["경기"],
        "wins": row["승"],
        "draws": row["무"],
        "losses": row["패"],
        "win_rate": row["승률"],
        "recent_ten": row["최근 10경기"],
        "streak": row["연속"],
        "run_differential": row["득실차"],
        "first_place_gap": row["1위 차"],
        "fifth_place_gap": row["5위 차"],
    } for row in rows]


async def _game_and_relays(client, game_id):
    game = await client.game_detail(game_id)
    relays = [] if not relay_is_available(game) else await client.all_relays(game_id, _total_innings(game))
    return game, relays


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    return {"status": "ok", "service": "kbo-tracker-api"}


@router.get("/games", response_model=GamesResponse, tags=["games"])
async def games(
    target_date: date | None = Query(default=None, alias="date"),
    client: NaverSportsClient = Depends(get_naver_client),
):
    selected = target_date or datetime.now(KST).date()
    return {"date": selected.isoformat(), "games": await client.games_by_date(selected.isoformat())}


@router.get("/games/{game_id}", response_model=GameResponse, tags=["games"])
async def game_detail(game_id: str, client: NaverSportsClient = Depends(get_naver_client)):
    return {"game": await client.game_detail(game_id)}


@router.get("/games/{game_id}/relay", response_model=RelayResponse, tags=["games"])
async def game_relay(
    game_id: str,
    inning: int | None = Query(default=None, ge=1, le=20),
    client: NaverSportsClient = Depends(get_naver_client),
):
    relay = await client.relay(game_id, inning)
    return {"game_id": game_id, "inning": inning, **relay}


@router.get("/games/{game_id}/highlights", response_model=HighlightsResponse, tags=["analysis"])
async def game_highlights(game_id: str, client: NaverSportsClient = Depends(get_naver_client)):
    game, relays = await _game_and_relays(client, game_id)
    home, away = _team_names(game)
    return {"game_id": game_id, "highlights": extract_highlights(relays, home, away)}


@router.get("/games/{game_id}/win-probability", response_model=WinProbabilityResponse, tags=["analysis"])
async def game_win_probability(game_id: str, client: NaverSportsClient = Depends(get_naver_client)):
    game, relays = await _game_and_relays(client, game_id)
    home, away = _team_names(game)
    return {"game_id": game_id, "points": extract_win_probabilities(relays, home, away)}


@router.get("/games/{game_id}/dashboard", response_model=DashboardResponse, tags=["analysis"])
async def game_dashboard(game_id: str, client: NaverSportsClient = Depends(get_naver_client)):
    """Return the data needed by the live dashboard with one relay collection."""
    game = await client.game_detail(game_id)
    if relay_is_available(game):
        relays, latest = await asyncio.gather(
            client.all_relays(game_id, _total_innings(game)),
            client.relay(game_id),
        )
    else:
        relays = []
        latest = {}
    home, away = _team_names(game)
    return {
        "game_id": game_id,
        "game": game,
        "highlights": extract_highlights(relays, home, away),
        "points": extract_win_probabilities(relays, home, away),
        "live_situation": build_live_situation(game, latest),
    }


@router.get("/games/{game_id}/summary", response_model=SummaryResponse, tags=["analysis"])
async def game_summary(game_id: str, client: NaverSportsClient = Depends(get_naver_client)):
    game = await client.game_detail(game_id)
    if not is_game_finished(game):
        raise HTTPException(status_code=409, detail="경기가 종료된 후 요약을 확인할 수 있습니다.")
    relays, latest = await asyncio.gather(
        client.all_relays(game_id, _total_innings(game)),
        client.relay(game_id),
    )
    home, away = _team_names(game)
    summary = build_game_summary(
        game,
        relays,
        home,
        away,
        latest["home_lineup"],
        latest["away_lineup"],
    )
    return {"game_id": game_id, "summary": summary}


@router.get("/standings", response_model=StandingsResponse, tags=["standings"])
async def team_standings(
    season: int | None = Query(default=None, ge=2008, le=2100),
    favorite_team: str = Query(default="선택 안 함"),
    client: NaverSportsClient = Depends(get_naver_client),
):
    selected_season = season or datetime.now(KST).year
    teams, recent = await client.standings(selected_season)
    rows, next_game = build_standings(teams, recent, favorite_team)
    return {
        "season": selected_season,
        "standings": _standings_response(rows, teams),
        "favorite_next_game": next_game,
    }


@router.get("/teams/{team_name}/next-game", response_model=NextGameResponse, tags=["standings"])
async def next_game(
    team_name: str,
    season: int | None = Query(default=None, ge=2008, le=2100),
    client: NaverSportsClient = Depends(get_naver_client),
):
    selected_season = season or datetime.now(KST).year
    teams, recent = await client.standings(selected_season)
    normalized = normalize_team(team_name)
    if not any(normalize_team(team.get("teamName") or team.get("teamId")) == normalized for team in teams):
        raise HTTPException(status_code=404, detail="KBO 팀을 찾을 수 없습니다.")
    _, upcoming = build_standings(teams, recent, normalized)
    return {"season": selected_season, "team": normalized, "next_game": upcoming}
