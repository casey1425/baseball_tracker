import streamlit as st
import httpx
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="KBO 실시간 중계 대시보드", layout="wide", page_icon="⚾")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# 1. 특정 날짜 경기 목록 조회
@st.cache_data(ttl=15)
def fetch_games_by_date(target_date: str):
    url = "https://api-gw.sports.naver.com/schedule/games"
    params = {
        "fields": "basic,superOrganize,statusInfo",
        "fromDate": target_date,
        "toDate": target_date,
        "upperCategoryId": "kbaseball",
        "category": "kbaseball",
        "size": 100
    }
    try:
        res = httpx.get(url, params=params, headers=HEADERS, timeout=5.0)
        res.raise_for_status()
        games = res.json().get("result", {}).get("games", [])
        
        parsed = []
        for g in games:
            parsed.append({
                "game_id": g.get("gameId"),
                "home": g.get("homeTeamName", "홈"),
                "away": g.get("awayTeamName", "원정"),
                "home_score": g.get("homeTeamScore", 0),
                "away_score": g.get("awayTeamScore", 0),
                "status": g.get("statusInfo") or g.get("statusCode", "정보없음"),
                "venue": g.get("venue") or g.get("stadium") or "구장 미정"
            })
        return parsed
    except Exception as e:
        st.error(f"경기 목록 조회 오류: {e}")
        return []

# 2. 경기 상세(라인스코어/선발투수) 조회
def fetch_game_detail(game_id: str):
    url = f"https://api-gw.sports.naver.com/schedule/games/{game_id}"
    try:
        res = httpx.get(url, headers=HEADERS, timeout=5.0)
        res.raise_for_status()
        return res.json().get("result", {}).get("game", {})
    except Exception as e:
        st.error(f"경기 상세 조회 오류: {e}")
        return {}

# 3. 실시간 문자 중계 및 실시간 볼카운트/주자 상태 조회
def fetch_relay(game_id: str):
    url = f"https://api-gw.sports.naver.com/schedule/games/{game_id}/relay"
    try:
        res = httpx.get(url, headers=HEADERS, timeout=5.0)
        res.raise_for_status()
        result = res.json().get("result", {})
        relay_data = result.get("textRelayData", {})
        
        text_relays = relay_data.get("textRelays", [])
        current_state = relay_data.get("currentGameState", {})
        
        # currentGameState가 비어있을 경우 최신 텍스트 옵션에서 추출
        if not current_state and text_relays:
            for item in reversed(text_relays):
                opts = item.get("textOptions", [])
                if opts:
                    current_state = opts[-1].get("currentGameState", {})
                    if current_state:
                        break
                        
        return text_relays, current_state
    except Exception as e:
        st.error(f"중계 데이터 조회 오류: {e}")
        return [], {}

# 4. 라인스코어 데이터프레임 생성
def build_linescore_df(game_data):
    away_name = game_data.get("awayTeamName", "원정")
    home_name = game_data.get("homeTeamName", "홈")
    away_innings = game_data.get("awayTeamScoreByInning", [])
    home_innings = game_data.get("homeTeamScoreByInning", [])
    
    total_innings = max(len(away_innings), len(home_innings), 9)
    col_names = [str(i) for i in range(1, total_innings + 1)]
    
    def pad(scores, length):
        return [str(s) if s is not None else "-" for s in scores] + ["-"] * (length - len(scores))
    
    data = {"팀": [away_name, home_name]}
    for idx, col in enumerate(col_names):
        data[col] = [pad(away_innings, total_innings)[idx], pad(home_innings, total_innings)[idx]]
        
    away_rheb = game_data.get("awayTeamRheb", [])
    home_rheb = game_data.get("homeTeamRheb", [])
    if len(away_rheb) >= 4 and len(home_rheb) >= 4:
        data["R"] = [away_rheb[0], home_rheb[0]]
        data["H"] = [away_rheb[1], home_rheb[1]]
        data["E"] = [away_rheb[2], home_rheb[2]]
        data["B"] = [away_rheb[3], home_rheb[3]]
    else:
        data["R"] = [game_data.get("awayTeamScore", 0), game_data.get("homeTeamScore", 0)]
        data["H"], data["E"], data["B"] = ["-", "-"], ["-", "-"], ["-", "-"]
        
    return pd.DataFrame(data)

