import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from game_preferences import load_favorite, save_favorite, choose_game, ordered_games
from game_summary import build_game_summary, is_game_finished
from highlight_events import classify_highlight, extract_highlights
from relay_filters import available_innings, filter_relays
from standings import build_standings

GAMES = [dict(gameId='a', homeTeamName='LG', awayTeamName='두산', statusCode='BEFORE', statusInfo='경기전'), dict(gameId='b', homeTeamName='kt', awayTeamName='한화', statusCode='BEFORE', statusInfo='경기전')]

class Response:
    status_code = 200

    def __init__(self, payload=None):
        self.payload = payload or {'result': {'games': GAMES}}

    def raise_for_status(self): pass
    def json(self): return self.payload


def live_response(url, **kwargs):
    relay = {
        "result": {
            "textRelayData": {
                "textRelays": [
                    {"no": 1, "inn": 1, "title": "김인태", "textOptions": [{"text": "김인태 : 홈런"}]},
                    {"no": 2, "inn": 2, "title": "박찬호", "textOptions": [{"text": "박찬호 : 삼진 아웃"}]},
                ]
            }
        }
    }
    if url.endswith('/relay'):
        return Response(relay)
    if '/schedule/games/' in url:
        return Response({'result': {'game': {'statusInfo': '2회말'}}})
    games = [dict(gameId='live', homeTeamName='LG', awayTeamName='두산', statusCode='LIVE', statusInfo='2회말')]
    return Response({'result': {'games': games}})


def finished_response(url, **kwargs):
    relays = [
        {
            "no": 1, "inn": 1, "homeOrAway": "0",
            "metricOption": {"wpaByPlate": -8.0},
            "textOptions": [{"seqno": 1, "text": "원정타자 : 2루타", "currentGameState": {"awayScore": 1, "homeScore": 0}}],
            "title": "원정타자",
        },
        {
            "no": 2, "inn": 9, "homeOrAway": "1",
            "metricOption": {"wpaByPlate": 42.0},
            "textOptions": [{"seqno": 2, "text": "홈타자 : 끝내기 홈런", "currentGameState": {"awayScore": 1, "homeScore": 2}}],
            "title": "홈타자",
        },
    ]
    lineup = {
        "homeLineup": {"batter": [{"name": "홈타자", "hit": 2, "hr": 1, "rbi": 2, "run": 1}], "pitcher": []},
        "awayLineup": {"batter": [{"name": "원정타자", "hit": 1, "hr": 0, "rbi": 1, "run": 1}], "pitcher": []},
    }
    if url.endswith('/relay'):
        return Response({'result': {'textRelayData': {"textRelays": relays, **lineup}}})
    if '/schedule/games/' in url:
        return Response({'result': {'game': {
            "statusCode": "RESULT", "statusInfo": "경기종료",
            "awayTeamName": "두산", "homeTeamName": "LG",
            "awayTeamScore": 1, "homeTeamScore": 2,
        }}})
    games = [dict(gameId='done', homeTeamName='LG', awayTeamName='두산', homeTeamScore=2, awayTeamScore=1, statusCode='RESULT', statusInfo='경기종료')]
    return Response({'result': {'games': games}})


def standings_response(url, **kwargs):
    if url.endswith('/teams/last-ten-games'):
        return Response({'result': {'seasonTeamLastTenGameStats': [
            {'teamId': 'KT', 'lastTenGameResult': '7승 1무 2패'},
            {'teamId': 'SS', 'lastTenGameResult': '6승 0무 4패'},
        ]}})
    if '/statistics/categories/kbo/seasons/' in url and url.endswith('/teams'):
        return Response({'result': {'seasonTeamStats': [
            {
                'teamId': 'KT', 'teamName': 'KT', 'ranking': 1, 'gameCount': 100,
                'winGameCount': 60, 'drawnGameCount': 2, 'loseGameCount': 38,
                'wra': 0.612, 'gameBehind': 0, 'continuousGameResult': '3승',
                'offenseRun': 520, 'defenseR': 420,
                'nextScheduleGameId': '20260911KTLT02026', 'opposingTeamName': '롯데',
            },
            {
                'teamId': 'SS', 'teamName': '삼성', 'ranking': 5, 'gameCount': 100,
                'winGameCount': 50, 'drawnGameCount': 2, 'loseGameCount': 48,
                'wra': 0.510, 'gameBehind': 10, 'continuousGameResult': '2패',
                'offenseRun': 450, 'defenseR': 460,
            },
        ]}})
    return Response()

