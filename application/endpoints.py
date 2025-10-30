from flask import request, Blueprint, jsonify, render_template, current_app, abort
from flask.views import MethodView 
from pathlib import Path
import json
import uuid
from functools import wraps 

try:
    # prefer package-relative import when running as a package
    from .services.elpriser_service import ElpriserService
    from .services.annotations_service import AnnotationsService
except Exception:
    # fallback for direct script runs
    from services.elpriser_service import ElpriserService
    from services.annotations_service import AnnotationsService

try:
    # prefer package-relative import when running as a package
    from .json_handler import JsonHandler
except Exception:
    # fallback for direct script runs
    from json_handler import JsonHandler

# Create blueprints
route_blueprint = Blueprint('routes', __name__)
bp = Blueprint('endpoints', __name__)

ALLOWED_PRISKLASSER = ['SE1', 'SE2', 'SE3', 'SE4']

# Try to use SQLAlchemy models if available
USE_DB = False
USE_SQLALCHEMY = False
try:
    from sqlalchemy import create_engine
    USE_SQLALCHEMY = True
except Exception as e:
    USE_SQLALCHEMY = False

if USE_SQLALCHEMY:
    try:
        from .models import Annotation, init_db, get_session
        # initialize DB lazily
        try:
            init_db()
            USE_DB = True
        except Exception as e:
            USE_DB = False
    except Exception as e:
        USE_DB = False
else:
    USE_DB = False

# Initialize services AFTER determining USE_DB
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANN_SERVICE = None  # Initialize later to avoid import issues

def get_annotations_service():
    """Lazy initialization of annotations service"""
    global ANN_SERVICE
    if ANN_SERVICE is None:
        try:
            from .services.annotations_service import AnnotationsService
        except Exception:
            from services.annotations_service import AnnotationsService
        ANN_SERVICE = AnnotationsService(PROJECT_ROOT, use_db=USE_DB)
    return ANN_SERVICE


class ExampleAPI(MethodView):
    """Example API endpoints for demonstration"""

    def get(self):
        return jsonify({"message": "This is a GET endpoint example"}), 200

    def post(self):
        data = request.get_json()
        return jsonify({"message": "This is a POST endpoint example", "data_received": data}), 200

    def put(self):
        data = request.get_json()
        return jsonify({"message": "This is a PUT endpoint example", "data_received": data}), 200

    def delete(self):
        return jsonify({"message": "This is a DELETE endpoint example"}), 200


class ElpriserAPI(MethodView):
    """API for fetching and managing electricity price data"""

    def get(self):
        """Fetch elpriser data"""
        return self._fetch_elpriser()

    def post(self):
        """Fetch elpriser data with parameters"""
        return self._fetch_elpriser()

    def _fetch_elpriser(self):
        data = request.get_json(silent=True) or {}
        prisklass = data.get('prisklass') or request.args.get('prisklass') or 'SE3'

        # Validate prisklass
        if prisklass not in ALLOWED_PRISKLASSER:
            return jsonify({"error": "Invalid prisklass", "allowed": ALLOWED_PRISKLASSER}), 422

        # Validate required date fields
        year = data.get('year') or request.args.get('year')
        month = data.get('month') or request.args.get('month')
        day = data.get('day') or request.args.get('day')

        missing = []
        if not year:
            missing.append('year')
        if not month:
            missing.append('month')
        if not day:
            missing.append('day')
        if missing:
            return jsonify({"error": "Missing required fields", "missing": missing}), 422

        # Use the ElpriserService to fetch/parse
        try:
            from .elpriser_api import ElpriserAPI as APIClass
        except Exception:
            from elpriser_api import ElpriserAPI as APIClass
        api = APIClass(year=year, month=month, day=day, prisklass=prisklass)
        priser = api.fetch_prices()

        if not priser:
            return jsonify({"error": "Failed to fetch elpriser data"}), 422

        # persist raw payload
        current_app.logger.debug('fetch_elpriser raw priser: %s', repr(priser)[:1000])
        json_handler = JsonHandler('elpriser_data.json')
        json_handler.write_json(priser)

        labels, values, summary = ElpriserService.parse_raw_payload(priser)

        # if caller requested debug, include the raw persisted payload as well
        if request.args.get('debug') in ('1', 'true', 'yes'):
            project_root = Path(__file__).resolve().parents[1]
            raw = ElpriserService.load_persisted(project_root)
            return jsonify({
                "message": "Elpriser data fetched and stored successfully (debug)",
                "prisklass": prisklass,
                "labels": labels,
                "values": values,
                "summary": summary,
                "raw_persisted": raw,
            }), 200

        return jsonify({"message": "Elpriser data fetched and stored successfully", "prisklass": prisklass, "labels": labels, "values": values, "summary": summary}), 200


