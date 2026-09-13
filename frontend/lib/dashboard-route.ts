export const GAME_TAB_KEYS = ["overview", "replay", "relay", "analysis", "players", "summary"] as const;

export type GameTab = (typeof GAME_TAB_KEYS)[number];

export function isGameTab(value: unknown): value is GameTab {
  return typeof value === "string" && GAME_TAB_KEYS.includes(value as GameTab);
}

export function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const parsed = new Date(Date.UTC(year, month - 1, day));
  return parsed.toISOString().slice(0, 10) === value;
}

export function dateFromGameId(gameId: string) {
  const match = gameId.match(/^(\d{4})(\d{2})(\d{2})/);
  if (!match) return "";
  const value = `${match[1]}-${match[2]}-${match[3]}`;
  return isIsoDate(value) ? value : "";
}

export function dashboardPath(date: string, gameId: string, tab: GameTab) {
  const query = new URLSearchParams();
  if (date) query.set("date", date);
  if (gameId) query.set("tab", tab);
  const path = gameId ? `/games/${encodeURIComponent(gameId)}` : "/";
  return query.size ? `${path}?${query.toString()}` : path;
}
