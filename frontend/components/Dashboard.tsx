"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchGameBundle, fetchGames, fetchStandings } from "@/lib/api";
import type { GameDetail, GameListItem, Highlight, LiveSituation, Standing, WinProbabilityPoint } from "@/types/baseball";
import { LiveSituationPanel } from "./LiveSituationPanel";
import { WinProbabilityChart } from "./WinProbabilityChart";

const KBO_TEAMS = ["LG", "한화", "SSG", "삼성", "NC", "KT", "롯데", "KIA", "두산", "키움"];
const FILTERS = ["전체", "홈런", "득점", "안타/장타", "선수교체", "승부처", "삼진", "경기결과"];
const POLL_INTERVAL = 10_000;

function kstDate() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
}

function shiftDate(value: string, days: number) {
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day + days));
  return date.toISOString().slice(0, 10);
}

function readableDate(value: string) {
  return new Intl.DateTimeFormat("ko-KR", {
    timeZone: "UTC",
    month: "long",
    day: "numeric",
    weekday: "short",
  }).format(new Date(`${value}T00:00:00Z`));
}

function isFinished(code?: string) {
  return ["RESULT", "ENDED", "FINAL"].includes((code ?? "").toUpperCase());
}

function isLive(game: GameListItem) {
  const code = game.status_code.toUpperCase();
  return !game.cancel && !isFinished(code) && !["BEFORE", "READY", "SCHEDULED"].includes(code);
}

function statusLabel(game: GameListItem) {
  if (game.cancel) return "취소";
  if (isFinished(game.status_code)) return "종료";
  return game.status || "예정";
}

function TeamMark({ name, imageUrl }: { name: string; imageUrl?: string }) {
  const [imageFailed, setImageFailed] = useState(false);

  useEffect(() => setImageFailed(false), [imageUrl]);

  if (imageUrl && !imageFailed) {
    const proxiedUrl = `/api/team-logo?url=${encodeURIComponent(imageUrl)}`;
    return <img className="team-mark" src={proxiedUrl} alt={`${name} 엠블럼`} onError={() => setImageFailed(true)} />;
  }
  return <span className="team-mark fallback">{name.slice(0, 1)}</span>;
}

function GameCard({ game, selected, favorite, onClick }: {
  game: GameListItem;
  selected: boolean;
  favorite: string;
  onClick: () => void;
}) {
  return (
    <button className={`game-card ${selected ? "selected" : ""} ${favorite && [game.home, game.away].includes(favorite) ? "favorite" : ""}`} onClick={onClick}>
      <div className="game-card-top">
        <span className={`status-pill ${isLive(game) ? "live" : ""}`}>{isLive(game) && <i />} {statusLabel(game)}</span>
        <span>{game.venue}</span>
      </div>
      <div className="matchup">
        <div><strong>{game.away}</strong><b>{game.away_score}</b></div>
        <span>:</span>
        <div><b>{game.home_score}</b><strong>{game.home}</strong></div>
      </div>
    </button>
  );
}

function LineScore({ detail }: { detail: GameDetail }) {
  const away = detail.awayTeamScoreByInning ?? [];
  const home = detail.homeTeamScoreByInning ?? [];
  const innings = Math.max(away.length, home.length, 9);
  return (
    <div className="line-score-scroll">
      <table className="line-score">
        <thead><tr><th>TEAM</th>{Array.from({ length: innings }, (_, i) => <th key={i}>{i + 1}</th>)}<th>R</th></tr></thead>
        <tbody>
          <tr><td>{detail.awayTeamName}</td>{Array.from({ length: innings }, (_, i) => <td key={i}>{away[i] ?? "-"}</td>)}<td>{detail.awayTeamScore ?? 0}</td></tr>
          <tr><td>{detail.homeTeamName}</td>{Array.from({ length: innings }, (_, i) => <td key={i}>{home[i] ?? "-"}</td>)}<td>{detail.homeTeamScore ?? 0}</td></tr>
        </tbody>
      </table>
    </div>
  );
}

function Standings({ rows, favorite }: { rows: Standing[]; favorite: string }) {
  return (
    <div className="standings-list">
      {rows.map((row) => (
        <div className={`standing-row ${row.team === favorite ? "favorite" : ""}`} key={row.team}>
          <b>{row.rank}</b>
          <TeamMark name={row.team} imageUrl={row.team_image_url} />
          <strong>{row.team}</strong>
          <span>{row.wins}승 {row.draws}무 {row.losses}패</span>
          <em>{row.win_rate}</em>
          <small>{row.streak || row.recent_ten}</small>
        </div>
      ))}
    </div>
  );
}