class ElpriserView(MethodView):
    """View for displaying electricity price data"""

    def get(self):
        # Get date parameters (default to today if not provided)
        year = request.args.get('year')
        month = request.args.get('month')
        day = request.args.get('day')
        
        # Default to current date if no date provided
        if not all([year, month, day]):
            from datetime import datetime
            now = datetime.now()
            year = year or str(now.year)
            month = month or str(now.month).zfill(2)
            day = day or str(now.day).zfill(2)
        
        date_str = f"{year}-{month}-{day}"
        area = request.args.get('prisklass') or request.args.get('area') or 'SE3'
        
        # Load elpriser data
        project_root = Path(__file__).resolve().parents[1]
        raw = ElpriserService.load_persisted(project_root)
        if not raw:
            return render_template('elpriser.html', 
                                 labels=[], 
                                 values=[], 
                                 summary={}, 
                                 annotations=[],
                                 date=date_str,
                                 area=area)
        
        labels, values, summary = ElpriserService.parse_raw_payload(raw)
        
        # Fetch annotations for this date and area
        annotations = get_annotations_service().list(date=date_str, area=area)
        
        return render_template('elpriser.html', 
                             labels=labels, 
                             values=values, 
                             summary=summary,
                             annotations=annotations,
                             date=date_str,
                             area=area)

class ElpriserDataView(MethodView):
    """Serve the persisted elpriser_data.json"""

    def get(self):
        """Serve the persisted elpriser_data.json from project root."""
        project_root = Path(__file__).resolve().parents[1]
        json_path = project_root / 'elpriser_data.json'
        if not json_path.exists():
            return jsonify({"error": "elpriser_data.json not found"}), 404

        try:
            with json_path.open('r', encoding='utf-8') as fh:
                data = json.load(fh)
            return jsonify(data), 200
        except Exception as exc:
            current_app.logger.exception('Failed to read elpriser_data.json')
            return jsonify({"error": "Failed to read elpriser_data.json", "detail": str(exc)}), 500


class AnnotationsAPI(MethodView):
    """API for managing annotations"""

    def get(self):
        """Fetch annotations"""
        # accept date as single param or year/month/day triple
        date = request.args.get('date')
        if not date:
            y = request.args.get('year')
            m = request.args.get('month')
            d = request.args.get('day')
            if y and m and d:
                date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

        area = request.args.get('prisklass') or request.args.get('area')

        items = get_annotations_service().list(date=date, area=area)
        return jsonify({'annotations': items}), 200

    def post(self):
        """Create a new annotation"""
        data = request.get_json(silent=True) or {}
        text = data.get('text')
        date = data.get('date')
        area = data.get('area') or data.get('prisklass')
        author = data.get('author') or 'anonymous'

        if not text or not date or not area:
            return jsonify({'error': 'Missing required fields: text, date, area'}), 422

        ann = get_annotations_service().create(date=date, area=area, text=text, author=author)
        if not ann:
            return jsonify({'error': 'Failed to persist annotation'}), 500
        return jsonify({'annotation': ann}), 201


class AnnotationVoteAPI(MethodView):
    """API for voting on annotations"""

    def post(self, ann_id):
        """Vote on an annotation"""
        data = request.get_json(silent=True) or {}
        vote = data.get('vote')
        if vote not in ('like', 'dislike'):
            return jsonify({'error': "vote must be 'like' or 'dislike'"}), 422

        found = get_annotations_service().vote(ann_id, vote)
        if not found:
            return jsonify({'error': 'Annotation not found or vote failed'}), 404
        return jsonify({'annotation': found}), 200


class AnnotationModerateAPI(MethodView):
    """API for moderating annotations"""

    def put(self, ann_id):
        """Moderate an annotation"""
        data = request.get_json(silent=True) or {}
        action = data.get('action')
        if action not in ('remove', 'warn', 'restore'):
            return jsonify({'error': "action must be 'remove', 'warn' or 'restore'"}), 422

        found = get_annotations_service().moderate(ann_id, action)
        if not found:
            return jsonify({'error': 'Annotation not found or moderation failed'}), 404
        return jsonify({'annotation': found}), 200


# Register class-based views
route_blueprint.add_url_rule('/GetExample', view_func=ExampleAPI.as_view('get_example'))
route_blueprint.add_url_rule('/PostExample', view_func=ExampleAPI.as_view('post_example'))
route_blueprint.add_url_rule('/PutExample', view_func=ExampleAPI.as_view('put_example'))
route_blueprint.add_url_rule('/DeleteExample', view_func=ExampleAPI.as_view('delete_example'))

route_blueprint.add_url_rule('/fetch_elpriser', view_func=ElpriserAPI.as_view('fetch_elpriser'))
route_blueprint.add_url_rule('/elpriser', view_func=ElpriserView.as_view('elpriser_view'))
route_blueprint.add_url_rule('/elpriser_data.json', view_func=ElpriserDataView.as_view('serve_elpriser_json'))

route_blueprint.add_url_rule('/annotations', view_func=AnnotationsAPI.as_view('annotations'))
route_blueprint.add_url_rule('/annotations/<ann_id>/vote', view_func=AnnotationVoteAPI.as_view('vote_annotation'))
route_blueprint.add_url_rule('/annotations/<ann_id>/moderate', view_func=AnnotationModerateAPI.as_view('moderate_annotation'))

# Register traditional function-based routes
@bp.route('/data')
def data():
    return render_template('data.html')

@bp.route('/profile')
def profile():
    return render_template('profile.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@bp.route('/settings')
def settings():
    return render_template('settings.html')

# Optional: support function-based registration if preferred
def register_routes(app):
    # bp is already registered by FlaskApp._register_blueprints()
    # app.register_blueprint(bp)
    pass

# endpoints.py
from functools import wraps
from flask import request, abort

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        password = request.args.get("password") or request.cookies.get("admin_auth")
        if password != "123":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
