"""Build a compact post-game summary from game, relay, and lineup data."""


FINISHED_CODES = {"RESULT", "FINAL", "ENDED", "END"}


def _number(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _integer(value):
    return int(_number(value))


def is_game_finished(game_detail, game_summary=None):
    summary = game_summary or {}
    codes = (game_detail.get("statusCode"), summary.get("status_code"))
    statuses = (game_detail.get("statusInfo"), summary.get("status"))
    return any(str(code).upper() in FINISHED_CODES for code in codes if code) or any(
        "종료" in str(status) for status in statuses if status
    )


def _plate_events(text_relays, home_name, away_name):
    events = []
    seen = set()
    for entry in text_relays:
        no = entry.get("no")
        if no is not None and no in seen:
            continue
        if no is not None:
            seen.add(no)

        metric = entry.get("metricOption") or {}
        wpa = _number(metric.get("wpaByPlate"))
        if not wpa:
            continue
        title = (entry.get("title") or "").strip()
        if not title or "==" in title or "공격" in title or "종료" in title:
            continue

        final_text = ""
        score = ""
        for option in reversed(entry.get("textOptions") or []):
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

        inning = entry.get("inn", "-")
        half = "말" if str(entry.get("homeOrAway")) == "1" else "초"
        description = f"{title} → {final_text}" if final_text and final_text != title else title
        events.append({
            "inning": f"{inning}회{half}",
            "description": description,
            "score": score,
            "wpa": wpa,
            "abs_wpa": abs(wpa),
            "order": _integer(no),
        })
    return events


def _score_flow(text_relays):
    states = []
    seen = set()
    options = []
    for entry in text_relays:
        for index, option in enumerate(entry.get("textOptions") or []):
            seqno = option.get("seqno")
            fallback = (_integer(entry.get("inn")), _integer(entry.get("no")), index)
            options.append((seqno is None, seqno if seqno is not None else fallback, option))

    for _, _, option in sorted(options, key=lambda item: (item[0], item[1])):
        state = option.get("currentGameState") or {}
        away = state.get("awayScore")
        home = state.get("homeScore")
        if away is None or home is None:
            continue
        score = (_integer(away), _integer(home))
        if score not in seen:
            seen.add(score)
            states.append(score)
    return states


def _flow_stats(text_relays, final_away, final_home):
    scores = _score_flow(text_relays)
    if (final_away, final_home) not in scores:
        scores.append((final_away, final_home))

    previous_leader = 0
    lead_changes = 0
    largest_lead = 0
    for away, home in scores:
        difference = away - home
        largest_lead = max(largest_lead, abs(difference))
        leader = 1 if difference > 0 else -1 if difference < 0 else 0
        if leader and previous_leader and leader != previous_leader:
            lead_changes += 1
        if leader:
            previous_leader = leader
    return lead_changes, largest_lead


def _mvp_candidate(game_detail, home_lineup, away_lineup, home_score, away_score):
    if home_score == away_score:
        return None
    winning_lineup = home_lineup if home_score > away_score else away_lineup
    batters = winning_lineup.get("batter") or []
    if batters:
        batter = max(
            batters,
            key=lambda player: (
                _integer(player.get("rbi")),
                _integer(player.get("hr")),
                _integer(player.get("hit")),
                _integer(player.get("run")),
            ),
        )
        hits = _integer(batter.get("hit"))
        home_runs = _integer(batter.get("hr"))
        rbi = _integer(batter.get("rbi"))
        runs = _integer(batter.get("run"))
        if any((hits, home_runs, rbi, runs)) and batter.get("name"):
            return f"{batter['name']} · {hits}안타 {home_runs}홈런 {rbi}타점 {runs}득점"

    winning_pitcher = game_detail.get("winPitcherName")
    return f"{winning_pitcher} · 승리투수" if winning_pitcher else None


def build_game_summary(game_detail, text_relays, home_name, away_name, home_lineup=None, away_lineup=None):
    home_score = _integer(game_detail.get("homeTeamScore"))
    away_score = _integer(game_detail.get("awayTeamScore"))
    if home_score > away_score:
        headline = f"{home_name} 승리 · {away_name} 상대 {home_score}-{away_score}"
        winner = home_name
    elif away_score > home_score:
        headline = f"{away_name} 승리 · {home_name} 상대 {away_score}-{home_score}"
        winner = away_name
    else:
        headline = f"{away_name} · {home_name} {away_score}-{home_score} 무승부"
        winner = "무승부"

    plate_events = _plate_events(text_relays, home_name, away_name)
    ranked_events = sorted(plate_events, key=lambda event: (-event["abs_wpa"], event["order"]))[:5]
    decisive = ranked_events[0] if ranked_events else None
    lead_changes, largest_lead = _flow_stats(text_relays, away_score, home_score)

    return {
        "headline": headline,
        "winner": winner,
        "final_score": f"{away_name} {away_score} : {home_score} {home_name}",
        "lead_changes": lead_changes,
        "largest_lead": largest_lead,
        "decisive_event": decisive,
        "key_events": ranked_events,
        "mvp_candidate": _mvp_candidate(
            game_detail,
            home_lineup or {},
            away_lineup or {},
            home_score,
            away_score,
        ),
    }
