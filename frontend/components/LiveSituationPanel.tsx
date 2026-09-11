import type { LiveSituation } from "@/types/baseball";

function CountDots({ value, total, tone }: { value: number; total: number; tone: string }) {
  return (
    <span className="count-dots">
      {Array.from({ length: total }, (_, index) => (
        <i key={index} className={index < value ? "on" : ""} style={{ "--dot-color": tone } as React.CSSProperties} />
      ))}
    </span>
  );
}

function resultTone(code: string) {
  if (code === "B") return "ball";
  if (["S", "T", "F"].includes(code)) return "strike";
  return "play";
}

export function LiveSituationPanel({ situation }: { situation: LiveSituation | null }) {
  if (!situation || !situation.available) {
    return (
      <article className="panel live-panel unavailable">
        <div className="panel-title"><div><span>LIVE AT BAT</span><h2>실시간 타석 상황</h2></div></div>
        <div className="live-empty"><b>경기 전</b><p>{situation?.message ?? "중계 정보를 불러오는 중입니다."}</p></div>
      </article>
    );
  }

  const count = situation.count ?? { balls: 0, strikes: 0, outs: 0 };
  const bases = situation.bases ?? { first: false, second: false, third: false };
  const pitches = situation.recent_pitches ?? [];

  return (
    <article className="panel live-panel">
      <div className="panel-title live-title">
        <div><span>LIVE AT BAT</span><h2>실시간 타석 상황</h2></div>
        <div className={`at-bat-status ${situation.phase}`}><i />{situation.message}</div>
      </div>

      <div className="situation-meta">
        <b>{situation.inning}</b><span>{situation.offense_team} 공격</span>
        {situation.matchup && <small>{situation.matchup}</small>}
      </div>

      <div className="live-situation-grid">
        <div className="matchup-players">
          <div className="player-card"><span>PITCHER</span><strong>{situation.pitcher?.name ?? "-"}</strong></div>
          <i>VS</i>
          <div className="player-card batter"><span>BATTER</span><strong>{situation.batter?.name ?? "-"}</strong></div>
        </div>

        <div className="diamond-and-count">
          <div className="base-diamond" aria-label={`주자 상황: 1루 ${bases.first ? "있음" : "없음"}, 2루 ${bases.second ? "있음" : "없음"}, 3루 ${bases.third ? "있음" : "없음"}`}>
            <i className={`base second ${bases.second ? "occupied" : ""}`} />
            <i className={`base third ${bases.third ? "occupied" : ""}`} />
            <i className={`base first ${bases.first ? "occupied" : ""}`} />
            <i className="home-plate" />
            <span className="base-line left" /><span className="base-line right" />
          </div>
          <div className="count-board">
            <div><b>B</b><CountDots value={count.balls} total={3} tone="#4bd38a" /></div>
            <div><b>S</b><CountDots value={count.strikes} total={2} tone="#ffcf4a" /></div>
            <div><b>O</b><CountDots value={count.outs} total={2} tone="#ff6b61" /></div>
          </div>
        </div>

        <div className="recent-pitches">
          <div className="recent-pitches-title"><b>최근 투구</b><span>최근 {pitches.length}구</span></div>
          {pitches.length ? [...pitches].reverse().map((pitch) => (
            <div className="pitch-row" key={`${pitch.number}-${pitch.text}`}>
              <b>{pitch.number}</b>
              <span>{pitch.pitch_type}</span>
              <em>{pitch.speed ? `${pitch.speed} km/h` : "-"}</em>
              <small className={resultTone(pitch.result_code)}>{pitch.text.replace(/^\d+구\s*/, "")}</small>
            </div>
          )) : <p className="no-pitches">아직 기록된 투구가 없습니다.</p>}
        </div>
      </div>

      {situation.last_result && <div className="last-play"><span>LAST PLAY</span><strong>{situation.last_result}</strong></div>}
    </article>
  );
}