class Features(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()

    def test_relay_filters(self):
        relays = [
            {"inn": 2, "title": "3번타자 김인태", "textOptions": [{"text": "김인태 : 우익수 뒤 홈런"}]},
            {"inn": 10, "title": "투수 교체", "textOptions": [{"text": "홍길동 투수로 교체"}]},
            {"inn": 1, "title": "1번타자 박찬호", "textOptions": [{"text": "박찬호 : 삼진 아웃"}]},
        ]
        self.assertEqual(available_innings(relays), ["1", "2", "10"])
        self.assertEqual(filter_relays(relays, query=" 김인태 "), [relays[0]])
        self.assertEqual(filter_relays(relays, inning="10"), [relays[1]])
        self.assertEqual(filter_relays(relays, result_types=["홈런"]), [relays[0]])
        self.assertEqual(filter_relays(relays, result_types=["삼진", "선수 교체"]), relays[1:])
        self.assertEqual(filter_relays(relays, query="박찬호", inning="2"), [])

    def test_result_filters_do_not_overlap(self):
        home_run = {"inn": 1, "title": "타자", "textOptions": [{"text": "좌익수 뒤 홈런"}]}
        strikeout = {"inn": 1, "title": "타자", "textOptions": [{"text": "삼진 아웃"}]}
        single = {"inn": 1, "title": "타자", "textOptions": [{"text": "우익수 앞 1루타"}]}
        run = {"inn": 1, "title": "주자", "textOptions": [{"text": "2루주자 홈인"}]}
        self.assertEqual(filter_relays([home_run], result_types=["안타·장타"]), [])
        self.assertEqual(filter_relays([strikeout], result_types=["아웃"]), [])
        self.assertEqual(filter_relays([single], result_types=["안타·장타"]), [single])
        self.assertEqual(filter_relays([run], result_types=["득점"]), [run])

    def test_highlights_use_text_classification_and_chronological_order(self):
        relays = [
            {
                "no": 2,
                "inn": 4,
                "homeOrAway": "0",
                "textOptions": [
                    {"seqno": 204, "type": 23, "text": "김민혁 : 우익수 앞 1루타", "currentGameState": {"awayScore": 5, "homeScore": 0}},
                ],
            },
            {
                "no": 1,
                "inn": 4,
                "homeOrAway": "0",
                "textOptions": [
                    {"seqno": 171, "type": 23, "text": "김상수 : 좌익수 앞 1루타", "currentGameState": {"awayScore": 1, "homeScore": 0}},
                    {"seqno": 173, "type": 24, "text": "2루주자 김현수 : 홈인", "currentGameState": {"awayScore": 2, "homeScore": 0}},
                ],
            },
        ]
        highlights = extract_highlights(relays, "롯데", "KT")
        self.assertEqual([event["seqno"] for event in highlights], [171, 173, 204])
        self.assertEqual([event["event_type"] for event in highlights], ["안타/장타", "득점", "안타/장타"])
        self.assertEqual([event["score"] for event in highlights], ["KT 1 : 0 롯데", "KT 2 : 0 롯데", "KT 5 : 0 롯데"])
        self.assertEqual(classify_highlight("우익수 앞 1루타", 23), "안타/장타")
        self.assertEqual(classify_highlight("우익수 뒤 홈런", 23), "홈런")

    def test_game_summary(self):
        relays = [
            {
                "no": 1, "inn": 1, "homeOrAway": "0", "title": "원정타자",
                "metricOption": {"wpaByPlate": -8.0},
                "textOptions": [{"seqno": 1, "text": "원정타자 : 적시타", "currentGameState": {"awayScore": 1, "homeScore": 0}}],
            },
            {
                "no": 2, "inn": 9, "homeOrAway": "1", "title": "홈타자",
                "metricOption": {"wpaByPlate": 42.0},
                "textOptions": [{"seqno": 2, "text": "홈타자 : 끝내기 홈런", "currentGameState": {"awayScore": 1, "homeScore": 2}}],
            },
        ]
        detail = {"statusCode": "RESULT", "awayTeamScore": 1, "homeTeamScore": 2}
        home_lineup = {"batter": [{"name": "홈타자", "hit": 2, "hr": 1, "rbi": 2, "run": 1}]}
        summary = build_game_summary(detail, relays, "LG", "두산", home_lineup, {})
        self.assertTrue(is_game_finished(detail))
        self.assertEqual(summary["headline"], "LG 승리 · 두산 상대 2-1")
        self.assertEqual(summary["lead_changes"], 1)
        self.assertEqual(summary["largest_lead"], 1)
        self.assertEqual(summary["decisive_event"]["wpa"], 42.0)
        self.assertEqual(summary["mvp_candidate"], "홈타자 · 2안타 1홈런 2타점 1득점")
        self.assertEqual(len(summary["key_events"]), 2)

    def test_standings_merge_favorite_and_recent_form(self):
        team_stats = [
            {'teamId': 'KT', 'teamName': 'KT', 'ranking': 1, 'gameCount': 100, 'winGameCount': 60, 'drawnGameCount': 2, 'loseGameCount': 38, 'wra': .612, 'gameBehind': 0, 'continuousGameResult': '3승', 'offenseRun': 520, 'defenseR': 420, 'nextScheduleGameId': '20260911KTLT02026', 'opposingTeamName': '롯데'},
            {'teamId': 'SS', 'teamName': '삼성', 'ranking': 5, 'gameCount': 100, 'winGameCount': 50, 'drawnGameCount': 2, 'loseGameCount': 48, 'wra': .510, 'gameBehind': 10, 'continuousGameResult': '2패', 'offenseRun': 450, 'defenseR': 460},
            {'teamId': 'HH', 'teamName': '한화', 'ranking': 6, 'gameCount': 100, 'winGameCount': 48, 'drawnGameCount': 2, 'loseGameCount': 50, 'wra': .490, 'gameBehind': 12, 'continuousGameResult': '1승', 'offenseRun': 430, 'defenseR': 470},
        ]
        recent = [{'teamId': 'KT', 'lastTenGameResult': '7승 1무 2패'}]
        rows, next_game = build_standings(team_stats, recent, 'KT')
        self.assertEqual(rows[0]['응원'], '⭐')
        self.assertEqual(rows[0]['최근 10경기'], '7승 1무 2패')
        self.assertEqual(rows[0]['득실차'], 100)
        self.assertEqual(rows[2]['5위 차'], '5위와 2.0G')
        self.assertEqual(next_game, {'date': '09월 11일', 'opponent': '롯데', 'location': '원정', 'game_id': '20260911KTLT02026'})

    def test_preferences(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'preferences.json'
            self.assertEqual(load_favorite(path), '선택 안 함')
            save_favorite('한화', path)
            self.assertEqual(load_favorite(path), '한화')
            path.write_text('broken')
            self.assertEqual(load_favorite(path), '선택 안 함')

    def test_order_and_selection(self):
        games = [dict(game_id='a', home='LG', away='두산'), dict(game_id='b', home='kt', away='한화')]
        self.assertEqual(ordered_games(games, 'KT')[0]['game_id'], 'b')
        self.assertEqual(choose_game(games, '한화'), 'b')
        self.assertEqual(choose_game(games, '한화', 'a'), 'a')
        self.assertEqual(choose_game(games, '한화', 'missing'), 'b')
        self.assertIsNone(choose_game([], '한화'))

    @patch('httpx.get', return_value=Response())
    @patch('game_preferences.save_favorite')
    @patch('game_preferences.load_favorite', return_value='한화')
    def test_ui(self, *_):
        app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['selected_game_id'], 'b')
        app.button(key='game_card_a').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['selected_game_id'], 'a')
        app.run()
        self.assertEqual(app.session_state['selected_game_id'], 'a')
        app.selectbox(key='favorite_team').select('KT').run()
        self.assertEqual(app.session_state['selected_game_id'], 'b')
        old_date = app.session_state['target_date']
        next(b for b in app.button if b.label == '◀ 이전').click().run()
        self.assertEqual((old_date - app.session_state['target_date']).days, 1)
        self.assertFalse(app.exception)

    @patch('httpx.get', side_effect=live_response)
    @patch('game_preferences.load_favorite', return_value='선택 안 함')
    def test_relay_filter_ui(self, *_):
        app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input(key='relay_search').value, '')
        self.assertEqual(app.selectbox(key='relay_inning').options, ['전체 이닝', '1회', '2회'])
        self.assertEqual(app.multiselect(key='relay_result_types').options[0], '홈런')
        app.text_input(key='relay_search').input('김인태').run()
        self.assertFalse(app.exception)
        self.assertTrue(any('전체 2개 중 1개' in caption.value for caption in app.caption))

    @patch('httpx.get', side_effect=finished_response)
    @patch('game_preferences.load_favorite', return_value='선택 안 함')
    def test_finished_game_summary_ui(self, *_):
        app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run()
        self.assertFalse(app.exception)
        self.assertTrue(any(tab.label == '📝 경기 종료 요약' for tab in app.tabs))
        self.assertTrue(any('LG 승리' in message.value for message in app.success))

    @patch('httpx.get', side_effect=standings_response)
    @patch('game_preferences.load_favorite', return_value='KT')
    def test_standings_ui(self, *_):
        app = AppTest.from_file(str(Path(__file__).with_name('app.py'))).run()
        app.radio(key='dashboard_view').set_value('🏆 팀 순위').run()
        self.assertFalse(app.exception)
        self.assertTrue(any('KBO 팀 순위' in header.value for header in app.header))
        self.assertTrue(any('vs 롯데' in message.value for message in app.info))
        self.assertGreaterEqual(len(app.dataframe), 1)

if __name__ == '__main__': unittest.main()
