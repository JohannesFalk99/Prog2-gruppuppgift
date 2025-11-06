import sys
from pathlib import Path
import pytest
from flask import Flask

# ensure project root is on sys.path so tests can import application package
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from application.cookie_manager import CookieManager


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['COOKIE_CONSENT_DAYS'] = 7
    app.config['COOKIE_USER_ID_DAYS'] = 7
    # provide a minimal index route so url_for('index') resolves in tests
    app.add_url_rule('/', 'index', lambda: 'index')
    return app


def test_accept_cookies_sets_consent_and_user_id(app):
    cm = CookieManager()
    with app.test_request_context('/'):
        resp = cm.accept_cookies()
        # Cookies are set on response headers
        header = resp.headers.get_all('Set-Cookie')
        assert any('consent=true' in h for h in header)
        assert any('user_id=' in h for h in header)


def test_decline_cookies_sets_consent_false(app):
    cm = CookieManager()
    with app.test_request_context('/'):
        resp = cm.decline_cookies()
        header = resp.headers.get_all('Set-Cookie')
        assert any('consent=false' in h for h in header)


def test_get_and_delete_cookie(app):
    cm = CookieManager()
    with app.test_request_context('/', headers={'Cookie': 'user_id=abc123'}):
        # get_user_id reads from request cookies
        assert cm.get_user_id() == 'abc123'

        # delete_cookie expects a response object; ensure cookie removed
        from flask import make_response
        resp = make_response('ok')
        resp = cm.delete_cookie(resp, 'user_id')
        header = resp.headers.get_all('Set-Cookie')
        # Deleting cookie will set cookie with expiration in the past or empty value
        assert any('user_id=' in h for h in header)
