"use client";

import { useMemo, useState } from "react";
import type { RelayEntry } from "@/types/baseball";

const RESULT_FILTERS = ["전체 결과", "홈런", "안타·장타", "득점", "삼진", "볼넷·사구", "아웃", "선수 교체"];

export function RelayPanel({ entries }: { entries: RelayEntry[] }) {
  const [query, setQuery] = useState("");
  const [inning, setInning] = useState("전체 이닝");
  const [resultType, setResultType] = useState("전체 결과");
  const innings = useMemo(
    () => [...new Set(entries.map((entry) => entry.inning_number))].sort((a, b) => Number(a) - Number(b)),
    [entries],
  );
  const filtered = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase("ko-KR");
    return entries.filter((entry) => {
      const matchesQuery = !normalized || `${entry.title} ${entry.result} ${entry.pitches.map((pitch) => pitch.text).join(" ")}`.toLocaleLowerCase("ko-KR").includes(normalized);
      const matchesInning = inning === "전체 이닝" || entry.inning_number === inning;
      const matchesResult = resultType === "전체 결과" || entry.categories.includes(resultType);
      return matchesQuery && matchesInning && matchesResult;
    });
  }, [entries, inning, query, resultType]);

  return (
    <article className="panel relay-panel">
      <div className="panel-title"><div><span>FULL PLAY BY PLAY</span><h2>상세 중계</h2></div><small>전체 {entries.length}개 중 {filtered.length}개</small></div>
      <div className="relay-controls">
        <label className="relay-search"><span>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="선수 이름이나 중계 내용 검색" /></label>
        <select aria-label="이닝 선택" value={inning} onChange={(event) => setInning(event.target.value)}><option>전체 이닝</option>{innings.map((value) => <option value={value} key={value}>{value}회</option>)}</select>
        <select aria-label="결과 선택" value={resultType} onChange={(event) => setResultType(event.target.value)}>{RESULT_FILTERS.map((value) => <option key={value}>{value}</option>)}</select>
      </div>
      <div className="relay-list">
        {filtered.length ? filtered.map((entry) => (
          <details className="relay-entry" key={entry.id}>
            <summary>
              <span className="relay-inning">{entry.inning}</span>
              <div><b>{entry.title}</b><strong>{entry.result}</strong></div>
              <small>{entry.score}</small><i>⌄</i>
            </summary>
            <div className="relay-pitches">
              {entry.pitches.length ? entry.pitches.map((pitch) => (
                <div key={`${entry.id}-${pitch.number}`}><b>{pitch.number}구</b><span>{pitch.pitch_type}</span><em>{pitch.speed ? `${pitch.speed} km/h` : "-"}</em><strong>{pitch.text.replace(/^\d+구\s*/, "")}</strong><small>B {pitch.ball} · S {pitch.strike} · O {pitch.out}</small></div>
              )) : <p>투구별 기록 없이 결과만 제공된 중계입니다.</p>}
            </div>
          </details>
        )) : <div className="empty-state compact">검색 조건에 맞는 중계가 없습니다.</div>}
      </div>
    </article>
  );
}
