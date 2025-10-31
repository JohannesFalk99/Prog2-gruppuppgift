import importlib
from flask import Flask
from pathlib import Path
import uuid
from functools import wraps
from flask import request, make_response, redirect, url_for, abort, current_app
import hashlib
from datetime import datetime


try:
    # prefer package-relative import when running as a package
    from .endpoints import require_admin
except ImportError:
    # fallback for direct script execution
    from endpoints import require_admin

try:
    # prefer package-relative import when running as a package
    from .config import get_config
except ImportError:
    # fallback for direct script execution
    from config import get_config

class Config:
    """Application configuration class"""
    SECRET_KEY = 'dev-secret-key-change-in-production'
    DEBUG = True
    TESTING = False

    @classmethod
    def init_app(cls, app):
        """Initialize application with configuration"""
        app.config.from_object(cls)

class FlaskApp:
    """Main Flask application class"""

    def __init__(self, config_class=None):
        if config_class is None:
            config_class = get_config()

        self.app = Flask(__name__)
        config_class.init_app(self.app)
        self._register_error_handlers()
        self._register_blueprints()
        self._register_routes()

    def _register_error_handlers(self):
        """Register error handlers"""
        try:
            from .error_handlers import ErrorHandler
        except ImportError:
            from error_handlers import ErrorHandler
        ErrorHandler.register_error_handlers(self.app)

    def _register_blueprints(self):
        """Register all blueprints from endpoints module"""
        try:
            # Try package-relative import first
            from . import endpoints as _endpoints
        except ImportError:
            # Fallback for direct script execution
            import endpoints as _endpoints

        # Register blueprints if they exist
        if hasattr(_endpoints, 'bp'):
            self.app.register_blueprint(_endpoints.bp)
        if hasattr(_endpoints, 'route_blueprint'):
            self.app.register_blueprint(_endpoints.route_blueprint)

        # Register routes via function if available
        if hasattr(_endpoints, 'register_routes'):
            _endpoints.register_routes(self.app)

    def _register_routes(self):
        """Register additional routes directly on the app"""
        try:
            from .cookie_manager import CookieManager
        except ImportError:
            from cookie_manager import CookieManager

        cookie_manager = CookieManager()

        @self.app.route("/")
        def index():
            consent = cookie_manager.has_consent()
            user_id = cookie_manager.get_user_id()
            # record a page view for this user (if DB available)
            try:
                cookie_manager.record_view()
            except Exception:
                pass
            from flask import render_template
            return render_template("index.html", consent=consent, user_id=user_id)

        # Cookie routes
        @self.app.route("/set")
        def set_cookie():
            return cookie_manager.accept_cookies()

        @self.app.route("/get")
        def get_cookie():
            from flask import request
            user_id = request.cookies.get("user_id")
            return f"user_id = {user_id}" if user_id else "NO cookies claimed!"

        @self.app.route("/delete")
        def delete_cookie():
            from flask import make_response
            resp = make_response("Cookie deleted!")
            resp.delete_cookie("user_id")
            return resp

        @self.app.route("/accept_cookies")
        def accept_cookies():
            return cookie_manager.accept_cookies()

        @self.app.route("/decline_cookies")
        def decline_cookies():
            return cookie_manager.decline_cookies()

        # Pandas route
        @self.app.route("/pandas")
        def pandas_view():
            import pandas_test
            graph_html = pandas_test.build_chart()
            from flask import render_template
            return render_template("pandas.html", graph_html=graph_html)

    def run(self, host='127.0.0.1', port=5000, debug=None):
        """Run the Flask application"""
        debug = debug if debug is not None else self.app.config['DEBUG']
        self.app.run(host=host, port=port, debug=debug)

# Create application instance
app = FlaskApp().app

if __name__ == '__main__':
    FlaskApp().run()

def set_cookie(response, key, value, days_expire=7):
    max_age = days_expire * 24 * 60 * 60
    response.set_cookie(key, value, max_age=max_age, httponly=True, samesite="Lax")
    return response

def get_cookie(key):
    return request.cookies.get(key)

def delete_cookie(response, key):
    response.delete_cookie(key)
    return response

def has_cookie_consent():
    return request.cookies.get("consent") == "true"

def accept_cookies():
    """Sätt consent=true och en unik användar-ID-cookie.

    Additionally attempt to persist a CookieRecord in the DB (if available).
    This mirrors the production `CookieManager.accept_cookies()` behavior so
    tests using this helper will exercise DB writes.
    """
    resp = make_response(redirect(url_for("index")))
    resp = set_cookie(resp, "consent", "true", days_expire=7)

    # Om ingen user_id finns, skapa en
    if not request.cookies.get("user_id"):
        user_id = str(uuid.uuid4())
        resp = set_cookie(resp, "user_id", user_id, days_expire=7)
        # attempt to persist cookie acceptance and fingerprint to DB
        try:
            # Ensure DB/tables exist and import session
            try:
                from . import models as _models
                _models.init_db()
                from .models import CookieRecord, get_session
            except Exception:
                import models as _models
                _models.init_db()
                from models import CookieRecord, get_session
            ua = request.headers.get('User-Agent')
            al = request.headers.get('Accept-Language')
            fp_src = (ua or '') + '|' + (al or '')
            fp_hash = hashlib.sha256(fp_src.encode('utf-8')).hexdigest()
            sess = get_session()
            cr = CookieRecord(id=str(uuid.uuid4()), user_id=user_id, user_agent=ua, accept_language=al, fingerprint_hash=fp_hash, views=0, annotations_count=0, created_at=datetime.utcnow(), last_seen=datetime.utcnow())
            sess.add(cr)
            sess.commit()
        except Exception:
            try:
                current_app.logger.debug('cookies_test.accept_cookies: DB not available or insert failed')
            except Exception:
                pass

    return resp

def decline_cookies():
    resp = make_response(redirect(url_for("index")))
    return set_cookie(resp, "consent", "false", days_expire=7)

def require_admin(f):
    """Decorator som spärrar endpoints om inte rätt admin-lösenord anges"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Hämta lösenord från query eller cookie
        password = request.args.get("password") or request.cookies.get("admin_auth")
        if password != "123":   # byt till något säkrare i skarp miljö
            abort(403)
        return f(*args, **kwargs)

    return decorated_function

def record_view():
    """Record a page view for the current user_id in the DB (if available).

    This mirrors the `CookieManager.record_view()` used by the main app so tests
    that call this helper will increment `views` and update `last_seen`.
    """
    try:
        uid = get_cookie('user_id')
        if not uid:
            return
        # ensure DB/tables exist
        try:
            from . import models as _models
            _models.init_db()
            from .models import CookieRecord, get_session
        except Exception:
            import models as _models
            _models.init_db()
            from models import CookieRecord, get_session
        sess = get_session()
        cr = sess.query(CookieRecord).filter(CookieRecord.user_id == uid).one_or_none()
        if cr:
            cr.views = (cr.views or 0) + 1
            cr.last_seen = datetime.utcnow()
            sess.commit()
    except Exception:
        try:
            current_app.logger.debug('cookies_test.record_view: DB write failed')
        except Exception:
            pass
        return
