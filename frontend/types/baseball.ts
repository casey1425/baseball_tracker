export interface GameListItem {
  game_id: string;
  home: string;
  away: string;
  home_score: number | string;
  away_score: number | string;
  status: string;
  status_code: string;
  venue: string;
  cancel: boolean;
}

export interface GameDetail {
  gameId?: string;
  gameDateTime?: string;
  homeTeamName?: string;
  awayTeamName?: string;
  homeTeamFullName?: string;
  awayTeamFullName?: string;
  homeTeamEmblemUrl?: string;
  awayTeamEmblemUrl?: string;
  homeTeamScore?: number | string;
  awayTeamScore?: number | string;
  homeTeamScoreByInning?: Array<number | string>;
  awayTeamScoreByInning?: Array<number | string>;
  homeTeamRheb?: Array<number | string> | Record<string, number | string>;
  awayTeamRheb?: Array<number | string> | Record<string, number | string>;
  statusInfo?: string;
  statusCode?: string;
  currentInning?: string;
  stadium?: string;
  homeStarterName?: string;
  awayStarterName?: string;
}

export interface Highlight {
  inning: string;
  event_type: string;
  icon: string;
  color: string;
  tag_bg: string;
  text: string;
  score: string;
  seqno?: number;
}

export interface WinProbabilityPoint {
  step: number;
  inning: string;
  event: string;
  home_win_rate: number;
  away_win_rate: number;
  wpa: number;
  score: string;
  is_major: boolean;
}

export interface LiveSituation {
  available: boolean;
  phase: "scheduled" | "live" | "final";
  message: string;
  inning?: string;
  offense_team?: string;
  pitcher?: { code: string; name: string };
  batter?: { code: string; name: string };
  count?: { balls: number; strikes: number; outs: number };
  bases?: { first: boolean; second: boolean; third: boolean };
  recent_pitches?: Array<{
    number: number;
    text: string;
    pitch_type: string;
    speed: string;
    result_code: string;
  }>;
  last_result?: string;
  matchup?: string;
}

export interface Standing {
  favorite: boolean;
  rank: number;
  team: string;
  team_image_url?: string;
  games: number;
  wins: number;
  draws: number;
  losses: number;
  win_rate: number | string;
  recent_ten: string;
  streak: string;
  run_differential: number;
  first_place_gap: number | string;
  fifth_place_gap: number | string;
}
