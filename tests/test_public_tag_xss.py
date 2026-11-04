import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from udisc_scrape import InvalidUDiscEventURL, validate_udisc_event_url


db_stub = types.ModuleType('db')
for function_name in (
    'add_player',
    'add_ctp',
    'get_ctp',
    'get_ctp_wrap',
    'get_players',
    'get_player_history',
    'get_player_most_recent_tag',
    'get_tag_history',
    'get_tag_holders',
    'update_player_place',
    'update_tag_out',
    'wrap_up',
    'get_players_detailed',
    'delete_player',
    'return_users_from_individuals',
    'get_player_stats_by_tag',
    'get_scoreboard_url',
    'get_todays_player_handicaps',
):
    setattr(db_stub, function_name, lambda *args, **kwargs: None)

disc_choice_stub = types.ModuleType('disc_choice')
disc_choice_stub.punishment = lambda: None
fuzzy_sort_stub = types.ModuleType('fuzzy_sort')
fuzzy_sort_stub.fuzzy_sort_names = lambda *args, **kwargs: None
payout_stub = types.ModuleType('payout')
payout_stub.payout_manager = lambda *args, **kwargs: None
udisc_scrape_stub = types.ModuleType('udisc_scrape')
udisc_scrape_stub.InvalidUDiscEventURL = InvalidUDiscEventURL
udisc_scrape_stub.scrape_results_page = lambda *args, **kwargs: None
udisc_scrape_stub.validate_udisc_event_url = validate_udisc_event_url

with patch.dict(
    sys.modules,
    {
        'db': db_stub,
        'disc_choice': disc_choice_stub,
        'fuzzy_sort': fuzzy_sort_stub,
        'payout': payout_stub,
        'udisc_scrape': udisc_scrape_stub,
    },
):
    module_spec = importlib.util.spec_from_file_location(
        'flask_app_security_under_test',
        Path(__file__).resolve().parents[1] / 'flask_app.py',
    )
    flask_app = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(flask_app)


class PublicTagHistorySecurityTests(unittest.TestCase):
    def setUp(self):
        flask_app.app.config.update(
            SECRET_KEY='test-secret',
            SITE_USER='test-user',
            SITE_PASSWORD='test-password',
        )

    def test_no_data_response_escapes_attacker_controlled_tag_and_year(self):
        client = flask_app.app.test_client()
        with patch.object(flask_app, 'get_player_stats_by_tag', return_value=([], None)):
            response = client.get(
                '/tags/2026%3Csvg%20onload%3Dalert(1)%3E/'
                '%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E'
            )

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('&lt;svg', body)
        self.assertIn('&lt;img', body)
        self.assertNotIn('<svg', body)
        self.assertNotIn('<img', body)

    def test_invalid_score_entry_url_is_rejected_before_database_access(self):
        client = flask_app.app.test_client()
        with client.session_transaction() as session:
            session['csrf_token'] = 'test-token'

        with patch.object(flask_app, 'get_players') as get_players:
            response = client.post(
                '/newscoreentry',
                data={
                    'csrf_token': 'test-token',
                    'udisc_code': 'http://127.0.0.1/events/Event123',
                },
                headers={'Authorization': 'Basic dGVzdC11c2VyOnRlc3QtcGFzc3dvcmQ='},
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/newscoreentry', response.headers['Location'])
        get_players.assert_not_called()

    def test_authenticated_post_without_csrf_token_is_rejected(self):
        client = flask_app.app.test_client()
        with patch.object(flask_app, 'get_players') as get_players:
            response = client.post(
                '/newscoreentry',
                data={'udisc_code': 'https://udisc.com/events/Event123'},
                headers={'Authorization': 'Basic dGVzdC11c2VyOnRlc3QtcGFzc3dvcmQ='},
            )

        self.assertEqual(response.status_code, 400)
        get_players.assert_not_called()

    def test_authenticated_form_renders_session_csrf_token(self):
        client = flask_app.app.test_client()
        response = client.get(
            '/',
            headers={'Authorization': 'Basic dGVzdC11c2VyOnRlc3QtcGFzc3dvcmQ='},
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertRegex(
            body,
            r'<input type="hidden" name="csrf_token" value="[A-Za-z0-9_-]{40,}">',
        )

    def test_public_ctp_post_without_csrf_token_is_rejected(self):
        client = flask_app.app.test_client()
        with patch.object(flask_app, 'add_ctp') as add_ctp:
            response = client.post('/ctp/1', data={'new_name': 'Player'})

        self.assertEqual(response.status_code, 400)
        add_ctp.assert_not_called()


if __name__ == '__main__':
    unittest.main()
