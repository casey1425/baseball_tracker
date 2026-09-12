"use client";

import { useState } from "react";
import type { Boxscore } from "@/types/baseball";

function average(value: number) {
  return value ? value.toFixed(3).replace(/^0/, "") : ".000";
}

export function BoxscorePanel({ boxscore }: { boxscore: Boxscore | null }) {
  const [side, setSide] = useState<"away" | "home">("away");
  if (!boxscore) return <article className="panel"><div className="empty-state compact">선수 기록을 불러오는 중입니다.</div></article>;
  const team = boxscore[side];

  return (
    <article className="panel boxscore-panel">
      <div className="panel-title"><div><span>PLAYER STATS</span><h2>선수 기록</h2></div></div>
      <div className="team-switch">
        <button className={side === "away" ? "active" : ""} onClick={() => setSide("away")}>{boxscore.away.team}</button>
        <button className={side === "home" ? "active" : ""} onClick={() => setSide("home")}>{boxscore.home.team}</button>
      </div>
      <h3>타자 기록</h3>
      <div className="stats-table-wrap"><table className="stats-table"><thead><tr><th>타순</th><th>선수</th><th>포지션</th><th>타수</th><th>안타</th><th>홈런</th><th>타점</th><th>득점</th><th>사사구</th><th>삼진</th><th>시즌 AVG</th></tr></thead><tbody>{team.batters.map((player, index) => <tr key={`${player.name}-${index}`}><td>{player.substitute ? "↳" : player.order || "-"}</td><td><b>{player.name}</b></td><td>{player.position}</td><td>{player.at_bats}</td><td>{player.hits}</td><td>{player.home_runs}</td><td>{player.rbi}</td><td>{player.runs}</td><td>{player.walks}</td><td>{player.strikeouts}</td><td>{average(player.season_average)}</td></tr>)}</tbody></table></div>
      {!team.batters.length && <div className="empty-state compact">타자 기록이 아직 없습니다.</div>}
      <h3>투수 기록</h3>
      <div className="stats-table-wrap"><table className="stats-table"><thead><tr><th>선수</th><th>이닝</th><th>투구</th><th>피안타</th><th>피홈런</th><th>사사구</th><th>삼진</th><th>실점</th><th>자책</th><th>시즌 ERA</th></tr></thead><tbody>{team.pitchers.map((player, index) => <tr key={`${player.name}-${index}`}><td><b>{player.name}</b></td><td>{player.innings}</td><td>{player.pitch_count}</td><td>{player.hits}</td><td>{player.home_runs}</td><td>{player.walks}</td><td>{player.strikeouts}</td><td>{player.runs}</td><td>{player.earned_runs}</td><td>{player.season_era}</td></tr>)}</tbody></table></div>
      {!team.pitchers.length && <div className="empty-state compact">투수 기록이 아직 없습니다.</div>}
    </article>
  );
}
