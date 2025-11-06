import importlib
from flask import Flask
from pathlib import Path


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

        # Register all cookie routes via CookieManager
        CookieManager.register_routes(self.app)

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
