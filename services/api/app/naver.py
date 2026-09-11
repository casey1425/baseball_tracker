"""Async client for the Naver Sports endpoints used by the API."""

import asyncio

import httpx


DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://m.sports.naver.com/",
}

TEAM_STADIUM_MAP = {
    "두산": "잠실", "LG": "잠실", "KT": "수원", "kt": "수원",
    "SSG": "문학", "키움": "고척", "한화": "대전", "KIA": "광주",
    "기아": "광주", "삼성": "대구", "롯데": "사직", "NC": "창원",
}


class UpstreamError(RuntimeError):
    """Raised when Naver Sports cannot provide a usable response."""


class NaverSportsClient:
    base_url = "https://api-gw.sports.naver.com"

    async def _get(self, path, params=None):
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url,
                headers=DEFAULT_HEADERS,
                timeout=7.0,
                follow_redirects=True,
            ) as client:
                response = await client.get(path, params=params)
                response.raise_for_status()
                return response.json() or {}
        except (httpx.HTTPError, ValueError) as exc:
            raise UpstreamError(f"Naver Sports request failed: {path}") from exc

    async def games_by_date(self, target_date):
        payload = await self._get("/schedule/games", params={
            "fromDate": target_date,
            "toDate": target_date,
            "upperCategoryId": "kbaseball",
            "category": "kbaseball",
            "size": 100,
        })
        games = ((payload.get("result") or {}).get("games") or [])
        parsed = []
        for game in games:
            game_id = game.get("gameId")
            home = game.get("homeTeamName")
            away = game.get("awayTeamName")
            if not game_id or not home or not away:
                continue
            venue = game.get("stadium") or game.get("stadiumName") or game.get("venue")
            if not venue or venue == "구장 미정":
                venue = TEAM_STADIUM_MAP.get(home, "구장 미정")
            status = game.get("statusInfo") or game.get("statusCode") or "정보없음"
            parsed.append({
                "game_id": game_id,
                "home": home,
                "away": away,
                "home_score": game.get("homeTeamScore") or 0,
                "away_score": game.get("awayTeamScore") or 0,
                "status": status,
                "status_code": game.get("statusCode") or "",
                "venue": venue,
                "cancel": bool(game.get("cancel")) or "취소" in str(status),
            })
        return parsed

    async def game_detail(self, game_id):
        payload = await self._get(f"/schedule/games/{game_id}")
        return ((payload.get("result") or {}).get("game") or {})

    async def relay(self, game_id, inning=None):
        params = {"inning": inning} if inning is not None else None
        payload = await self._get(f"/schedule/games/{game_id}/relay", params=params)
        relay_data = ((payload.get("result") or {}).get("textRelayData") or {})
        return {
            "text_relays": relay_data.get("textRelays") or [],
            "current_state": relay_data.get("currentGameState") or {},
            "home_lineup": relay_data.get("homeLineup") or {},
            "away_lineup": relay_data.get("awayLineup") or {},
            "pitcher_vs_batter": relay_data.get("pitcherVsBatterCareerStats") or "",
        }

    async def all_relays(self, game_id, total_innings):
        innings = range(1, max(total_innings, 9) + 1)
        responses = await asyncio.gather(*(self.relay(game_id, inning) for inning in innings))
        seen = set()
        relays = []
        for inning, response in zip(innings, responses):
            entries = response["text_relays"]
            matched = [entry for entry in entries if str(entry.get("inn")) == str(inning)]
            for entry in matched or entries:
                no = entry.get("no")
                if no is not None and no in seen:
                    continue
                if no is not None:
                    seen.add(no)
                relays.append(entry)
        return relays

    async def standings(self, season):
        base = f"/statistics/categories/kbo/seasons/{season}/teams"
        teams_payload, recent_payload = await asyncio.gather(
            self._get(base, params={"gameType": "REGULAR_SEASON"}),
            self._get(f"{base}/last-ten-games"),
        )
        teams = ((teams_payload.get("result") or {}).get("seasonTeamStats") or [])
        recent = ((recent_payload.get("result") or {}).get("seasonTeamLastTenGameStats") or [])
        return teams, recent


def get_naver_client():
    return NaverSportsClient()