export function Dashboard() {
  const [date, setDate] = useState("");
  const [games, setGames] = useState<GameListItem[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [detail, setDetail] = useState<GameDetail | null>(null);
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [points, setPoints] = useState<WinProbabilityPoint[]>([]);
  const [liveSituation, setLiveSituation] = useState<LiveSituation | null>(null);
  const [standings, setStandings] = useState<Standing[]>([]);
  const [favorite, setFavorite] = useState("");
  const [filter, setFilter] = useState("전체");
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  useEffect(() => {
    setDate(kstDate());
    setFavorite(localStorage.getItem("kbo-favorite-team") ?? "");
  }, []);

  const loadGames = useCallback(async (signal?: AbortSignal, silent = false) => {
    if (!date) return;
    if (!silent) setLoading(true);
    try {
      const result = await fetchGames(date, signal);
      setGames(result.games);
      setSelectedId((current) => {
        if (result.games.some((game) => game.game_id === current)) return current;
        const preferred = result.games.find((game) => favorite && [game.home, game.away].includes(favorite));
        return preferred?.game_id ?? result.games[0]?.game_id ?? "";
      });
      setError("");
      setUpdatedAt(new Date());
    } catch (err) {
      if ((err as Error).name !== "AbortError") setError((err as Error).message);
    } finally {
      if (!silent) setLoading(false);
    }
  }, [date, favorite]);

  const loadDetail = useCallback(async (signal?: AbortSignal, silent = false) => {
    if (!selectedId) {
      setDetail(null);
      setHighlights([]);
      setPoints([]);
      setLiveSituation(null);
      return;
    }
    if (!silent) setDetailLoading(true);
    try {
      const bundle = await fetchGameBundle(selectedId, signal);
      setDetail(bundle.detail);
      setHighlights(bundle.highlights);
      setPoints(bundle.points);
      setLiveSituation(bundle.liveSituation);
      setError("");
      setUpdatedAt(new Date());
    } catch (err) {
      if ((err as Error).name !== "AbortError") setError((err as Error).message);
    } finally {
      if (!silent) setDetailLoading(false);
    }
  }, [selectedId]);

  useEffect(() => {
    const controller = new AbortController();
    loadGames(controller.signal);
    return () => controller.abort();
  }, [loadGames]);

  useEffect(() => {
    const controller = new AbortController();
    loadDetail(controller.signal);
    return () => controller.abort();
  }, [loadDetail]);

  useEffect(() => {
    const controller = new AbortController();
    fetchStandings(favorite, date.slice(0, 4), controller.signal).then((data) => setStandings(data.standings)).catch(() => undefined);
    return () => controller.abort();
  }, [favorite, date]);

  useEffect(() => {
    if (!autoRefresh || !date) return;
    const timer = window.setInterval(() => {
      loadGames(undefined, true);
      loadDetail(undefined, true);
    }, POLL_INTERVAL);
    return () => window.clearInterval(timer);
  }, [autoRefresh, date, loadGames, loadDetail]);

  const filteredHighlights = useMemo(
    () => filter === "전체" ? highlights : highlights.filter((item) => item.event_type === filter),
    [filter, highlights],
  );
  const selectedGame = games.find((game) => game.game_id === selectedId);
  const homeName = detail?.homeTeamName ?? selectedGame?.home ?? "홈";
  const awayName = detail?.awayTeamName ?? selectedGame?.away ?? "원정";

  function updateFavorite(team: string) {
    setFavorite(team);
    if (team) localStorage.setItem("kbo-favorite-team", team);
    else localStorage.removeItem("kbo-favorite-team");
  }

  return (
    <main>
      <header className="topbar">
        <div className="brand"><span>⚾</span><div><b>KBO</b><strong>LIVE TRACKER</strong></div></div>
        <div className="header-actions">
          <label className="favorite-select"><span>응원팀</span><select value={favorite} onChange={(event) => updateFavorite(event.target.value)}><option value="">선택 안 함</option>{KBO_TEAMS.map((team) => <option key={team}>{team}</option>)}</select></label>
          <button className={`refresh-toggle ${autoRefresh ? "active" : ""}`} onClick={() => setAutoRefresh((value) => !value)}><i /> 실시간 {autoRefresh ? "ON" : "OFF"}</button>
        </div>
      </header>

      <section className="hero">
        <div><span className="eyebrow">TODAY&apos;S GAMES</span><h1>오늘의 KBO를<br /><em>한눈에.</em></h1><p>모든 경기의 흐름과 승부처를 실시간으로 확인하세요.</p></div>
        <div className="date-control"><button onClick={() => setDate((value) => shiftDate(value, -1))} aria-label="이전 날짜">←</button><button className="date-main" onClick={() => setDate(kstDate())}><b>{date ? readableDate(date) : "날짜 불러오는 중"}</b><span>{date}</span></button><button onClick={() => setDate((value) => shiftDate(value, 1))} aria-label="다음 날짜">→</button></div>
      </section>

      {error && <div className="error-banner"><b>데이터를 불러오지 못했습니다.</b><span>{error}</span><button onClick={() => { loadGames(); loadDetail(); }}>다시 시도</button></div>}

      <section className="games-section">
        <div className="section-heading"><div><span>GAMES</span><h2>전체 경기</h2></div><small>{updatedAt ? `마지막 갱신 ${updatedAt.toLocaleTimeString("ko-KR", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}` : ""}</small></div>
        <div className="game-grid">
          {loading ? Array.from({ length: 5 }, (_, index) => <div className="game-card skeleton" key={index} />) : games.length ? games.map((game) => <GameCard key={game.game_id} game={game} selected={selectedId === game.game_id} favorite={favorite} onClick={() => setSelectedId(game.game_id)} />) : <div className="empty-state">이 날짜에는 예정된 경기가 없습니다.</div>}
        </div>
      </section>

      {selectedId && (
        <div className="dashboard-grid">
          <section className="main-column">
            <article className="panel scoreboard-panel">
              {detailLoading && !detail ? <div className="panel-loading">경기 정보를 불러오는 중입니다.</div> : detail && <>
                <div className="score-meta"><span>{detail.stadium ?? selectedGame?.venue}</span><b>{detail.statusInfo ?? selectedGame?.status}</b></div>
                <div className="big-score">
                  <div><TeamMark name={awayName} imageUrl={detail.awayTeamEmblemUrl} /><span><small>AWAY</small><strong>{awayName}</strong></span><b>{detail.awayTeamScore ?? 0}</b></div>
                  <i>:</i>
                  <div><b>{detail.homeTeamScore ?? 0}</b><span><small>HOME</small><strong>{homeName}</strong></span><TeamMark name={homeName} imageUrl={detail.homeTeamEmblemUrl} /></div>
                </div>
                <LineScore detail={detail} />
              </>}
            </article>

            <LiveSituationPanel situation={liveSituation} />

            <article className="panel chart-panel">
              <div className="panel-title"><div><span>WIN PROBABILITY</span><h2>승리 확률</h2></div><small>★ 주요 승부처</small></div>
              <WinProbabilityChart points={points} homeTeam={homeName} awayTeam={awayName} />
            </article>

            <article className="panel highlights-panel">
              <div className="panel-title"><div><span>PLAY BY PLAY</span><h2>주요 장면</h2></div><small>{filteredHighlights.length}개 이벤트</small></div>
              <div className="filters">{FILTERS.map((name) => <button key={name} className={filter === name ? "active" : ""} onClick={() => setFilter(name)}>{name}</button>)}</div>
              <div className="timeline">
                {filteredHighlights.length ? [...filteredHighlights].reverse().slice(0, 30).map((item, index) => (
                  <div className="event" key={`${item.seqno ?? index}-${item.text}`} style={{ "--event-color": item.color } as React.CSSProperties}>
                    <div className="event-icon">{item.icon}</div>
                    <div><span>{item.inning} · {item.event_type}</span><strong>{item.text}</strong></div>
                    <small>{item.score}</small>
                  </div>
                )) : <div className="empty-state compact">선택한 조건의 주요 장면이 없습니다.</div>}
              </div>
            </article>
          </section>

          <aside className="side-column">
            <article className="panel standings-panel">
              <div className="panel-title"><div><span>{date.slice(0, 4)} SEASON</span><h2>팀 순위</h2></div></div>
              {standings.length ? <Standings rows={standings} favorite={favorite} /> : <div className="empty-state compact">순위를 불러오는 중입니다.</div>}
            </article>
            <article className="info-card"><span>LIVE UPDATE</span><strong>10초마다<br />새로운 경기 상황을<br />확인합니다.</strong><p>상단 버튼으로 자동 갱신을 켜거나 끌 수 있습니다.</p></article>
          </aside>
        </div>
      )}
      <footer>DATA PROVIDED BY NAVER SPORTS · KBO LIVE TRACKER</footer>
    </main>
  );
}
