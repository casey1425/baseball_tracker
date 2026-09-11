import unittest

from fastapi.testclient import TestClient

from services.api.app.main import app
from services.api.app.naver import get_naver_client


class FakeNaverClient:
    def __init__(self, finished=True):
        self.finished = finished

    async def games_by_date(self, target_date):
        return [{
            "game_id": "game-1", "home": "LG", "away": "두산",
            "home_score": 2, "away_score": 1, "status": "경기종료",
            "status_code": "RESULT", "venue": "잠실", "cancel": False,
        }]

    async def game_detail(self, game_id):
        return {
            "gameId": game_id,
            "statusCode": "RESULT" if self.finished else "LIVE",
            "statusInfo": "경기종료" if self.finished else "5회말",
            "homeTeamName": "LG", "awayTeamName": "두산",
            "homeTeamScore": 2, "awayTeamScore": 1,
            "homeTeamScoreByInning": [0, 0, 0, 0, 0, 0, 0, 0, 2],
            "awayTeamScoreByInning": [1, 0, 0, 0, 0, 0, 0, 0, 0],
        }

    async def relay(self, game_id, inning=None):
        return {
            "text_relays": self._relays(),
            "current_state": {
                "homeScore": 2, "awayScore": 1, "pitcher": "P1", "batter": "B1",
                "ball": 1, "strike": 1, "out": 1, "base1": "R1", "base2": "0", "base3": "0",
            },
            "home_lineup": {"batter": [{"pcode": "B1", "name": "홈타자", "hit": 2, "hr": 1, "rbi": 2, "run": 1}]},
            "away_lineup": {"batter": [], "pitcher": [{"pcode": "P1", "name": "원정투수"}]},
            "pitcher_vs_batter": "시즌 첫 맞대결",
        }

    async def all_relays(self, game_id, total_innings):
        return self._relays()

    async def standings(self, season):
        teams = [
            {
                "teamId": "KT", "teamName": "KT", "ranking": 1,
                "gameCount": 100, "winGameCount": 60, "drawnGameCount": 2,
                "loseGameCount": 38, "wra": 0.612, "gameBehind": 0,
                "continuousGameResult": "3승", "offenseRun": 520, "defenseR": 420,
                "nextScheduleGameId": "20260911KTLT02026", "opposingTeamName": "롯데",
            },
            {
                "teamId": "SS", "teamName": "삼성", "ranking": 5,
                "gameCount": 100, "winGameCount": 50, "drawnGameCount": 2,
                "loseGameCount": 48, "wra": 0.510, "gameBehind": 10,
                "continuousGameResult": "2패", "offenseRun": 450, "defenseR": 460,
            },
        ]
        recent = [{"teamId": "KT", "lastTenGameResult": "7승 1무 2패"}]
        return teams, recent

    @staticmethod
    def _relays():
        return [
            {
                "no": 1, "inn": 1, "homeOrAway": "0", "title": "원정타자",
                "metricOption": {"homeTeamWinRate": 40.0, "awayTeamWinRate": 60.0, "wpaByPlate": -8.0},
                "textOptions": [{"seqno": 1, "type": 23, "text": "원정타자 : 2루타", "currentGameState": {"awayScore": 1, "homeScore": 0}}],
            },
            {
                "no": 2, "inn": 9, "homeOrAway": "1", "title": "4번타자 홈타자",
                "metricOption": {"homeTeamWinRate": 100.0, "awayTeamWinRate": 0.0, "wpaByPlate": 42.0},
                "textOptions": [
                    {"seqno": 2, "type": 1, "pitchNum": 1, "pitchResult": "B", "stuff": "직구", "speed": "145", "text": "1구 볼"},
                    {"seqno": 3, "type": 23, "text": "홈타자 : 끝내기 홈런", "currentGameState": {"awayScore": 1, "homeScore": 2}},
                ],
            },
        ]


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeNaverClient()
        app.dependency_overrides[get_naver_client] = lambda: self.fake
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_health_and_openapi(self):
        self.assertEqual(self.client.get("/api/v1/health").json()["status"], "ok")
        schema = self.client.get("/openapi.json").json()
        self.assertIn("/api/v1/games/{game_id}/summary", schema["paths"])

    def test_games_detail_and_relay(self):
        games = self.client.get("/api/v1/games", params={"date": "2026-09-11"})
        self.assertEqual(games.status_code, 200)
        self.assertEqual(games.json()["date"], "2026-09-11")
        self.assertEqual(games.json()["games"][0]["game_id"], "game-1")
        self.assertEqual(self.client.get("/api/v1/games/game-1").json()["game"]["homeTeamName"], "LG")
        relay = self.client.get("/api/v1/games/game-1/relay", params={"inning": 9}).json()
        self.assertEqual(relay["inning"], 9)
        self.assertEqual(len(relay["text_relays"]), 2)

    def test_analysis_endpoints(self):
        highlights = self.client.get("/api/v1/games/game-1/highlights").json()["highlights"]
        self.assertEqual([event["event_type"] for event in highlights], ["안타/장타", "홈런"])
        points = self.client.get("/api/v1/games/game-1/win-probability").json()["points"]
        self.assertEqual(len(points), 3)
        summary = self.client.get("/api/v1/games/game-1/summary")
        self.assertEqual(summary.status_code, 200)
        self.assertIn("LG 승리", summary.json()["summary"]["headline"])

    def test_dashboard_endpoint(self):
        response = self.client.get("/api/v1/games/game-1/dashboard")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["game"]["homeTeamName"], "LG")
        self.assertEqual([event["event_type"] for event in payload["highlights"]], ["안타/장타", "홈런"])
        self.assertEqual(len(payload["points"]), 3)
        situation = payload["live_situation"]
        self.assertEqual(situation["pitcher"]["name"], "원정투수")
        self.assertEqual(situation["batter"]["name"], "홈타자")
        self.assertTrue(situation["bases"]["first"])
        self.assertEqual(situation["recent_pitches"][0]["speed"], "145")

    def test_summary_requires_finished_game(self):
        self.fake.finished = False
        response = self.client.get("/api/v1/games/game-1/summary")
        self.assertEqual(response.status_code, 409)

    def test_standings_and_next_game(self):
        standings = self.client.get("/api/v1/standings", params={"season": 2026, "favorite_team": "KT"})
        self.assertEqual(standings.status_code, 200)
        self.assertTrue(standings.json()["standings"][0]["favorite"])
        self.assertEqual(standings.json()["standings"][0]["recent_ten"], "7승 1무 2패")
        next_game = self.client.get("/api/v1/teams/KT/next-game", params={"season": 2026})
        self.assertEqual(next_game.json()["next_game"]["opponent"], "롯데")
        unknown = self.client.get("/api/v1/teams/없는팀/next-game", params={"season": 2026})
        self.assertEqual(unknown.status_code, 404)


if __name__ == "__main__":
    unittest.main()
