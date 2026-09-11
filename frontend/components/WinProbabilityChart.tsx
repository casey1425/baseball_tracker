"use client";

import { useState, type PointerEvent } from "react";
import type { WinProbabilityPoint } from "@/types/baseball";

interface Props {
  points: WinProbabilityPoint[];
  homeTeam: string;
  awayTeam: string;
}

export function WinProbabilityChart({ points, homeTeam, awayTeam }: Props) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

  if (points.length < 2) {
    return <div className="empty-chart">승리 확률 데이터가 아직 없습니다.</div>;
  }

  const width = 900;
  const height = 280;
  const padX = 26;
  const padY = 22;
  const usableWidth = width - padX * 2;
  const usableHeight = height - padY * 2;
  const x = (index: number) => padX + (index / Math.max(points.length - 1, 1)) * usableWidth;
  const y = (value: number) => padY + ((100 - value) / 100) * usableHeight;
  const homeLine = points.map((point, index) => `${x(index)},${y(point.home_win_rate)}`).join(" ");
  const major = points.map((point, index) => ({ point, index })).filter(({ point }) => point.is_major);
  const latest = points.at(-1)!;
  const hovered = hoveredIndex === null ? null : points[hoveredIndex];
  const hoveredX = hoveredIndex === null ? 0 : x(hoveredIndex);
  const hoveredY = hovered ? y(hovered.home_win_rate) : 0;
  const tooltipPosition = hoveredIndex === null ? 0 : (hoveredX / width) * 100;
  const tooltipEdge = tooltipPosition < 18 ? "left" : tooltipPosition > 82 ? "right" : "center";

  function selectNearestPoint(event: PointerEvent<SVGSVGElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    const svgX = ((event.clientX - rect.left) / rect.width) * width;
    const ratio = Math.max(0, Math.min(1, (svgX - padX) / usableWidth));
    setHoveredIndex(Math.round(ratio * (points.length - 1)));
  }

  return (
    <div>
      <div className="chart-legend">
        <span><i className="legend-dot home" />{homeTeam} {latest.home_win_rate.toFixed(1)}%</span>
        <span><i className="legend-dot away" />{awayTeam} {latest.away_win_rate.toFixed(1)}%</span>
      </div>
      <div className="chart-wrap">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="홈팀 승리 확률 변화"
          onPointerMove={selectNearestPoint}
          onPointerDown={selectNearestPoint}
          onPointerLeave={() => setHoveredIndex(null)}
        >
          {[0, 25, 50, 75, 100].map((value) => (
            <g key={value}>
              <line x1={padX} x2={width - padX} y1={y(value)} y2={y(value)} className={value === 50 ? "mid-grid" : "chart-grid"} />
              <text x={padX + 4} y={y(value) - 5} className="axis-label">{value}%</text>
            </g>
          ))}
          <defs>
            <linearGradient id="probabilityFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#ffcf4a" stopOpacity="0.28" />
              <stop offset="1" stopColor="#ffcf4a" stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon points={`${padX},${y(0)} ${homeLine} ${width - padX},${y(0)}`} fill="url(#probabilityFill)" />
          <polyline points={homeLine} className="probability-line" />
          {major.map(({ point, index }) => (
            <circle key={`${point.step}-${index}`} cx={x(index)} cy={y(point.home_win_rate)} r="5" className="major-point">
              <title>{`${point.inning} · ${point.event} · ${point.home_win_rate.toFixed(1)}%`}</title>
            </circle>
          ))}
          {hovered && (
            <g className="hover-guide">
              <line x1={hoveredX} x2={hoveredX} y1={padY} y2={height - padY} />
              <circle cx={hoveredX} cy={hoveredY} r="6" />
            </g>
          )}
        </svg>
        {hovered && (
          <div
            className={`chart-tooltip ${tooltipEdge}`}
            style={{ left: `${tooltipPosition}%`, top: `${(hoveredY / height) * 100}%` }}
            role="status"
          >
            <div className="tooltip-top"><b>{hovered.inning}</b><span>{hovered.score || "경기 시작"}</span></div>
            <strong>{hovered.event}</strong>
            <div className="tooltip-probabilities">
              <span><i className="home" />{homeTeam}<b>{hovered.home_win_rate.toFixed(1)}%</b></span>
              <span><i className="away" />{awayTeam}<b>{hovered.away_win_rate.toFixed(1)}%</b></span>
            </div>
            <small>WPA {hovered.wpa > 0 ? "+" : ""}{hovered.wpa.toFixed(1)}%</small>
          </div>
        )}
      </div>
    </div>
  );
}
