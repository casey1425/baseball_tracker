"use client";

import { useEffect, useMemo, useRef, useState } from "react";

const WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"];

function parseDate(value: string) {
  const [year, month, day] = value.split("-").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
}

function isoDate(date: Date) {
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

function kstDate() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date());
}

export function DatePicker({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const [open, setOpen] = useState(false);
  const [month, setMonth] = useState(() => new Date());
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (value) {
      const selected = parseDate(value);
      setMonth(new Date(Date.UTC(selected.getUTCFullYear(), selected.getUTCMonth(), 1)));
    }
  }, [value]);

  useEffect(() => {
    function closeOnOutside(event: PointerEvent) {
      if (!containerRef.current?.contains(event.target as Node)) setOpen(false);
    }
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", closeOnOutside);
    document.addEventListener("keydown", closeOnEscape);
    return () => {
      document.removeEventListener("pointerdown", closeOnOutside);
      document.removeEventListener("keydown", closeOnEscape);
    };
  }, []);

  const dates = useMemo(() => {
    const first = new Date(Date.UTC(month.getUTCFullYear(), month.getUTCMonth(), 1));
    const gridStart = new Date(first);
    gridStart.setUTCDate(1 - first.getUTCDay());
    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(gridStart);
      date.setUTCDate(gridStart.getUTCDate() + index);
      return date;
    });
  }, [month]);
  const today = kstDate();

  function shiftMonth(offset: number) {
    setMonth((current) => new Date(Date.UTC(current.getUTCFullYear(), current.getUTCMonth() + offset, 1)));
  }

  return (
    <div className="date-picker" ref={containerRef}>
      <button className="date-main" type="button" aria-haspopup="dialog" aria-expanded={open} onClick={() => setOpen((current) => !current)}>
        <b>{value ? readableDate(value) : "날짜 불러오는 중"}</b>
        <span>{value}<i>달력</i></span>
      </button>
      {open && (
        <div className="calendar-popover" role="dialog" aria-label="날짜 선택 달력">
          <div className="calendar-header">
            <button type="button" aria-label="이전 달" onClick={() => shiftMonth(-1)}>←</button>
            <strong>{month.getUTCFullYear()}년 {month.getUTCMonth() + 1}월</strong>
            <button type="button" aria-label="다음 달" onClick={() => shiftMonth(1)}>→</button>
          </div>
          <div className="calendar-weekdays">{WEEKDAYS.map((day) => <span key={day}>{day}</span>)}</div>
          <div className="calendar-days">
            {dates.map((date) => {
              const dateValue = isoDate(date);
              const outside = date.getUTCMonth() !== month.getUTCMonth();
              return (
                <button
                  type="button"
                  key={dateValue}
                  className={`${outside ? "outside" : ""} ${dateValue === value ? "selected" : ""} ${dateValue === today ? "today" : ""}`}
                  aria-label={dateValue}
                  aria-pressed={dateValue === value}
                  onClick={() => { onChange(dateValue); setOpen(false); }}
                >
                  {date.getUTCDate()}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
