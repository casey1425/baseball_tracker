import httpx
from datetime import datetime

def get_kbo_games(target_date: str = "2026-08-27"):
    """
    네이버 스포츠 API에서 KBO(kbaseball) 경기 목록을 수집합니다.
    """
    url = "https://api-gw.sports.naver.com/schedule/games"
    params = {
        "fields": "basic,superOrganize,statusInfo",
        "fromDate": target_date,
        "toDate": target_date,
        "upperCategoryId": "kbaseball",
        "category": "kbaseball",
        "size": 100
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(url, params=params, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        games = data.get("result", {}).get("games", [])
        if not games:
            print(f"[{target_date}] KBO 경기 데이터를 찾을 수 없습니다.")
            return []

        print(f"=== {target_date} KBO 경기 목록 ({len(games)}경기) ===")
        parsed_games = []
        for g in games:
            home = g.get("homeTeamName") or (g.get("homeTeam", {}).get("name") if isinstance(g.get("homeTeam"), dict) else "홈")
            away = g.get("awayTeamName") or (g.get("awayTeam", {}).get("name") if isinstance(g.get("awayTeam"), dict) else "원정")
            home_score = g.get("homeTeamScore", 0)
            away_score = g.get("awayTeamScore", 0)
            status = g.get("statusInfo") or g.get("statusCode", "정보없음")
            venue = g.get("venue") or "구장 미정"
            game_id = g.get("gameId")

            parsed_games.append({
                "game_id": game_id,
                "status": status,
                "away": away,
                "away_score": away_score,
                "home": home,
                "home_score": home_score,
                "venue": venue
            })
            print(f"[{status}] {away} {away_score} vs {home_score} {home} ({venue}) | ID: {game_id}")

        return parsed_games

    except Exception as e:
        print(f"네트워크/파싱 오류 발생: {e}")
        return []

if __name__ == "__main__":
    get_kbo_games("2026-08-27")