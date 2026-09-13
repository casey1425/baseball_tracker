import type {
  Boxscore,
  GameDetail,
  GameSummary,
  GameListItem,
  Highlight,
  LiveSituation,
  RelayEntry,
  Standing,
  WinProbabilityPoint,
} from "@/types/baseball";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL || "/api/kbo").replace(/\/$/, "");

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store", signal });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `API 요청에 실패했습니다. (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function fetchGames(date: string, signal?: AbortSignal) {
  return request<{ date: string; games: GameListItem[] }>(`/games?date=${date}`, signal);
}

export async function fetchGameBundle(gameId: string, signal?: AbortSignal) {
  const encoded = encodeURIComponent(gameId);
  const dashboard = await request<{
    game: GameDetail;
    highlights: Highlight[];
    points: WinProbabilityPoint[];
    live_situation: LiveSituation;
    relay_entries: RelayEntry[];
    boxscore: Boxscore;
    summary: GameSummary | null;
  }>(`/games/${encoded}/dashboard`, signal);
  return {
    detail: dashboard.game,
    highlights: dashboard.highlights,
    points: dashboard.points,
    liveSituation: dashboard.live_situation,
    relayEntries: dashboard.relay_entries,
    boxscore: dashboard.boxscore,
    summary: dashboard.summary,
  };
}

export async function fetchStandings(favoriteTeam: string, season: string, signal?: AbortSignal) {
  const query = new URLSearchParams();
  if (favoriteTeam) query.set("favorite_team", favoriteTeam);
  if (season) query.set("season", season);
  return request<{ standings: Standing[] }>(`/standings?${query.toString()}`, signal);
}
