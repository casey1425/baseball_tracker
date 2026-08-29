import httpx
import json

def get_game_relay(game_id: str):
    """
    경기 ID(game_id)의 실시간 문자 중계 및 타석 기록을 파싱합니다.
    """
    url = f"https://api-gw.sports.naver.com/schedule/games/{game_id}/relay"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        result = data.get("result", {})
        text_relay_data = result.get("textRelayData", {})

        # textRelayData가 딕셔너리인 경우 내부 리스트 추출, 리스트인 경우 그대로 사용
        if isinstance(text_relay_data, dict):
            relays = (
                text_relay_data.get("textRelays") or 
                text_relay_data.get("relays") or 
                text_relay_data.get("textRelayList") or 
                []
            )
            # 만약 위 키로도 안 잡히면 내부 딕셔너리 키 확인
            if not relays:
                for v in text_relay_data.values():
                    if isinstance(v, list):
                        relays = v
                        break
        elif isinstance(text_relay_data, list):
            relays = text_relay_data
        else:
            relays = []

        if not relays:
            print(f"[{game_id}] 중계 데이터 파싱 실패.")
            print(f"textRelayData 타입: {type(text_relay_data)}")
            if isinstance(text_relay_data, dict):
                print(f"textRelayData 내부 키 목록: {list(text_relay_data.keys())}")
            return

        print(f"=== 경기 ID: {game_id} 중계 로그 ({len(relays)}개 항목) ===")
        
        # 최근 10개 문자 중계 내역 출력
        for item in relays[-10:]:
            inning = item.get("inning", item.get("liveInning", "-"))
            text = item.get("text", item.get("message", item.get("title", ""))).strip()
            score = item.get("score", "")
            pitcher = item.get("pitcherName", "")
            batter = item.get("batterName", "")
            
            # 선수 정보가 있는 경우 함께 표기
            player_info = f" [투수:{pitcher}/타자:{batter}]" if pitcher or batter else ""
            print(f"[{inning}회] {text}{player_info} {f'({score})' if score else ''}")

    except Exception as e:
        print(f"문자 중계 수집 중 오류: {e}")

if __name__ == "__main__":
    SAMPLE_GAME_ID = "20260827OBKT02026"
    get_game_relay(SAMPLE_GAME_ID)