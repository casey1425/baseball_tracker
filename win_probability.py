"""Transform relay plate appearances into win-probability data points."""


def extract_win_probabilities(all_text_relays, home_name="홈", away_name="원정"):
    sorted_relays = sorted(all_text_relays, key=lambda item: int(item.get("no", 0)))
    data_points = [{
        "step": 0,
        "inn_num": 0,
        "inning": "경기 시작",
        "event": "경기 시작 전 (50:50)",
        "home_win_rate": 50.0,
        "away_win_rate": 50.0,
        "wpa": 0.0,
        "score": "0 : 0",
        "is_major": False,
    }]

    seen_no = set()
    step = 1
    for at_bat in sorted_relays:
        no = at_bat.get("no")
        if no in seen_no:
            continue
        seen_no.add(no)

        metric = at_bat.get("metricOption") or {}
        home_rate = metric.get("homeTeamWinRate", 0.0)
        away_rate = metric.get("awayTeamWinRate", 0.0)
        wpa = metric.get("wpaByPlate", 0.0)
        if (home_rate == 0.0 and away_rate == 0.0) or (home_rate + away_rate == 0.0):
            continue

        title = (at_bat.get("title") or "").strip()
        if not title or "==" in title or "공격" in title or "종료" in title:
            continue

        inning = at_bat.get("inn", 1)
        half = "말" if str(at_bat.get("homeOrAway")) == "1" else "초"
        final_text = ""
        score = ""
        for option in reversed(at_bat.get("textOptions") or []):
            text = (option.get("text") or "").strip()
            if not text or "==" in text or "공격" in text:
                continue
            final_text = text
            state = option.get("currentGameState") or {}
            home_score = state.get("homeScore")
            away_score = state.get("awayScore")
            if home_score is not None and away_score is not None:
                score = f"{away_name} {away_score} : {home_score} {home_name}"
            break

        event = f"{title} ➔ {final_text}" if final_text and final_text != title else title
        is_major = abs(wpa) >= 10.0 or any(
            keyword in final_text
            for keyword in ("홈런", "적시타", "역전", "끝내기", "밀어내기", "희생플라이")
        )
        data_points.append({
            "step": step,
            "inn_num": int(inning) if str(inning).isdigit() else 1,
            "inning": f"{inning}회{half}",
            "event": event,
            "home_win_rate": float(home_rate),
            "away_win_rate": float(away_rate),
            "wpa": float(wpa),
            "score": score,
            "is_major": is_major,
        })
        step += 1

    return data_points
