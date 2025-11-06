import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from flask import Flask

# Import require_admin from application endpoints
from application.endpoints import require_admin


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True

    @app.route('/')
    def index():
        return 'ok'

    @app.route('/admin-test')
    @require_admin
    def admin_view():
        return 'admin'

    return app


def test_require_admin_blocks_without_password(app):
    client = app.test_client()
    r = client.get('/admin-test')
    assert r.status_code == 403


def test_require_admin_allows_with_query_password(app):
    client = app.test_client()
    r = client.get('/admin-test?password=123')
    assert r.status_code == 200
    assert r.get_data(as_text=True) == 'admin'


def test_require_admin_allows_with_cookie(app):
    client = app.test_client()
    # set cookie admin_auth=123 (Flask client.set_cookie signature accepts key, value)
    client.set_cookie('admin_auth', '123')
    r = client.get('/admin-test')
    assert r.status_code == 200
    assert r.get_data(as_text=True) == 'admin'