# 5. 주자 다이아몬드 & BSO 볼카운트 위젯 렌더러 (들여쓰기 에러 해결)
def render_game_status_widget(state):
    try:
        ball = int(state.get("ball", 0))
        strike = int(state.get("strike", 0))
        out = int(state.get("out", 0))
    except (ValueError, TypeError):
        ball, strike, out = 0, 0, 0

    base1 = str(state.get("base1", "0")) in ["1", 1]
    base2 = str(state.get("base2", "0")) in ["1", 1]
    base3 = str(state.get("base3", "0")) in ["1", 1]

    # 베이스 색상 (점유 시 황금색, 비어있을 시 어두운 회색)
    c1 = "#FFB300" if base1 else "#333742"
    c2 = "#FFB300" if base2 else "#333742"
    c3 = "#FFB300" if base3 else "#333742"

    def make_dots(current_count, max_count, active_color):
        dots = ""
        for i in range(max_count):
            if i < current_count:
                dots += f'<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background-color:{active_color}; margin-right:4px; box-shadow: 0 0 6px {active_color};"></span>'
            else:
                dots += '<span style="display:inline-block; width:10px; height:10px; border-radius:50%; background-color:#2A2D34; border:1px solid #444; margin-right:4px;"></span>'
        return dots

    b_dots = make_dots(ball, 3, "#4CAF50")
    s_dots = make_dots(strike, 2, "#FF9800")
    o_dots = make_dots(out, 2, "#F44336")

    # 공백 줄바꿈 없이 한 줄로 결합하여 마크다운 파싱 오류 방지
    widget_html = (
        '<div style="background: rgba(30, 32, 40, 0.85); padding: 10px 16px; border-radius: 12px; border: 1px solid #3d4251; display: flex; align-items: center; justify-content: center; gap: 20px; margin: 8px auto; max-width: 280px;">'
        '<svg width="65" height="55" viewBox="0 0 80 70">'
        '<path d="M 40 58 L 64 35 L 40 12 L 16 35 Z" fill="none" stroke="#4B5263" stroke-width="2" stroke-dasharray="2 2" />'
        f'<rect x="34" y="6" width="12" height="12" transform="rotate(45 40 12)" fill="{c2}" stroke="#1E2028" stroke-width="1.5" rx="1"/>'
        f'<rect x="10" y="29" width="12" height="12" transform="rotate(45 16 35)" fill="{c3}" stroke="#1E2028" stroke-width="1.5" rx="1"/>'
        f'<rect x="58" y="29" width="12" height="12" transform="rotate(45 64 35)" fill="{c1}" stroke="#1E2028" stroke-width="1.5" rx="1"/>'
        '<polygon points="40,64 35,59 35,54 45,54 45,59" fill="#9E9E9E"/>'
        '</svg>'
        '<div style="display: flex; flex-direction: column; gap: 4px; font-family: monospace; font-size: 11px; font-weight: bold;">'
        f'<div style="display: flex; align-items: center;"><span style="color: #4CAF50; width: 14px; text-align: left;">B</span><div>{b_dots}</div></div>'
        f'<div style="display: flex; align-items: center;"><span style="color: #FF9800; width: 14px; text-align: left;">S</span><div>{s_dots}</div></div>'
        f'<div style="display: flex; align-items: center;"><span style="color: #F44336; width: 14px; text-align: left;">O</span><div>{o_dots}</div></div>'
        '</div>'
        '</div>'
    )
    
    # st.html 지원 버전일 경우 st.html 사용, 미지원 시 st.markdown 대체
    if hasattr(st, "html"):
        st.html(widget_html)
    else:
        st.markdown(widget_html, unsafe_allow_html=True)


# --- 대시보드 메인 UI ---
st.title("⚾ KBO 실시간 & 경기 기록 대시보드")

# 사이드바 날짜 탐색
st.sidebar.header("📅 날짜 선택")
if "target_date" not in st.session_state:
    st.session_state["target_date"] = datetime(2026, 8, 27).date()

c_prev, c_today, c_next = st.sidebar.columns(3)
if c_prev.button("◀ 이전"):
    st.session_state["target_date"] -= timedelta(days=1)
    st.rerun()
if c_today.button("오늘"):
    st.session_state["target_date"] = datetime.now().date()
    st.rerun()
if c_next.button("다음 ▶"):
    st.session_state["target_date"] += timedelta(days=1)
    st.rerun()

selected_date = st.sidebar.date_input("날짜 지정", st.session_state["target_date"])
st.session_state["target_date"] = selected_date
date_str = selected_date.strftime("%Y-%m-%d")

# 경기 목록 호출
games = fetch_games_by_date(date_str)

if not games:
    st.warning(f"[{date_str}] 진행되거나 등록된 KBO 경기가 없습니다.")
