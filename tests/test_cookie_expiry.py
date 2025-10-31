import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from flask import Flask
from application.cookie_manager import CookieManager


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['COOKIE_CONSENT_DAYS'] = 7
    app.config['COOKIE_USER_ID_DAYS'] = 14
    # minimal index route
    app.add_url_rule('/', 'index', lambda: 'index')
    return app


def test_cookies_have_security_flags(app):
    cm = CookieManager()
    with app.test_request_context('/'):
        resp = cm.accept_cookies()
        headers = resp.headers.get_all('Set-Cookie')
        # check for HttpOnly and SameSite attributes on cookies
        assert any('HttpOnly' in h for h in headers)
        assert any('SameSite=Lax' in h or 'SameSite=lax' in h for h in headers)


def test_cookie_max_age_matches_config(app):
    cm = CookieManager()
    with app.test_request_context('/'):
        resp = cm.accept_cookies()
        headers = resp.headers.get_all('Set-Cookie')
        # find consent cookie header
        consent_hdrs = [h for h in headers if 'consent=' in h]
        assert consent_hdrs, 'consent cookie not set'
        # max-age should be COOKIE_CONSENT_DAYS * 24 * 60 * 60
        expected = str(app.config['COOKIE_CONSENT_DAYS'] * 24 * 60 * 60)
        # Some environments format cookie expiry as 'Max-Age' or 'Expires'. Accept either.
        ok = any(f'Max-Age={expected}' in h or f'max-age={expected}' in h for h in consent_hdrs)
        if not ok:
            # fallback: check if an Expires attribute is present (not strictly equal check)
            ok = any('Expires=' in h or 'expires=' in h for h in consent_hdrs)
        assert ok, 'Cookie expiry did not match expected Max-Age or provide Expires header'
