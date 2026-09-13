"use client";

import { useEffect, useMemo, useState } from "react";
import type { WinProbabilityPoint } from "@/types/baseball";

const SPEEDS = [
  { label: "0.75×", delay: 1800 },
  { label: "1×", delay: 1100 },
  { label: "1.5×", delay: 700 },
  { label: "2×", delay: 400 },
];

function ReplayChart({ points, activeIndex }: { points: WinProbabilityPoint[]; activeIndex: number }) {
  const width = 900;
  const height = 190;
  const padX = 18;
  const padY = 15;
  const usableWidth = width - padX * 2;
  const usableHeight = height - padY * 2;
  const x = (index: number) => padX + (index / Math.max(points.length - 1, 1)) * usableWidth;
  const y = (value: number) => padY + ((100 - value) / 100) * usableHeight;
  const coordinates = points.map((point, index) => `${x(index)},${y(point.home_win_rate)}`);
  const current = points[activeIndex];

  return (
    <div className="replay-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`현재 ${current.inning}, 홈팀 승리 확률 ${current.home_win_rate.toFixed(1)}%`}>
        {[25, 50, 75].map((value) => <line key={value} x1={padX} x2={width - padX} y1={y(value)} y2={y(value)} className={value === 50 ? "mid-grid" : "chart-grid"} />)}
        <polyline points={coordinates.join(" ")} className="replay-line-background" />
        <polyline points={coordinates.slice(0, activeIndex + 1).join(" ")} className="replay-line-active" />
        {points.map((point, index) => point.is_major && <circle key={`${point.step}-${index}`} cx={x(index)} cy={y(point.home_win_rate)} r="4" className={index <= activeIndex ? "replay-major played" : "replay-major"} />)}
        <line x1={x(activeIndex)} x2={x(activeIndex)} y1={padY} y2={height - padY} className="replay-cursor" />
        <circle cx={x(activeIndex)} cy={y(current.home_win_rate)} r="7" className="replay-current" />
      </svg>
    </div>
  );
}

export function ReplayPanel({ points, homeTeam, awayTeam }: {
  points: WinProbabilityPoint[];
  homeTeam: string;
  awayTeam: string;
}) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [delay, setDelay] = useState(SPEEDS[1].delay);
  const lastIndex = Math.max(points.length - 1, 0);
  const current = points[activeIndex];
  const keyMoments = useMemo(
    () => points.map((point, index) => ({ point, index })).filter(({ point }) => point.is_major),
    [points],
  );

  useEffect(() => {
    setActiveIndex((index) => Math.min(index, lastIndex));
  }, [lastIndex]);

  useEffect(() => {
    if (!playing) return;
    if (activeIndex >= lastIndex) {
      setPlaying(false);
      return;
    }
    const timer = window.setTimeout(() => setActiveIndex((index) => Math.min(index + 1, lastIndex)), delay);
    return () => window.clearTimeout(timer);
  }, [activeIndex, delay, lastIndex, playing]);

  if (points.length < 2 || !current) {
    return <article className="panel"><div className="empty-state compact">다시보기 데이터가 아직 없습니다.</div></article>;
  }

  function togglePlayback() {
    if (!playing && activeIndex >= lastIndex) setActiveIndex(0);
    setPlaying((value) => !value);
  }

  function moveTo(index: number) {
    setPlaying(false);
    setActiveIndex(Math.max(0, Math.min(index, lastIndex)));
  }

  return (
    <article className="panel replay-panel">
      <div className="panel-title replay-title">
        <div><span>GAME REPLAY</span><h2>경기 다시보기</h2></div>
        <small>{activeIndex === 0 ? "경기 시작" : `${activeIndex} / ${lastIndex} 타석`}</small>
      </div>

      <div className="replay-stage">
        <div className="replay-scoreline"><span>{current.inning}</span><strong>{current.score || `${awayTeam} 0 : 0 ${homeTeam}`}</strong></div>
        <h3>{current.event}</h3>
        <div className="replay-probabilities">
          <div><span>{awayTeam}</span><b>{current.away_win_rate.toFixed(1)}%</b><i style={{ width: `${current.away_win_rate}%` }} /></div>
          <div className="home"><span>{homeTeam}</span><b>{current.home_win_rate.toFixed(1)}%</b><i style={{ width: `${current.home_win_rate}%` }} /></div>
        </div>
        <div className={`replay-wpa ${current.wpa > 0 ? "positive" : current.wpa < 0 ? "negative" : ""}`}>WPA {current.wpa > 0 ? "+" : ""}{current.wpa.toFixed(1)}%</div>
      </div>

      <ReplayChart points={points} activeIndex={activeIndex} />

      <input
        className="replay-range"
        type="range"
        min="0"
        max={lastIndex}
        value={activeIndex}
        aria-label="타석 위치"
        onChange={(event) => moveTo(Number(event.target.value))}
        style={{ "--replay-progress": `${(activeIndex / lastIndex) * 100}%` } as React.CSSProperties}
      />

      <div className="replay-controls">
        <button type="button" onClick={() => moveTo(activeIndex - 1)} disabled={activeIndex === 0}>← 이전 타석</button>
        <button type="button" className="play-button" onClick={togglePlayback}>{playing ? "Ⅱ 일시정지" : activeIndex >= lastIndex ? "↻ 처음부터" : "▶ 자동 재생"}</button>
        <button type="button" onClick={() => moveTo(activeIndex + 1)} disabled={activeIndex >= lastIndex}>다음 타석 →</button>
        <label>재생 속도<select value={delay} onChange={(event) => setDelay(Number(event.target.value))}>{SPEEDS.map((speed) => <option value={speed.delay} key={speed.delay}>{speed.label}</option>)}</select></label>
      </div>

      {keyMoments.length > 0 && (
        <div className="replay-moments">
          <h3>주요 장면 바로가기</h3>
          <div>{keyMoments.map(({ point, index }) => <button type="button" className={index === activeIndex ? "active" : ""} key={`${point.step}-${index}`} onClick={() => moveTo(index)}><span>★ {point.inning}</span><strong>{point.event}</strong><small>{point.wpa > 0 ? "+" : ""}{point.wpa.toFixed(1)}%</small></button>)}</div>
        </div>
      )}
    </article>
  );
}