else:
    game_options = {
        f"[{g['status']}] {g['away']} {g['away_score']} vs {g['home_score']} {g['home']} ({g['venue']})": g['game_id'] 
        for g in games
    }
    selected_label = st.sidebar.selectbox("경기를 선택하세요", list(game_options.keys()))
    selected_game_id = game_options[selected_label]
    
    game_detail = fetch_game_detail(selected_game_id)
    text_relays, current_state = fetch_relay(selected_game_id)

    if game_detail:
        # 상단 점수 헤더 & BSO/주자 위젯
        c1, c2, c3 = st.columns([2, 2, 2])
        with c1:
            st.markdown(f"<h2 style='text-align: right;'>{game_detail.get('awayTeamFullName', game_detail.get('awayTeamName'))}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: right; color: #1E88E5;'>{game_detail.get('awayTeamScore', 0)}</h1>", unsafe_allow_html=True)
            if game_detail.get('awayStarterName'):
                st.markdown(f"<p style='text-align: right; color: gray;'>선발: {game_detail['awayStarterName']}</p>", unsafe_allow_html=True)
        
        with c2:
            st.markdown(f"<p style='text-align: center; margin-top: 5px; font-weight: bold; font-size: 1.25rem;'>{game_detail.get('statusInfo', '경기종료')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray; margin-bottom: 2px;'>{game_detail.get('stadium', '구장')}</p>", unsafe_allow_html=True)
            
            # 주자 다이아몬드 및 BSO 볼카운트 위젯 렌더링
            render_game_status_widget(current_state)
            
            win_p, lose_p = game_detail.get("winPitcherName"), game_detail.get("losePitcherName")
            if win_p or lose_p:
                st.markdown(f"<p style='text-align: center; color: #8E94A0; font-size: 0.85rem;'>승: {win_p or '-'} / 패: {lose_p or '-'}</p>", unsafe_allow_html=True)
        
        with c3:
            st.markdown(f"<h2 style='text-align: left;'>{game_detail.get('homeTeamFullName', game_detail.get('homeTeamName'))}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: left; color: #E53935;'>{game_detail.get('homeTeamScore', 0)}</h1>", unsafe_allow_html=True)
            if game_detail.get('homeStarterName'):
                st.markdown(f"<p style='text-align: left; color: gray;'>선발: {game_detail['homeStarterName']}</p>", unsafe_allow_html=True)

        st.divider()

        # 라인스코어보드
        st.subheader("📊 라인스코어 (Linescore)")
        st.dataframe(build_linescore_df(game_detail), use_container_width=True, hide_index=True)

        st.divider()

        # 타석 및 투구 상세 중계 피드
        st.subheader("📋 타석 및 투구 상세 중계")
        
        if text_relays:
            st.caption(f"총 {len(text_relays)}개의 타석/이닝 이벤트")
            
            for at_bat in reversed(text_relays):
                title = at_bat.get("title", "").strip()
                inning = at_bat.get("inn", "")
                text_options = at_bat.get("textOptions", [])

                if not text_options or "==" in title or "공격" in title or "종료" in title:
                    header_text = title if title and "==" not in title else (text_options[0].get("text") if text_options else "")
                    if header_text and "==" not in header_text:
                        st.warning(f"📢 **[{inning}회] {header_text}**")
                    continue

                final_action = text_options[-1] if text_options else {}
                final_text = final_action.get("text", "").strip()
                
                state = final_action.get("currentGameState", {})
                b = state.get("ball", "-")
                s = state.get("strike", "-")
                o = state.get("out", "-")
                b1 = "1루" if str(state.get("base1")) == "1" else ""
                b2 = "2루" if str(state.get("base2")) == "1" else ""
                b3 = "3루" if str(state.get("base3")) == "1" else ""
                runners = ", ".join(filter(None, [b1, b2, b3])) or "주자 없음"

                if any(k in final_text for k in ["홈런", "적시타", "2루타", "3루타", "안타", "득점", "끝내기"]):
                    result_badge = f"🔥 **{final_text}**"
                elif any(k in final_text for k in ["삼진", "아웃", "병살", "플라이", "땅볼", "파울플라이"]):
                    result_badge = f"⚾ **{final_text}**"
                elif any(k in final_text for k in ["볼넷", "사구", "몸에 맞는"]):
                    result_badge = f"🚶 **{final_text}**"
                else:
                    result_badge = f"• **{final_text}**"

                expander_title = f"[{inning}회] {title} ➔ {final_text} (B{b}-S{s}-O{o} | {runners})"

                with st.expander(expander_title, expanded=False):
                    st.markdown(f"**결과 요약:** {result_badge}")
                    st.caption(f"상황: 볼카운트 B{b}-S{s}-O{o} | 주자: {runners}")
                    st.markdown("---")
                    
                    for opt in text_options:
                        pitch_text = opt.get("text", "").strip()
                        stuff = opt.get("stuff", "").strip()
                        opt_state = opt.get("currentGameState", {})
                        p_b = opt_state.get("ball", "-")
                        p_s = opt_state.get("strike", "-")
                        p_o = opt_state.get("out", "-")
                        
                        if "==" in pitch_text or not pitch_text:
                            continue

                        stuff_label = f"`[{stuff}]` " if stuff else ""
                        st.markdown(f"- {stuff_label}**{pitch_text}** `(B{p_b}-S{p_s}-O{p_o})`")
        else:
            st.info("문자 중계 데이터가 등록되어 있지 않습니다.")

if st.sidebar.button("🔄 실시간 새로고침"):
    st.cache_data.clear()
    st.rerun()