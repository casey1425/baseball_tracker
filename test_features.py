import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from game_preferences import load_favorite, save_favorite, choose_game, ordered_games

GAMES = [dict(gameId='a', homeTeamName='LG', awayTeamName='두산', statusCode='BEFORE', statusInfo='경기전'), dict(gameId='b', homeTeamName='kt', awayTeamName='한화', statusCode='BEFORE', statusInfo='경기전')]

class Response:
    def raise_for_status(self): pass
    def json(self): return {'result': {'games': GAMES}}

class Features(unittest.TestCase):
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

if __name__ == '__main__': unittest.main()
