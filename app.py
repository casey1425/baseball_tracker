import streamlit as st
import httpx
from datetime import datetime

st.set_page_config(page_title="KBO 실시간 중계 대시보드", layout="wide", page_icon="⚾")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 1. 경기 목록 가져오기
def fetch_games(target_date: str):
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
                "venue": g.get("venue") or "구장 미정"
            })
        return parsed
    except Exception as e:
        st.error(f"경기 목록 조회 오류: {e}")
        return []

# 2. 중계 로그 가져오기 (relay.py 검증 로직 적용)
def fetch_relay(game_id: str):
    url = f"https://api-gw.sports.naver.com/schedule/games/{game_id}/relay"
    try:
        res = httpx.get(url, headers=HEADERS, timeout=5.0)
        res.raise_for_status()
        result = res.json().get("result", {})
        relay_data = result.get("textRelayData", {})
        
        relays = []
        if isinstance(relay_data, dict):
            # 단일 키 탐색
            relays = (
                relay_data.get("textRelays") or 
                relay_data.get("relays") or 
                relay_data.get("textRelayList") or 
                []
            )
            # 단일 키가 없을 경우 내부 모든 리스트 병합
            if not relays:
                for v in relay_data.values():
                    if isinstance(v, list):
                        relays.extend(v)
        elif isinstance(relay_data, list):
            relays = relay_data
            
        return relays, relay_data
    except Exception as e:
        st.error(f"중계 데이터 조회 오류: {e}")
        return [], {}

# UI 레이아웃
st.title("⚾ KBO 실시간 경기 대시보드")

st.sidebar.header("경기 탐색")
selected_date = st.sidebar.date_input("날짜 선택", datetime(2026, 8, 27))
date_str = selected_date.strftime("%Y-%m-%d")

games = fetch_games(date_str)

if not games:
    st.warning(f"[{date_str}] 진행되거나 등록된 KBO 경기가 없습니다.")
else:
    game_options = {
        f"[{g['status']}] {g['away']} {g['away_score']} vs {g['home_score']} {g['home']} ({g['venue']})": g['game_id'] 
        for g in games
    }
    selected_label = st.sidebar.selectbox("경기를 선택하세요", list(game_options.keys()))
    selected_game_id = game_options[selected_label]
    
    current_game = next((g for g in games if g["game_id"] == selected_game_id), None)

    if current_game:
        # 상단 스코어보드
        col1, col2, col3 = st.columns([2, 1, 2])
        with col1:
            st.markdown(f"<h2 style='text-align: right;'>{current_game['away']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: right; color: #1E88E5;'>{current_game['away_score']}</h1>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<p style='text-align: center; margin-top: 15px; font-weight: bold; font-size: 1.2rem;'>{current_game['status']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: gray;'>{current_game['venue']}</p>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<h2 style='text-align: left;'>{current_game['home']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: left; color: #E53935;'>{current_game['home_score']}</h1>", unsafe_allow_html=True)

        st.divider()

        # 하단 문자 중계 로그
        st.subheader("📋 실시간 문자 중계 로그")
        relays, raw_data = fetch_relay(selected_game_id)

        if relays:
            st.caption(f"총 {len(relays)}개의 중계 항목을 불러왔습니다.")
            # 최신 로그가 위로 오도록 역순 출력
            for item in reversed(relays):
                if isinstance(item, dict):
                    text = item.get("text") or item.get("message") or item.get("title") or ""
                    inning = item.get("inning", item.get("liveInning", ""))
                    batter = item.get("batterName", "")
                    pitcher = item.get("pitcherName", "")
                else:
                    text = str(item)
                    inning, batter, pitcher = "", "", ""

                text = str(text).strip()
                if not text:
                    continue

                prefix = f"**[{inning}회]** " if inning else ""
                players = f" *(투수: {pitcher} / 타자: {batter})*" if pitcher or batter else ""

                if any(k in text for k in ["홈런", "득점", "적시타", "역전", "승리"]):
                    st.success(f"{prefix}🔥 {text}{players}")
                elif any(k in text for k in ["아웃", "삼진", "병살", "플라이", "땅볼"]):
                    st.info(f"{prefix}⚾ {text}{players}")
                elif "공격" in text or "이닝" in text:
                    st.warning(f"{prefix}📢 {text}")
                else:
                    st.markdown(f"{prefix}• {text}{players}")
        else:
            st.info("해당 경기는 상세 문자 중계 데이터가 아직 없거나 종료된 경기입니다.")

if st.sidebar.button("🔄 실시간 데이터 새로고침"):
    st.rerun()