import time
import unittest
from datetime import timedelta
from unittest.mock import patch

from flask import Flask
from itsdangerous import TimestampSigner

from auth import requires_auth


class AuthSessionTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            SECRET_KEY='test-secret',
            SITE_USER='league-user',
            SITE_PASSWORD='league-password',
            PERMANENT_SESSION_LIFETIME=timedelta(hours=3),
            SESSION_COOKIE_NAME='bcss_session',
            SESSION_COOKIE_PATH='/',
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            SESSION_COOKIE_SECURE=True,
            SESSION_REFRESH_EACH_REQUEST=False,
        )

        @self.app.get('/private')
        @requires_auth
        def private():
            return 'private content'

        self.client = self.app.test_client()

    def test_basic_auth_starts_three_hour_session_and_cookie_reuses_it(self):
        unauthorized = self.client.get('/private')
        self.assertEqual(unauthorized.status_code, 401)
        self.assertIn('WWW-Authenticate', unauthorized.headers)

        authenticated = self.client.get(
            '/private',
            headers={'Authorization': 'Basic bGVhZ3VlLXVzZXI6bGVhZ3VlLXBhc3N3b3Jk'},
        )
        self.assertEqual(authenticated.status_code, 200)
        cookie = authenticated.headers['Set-Cookie']
        self.assertIn('bcss_session=', cookie)
        self.assertIn('Path=/', cookie)
        self.assertIn('Secure', cookie)
        self.assertIn('HttpOnly', cookie)
        self.assertIn('SameSite=Lax', cookie)

        remembered = self.client.get('/private')
        self.assertEqual(remembered.status_code, 200)
        self.assertNotIn('Set-Cookie', remembered.headers)

    def test_session_signed_more_than_three_hours_ago_is_rejected(self):
        serializer = self.app.session_interface.get_signing_serializer(self.app)
        with patch.object(
            TimestampSigner,
            'get_timestamp',
            return_value=int(time.time()) - 3 * 60 * 60 - 1,
        ):
            expired_cookie = serializer.dumps({
                '_permanent': True,
                'bcss_authenticated': True,
            })

        self.client.set_cookie('bcss_session', expired_cookie)
        response = self.client.get('/private')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
