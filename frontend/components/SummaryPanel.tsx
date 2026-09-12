import type { GameSummary } from "@/types/baseball";

export function SummaryPanel({ summary }: { summary: GameSummary }) {
  return (
    <article className="panel summary-panel">
      <div className="summary-hero"><span>FINAL REPORT</span><h2>{summary.headline}</h2><p>{summary.final_score}</p></div>
      <div className="summary-stats"><div><span>WINNER</span><b>{summary.winner}</b></div><div><span>리드 교체</span><b>{summary.lead_changes}회</b></div><div><span>최대 점수 차</span><b>{summary.largest_lead}점</b></div></div>
      {summary.mvp_candidate && <div className="mvp-card"><span>★ MVP CANDIDATE</span><strong>{summary.mvp_candidate}</strong></div>}
      {summary.decisive_event && <div className="decisive-card"><span>결정적 장면</span><b>{summary.decisive_event.inning}</b><strong>{summary.decisive_event.description}</strong><small>WPA {summary.decisive_event.wpa > 0 ? "+" : ""}{summary.decisive_event.wpa.toFixed(1)}% · {summary.decisive_event.score}</small></div>}
      <div className="summary-events"><h3>주요 승부처 TOP {summary.key_events.length}</h3>{summary.key_events.map((event, index) => <div key={`${event.order}-${index}`}><b>{index + 1}</b><span><small>{event.inning}</small><strong>{event.description}</strong></span><em>{event.wpa > 0 ? "+" : ""}{event.wpa.toFixed(1)}%</em></div>)}</div>
    </article>
  );
}
