"""Public response models for the KBO Tracker API."""

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class GamesResponse(BaseModel):
    date: str
    games: list[dict[str, Any]]


class GameResponse(BaseModel):
    game: dict[str, Any]


class RelayResponse(BaseModel):
    game_id: str
    inning: int | None = None
    text_relays: list[dict[str, Any]]
    current_state: dict[str, Any]
    home_lineup: dict[str, Any]
    away_lineup: dict[str, Any]
    pitcher_vs_batter: str = ""


class HighlightsResponse(BaseModel):
    game_id: str
    highlights: list[dict[str, Any]]


class WinProbabilityResponse(BaseModel):
    game_id: str
    points: list[dict[str, Any]]


class DashboardResponse(BaseModel):
    game_id: str
    game: dict[str, Any]
    highlights: list[dict[str, Any]]
    points: list[dict[str, Any]]
    live_situation: dict[str, Any]


class SummaryResponse(BaseModel):
    game_id: str
    summary: dict[str, Any]


class StandingsResponse(BaseModel):
    season: int
    standings: list[dict[str, Any]]
    favorite_next_game: dict[str, Any] | None = None


class NextGameResponse(BaseModel):
    season: int
    team: str
    next_game: dict[str, Any] | None = Field(default=None)
