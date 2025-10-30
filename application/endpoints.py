from flask import request, Blueprint, jsonify, render_template 
from flask import Blueprint, render_template, current_app
from pathlib import Path
import json
import uuid

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

route_blueprint = Blueprint('routes', __name__)
ALLOWED_PRISKLASSER = ['SE1', 'SE2', 'SE3', 'SE4']

#Return 200, 422, 404
@route_blueprint.route('/GetExample', methods=['GET'])
def get_example():

    return jsonify({"message": "This is a GET endpoint example"}), 200

    #Failure 
    return jsonify({"error": "This is a GET endpoint failure example"}), 404


@route_blueprint.route('/PostExample', methods=['POST'])
def post_example():
    data = request.get_json()

    return jsonify({"message": "This is a POST endpoint example", "data_received": data}) 
    #Failure event
    return jsonify({"error": "This is a POST endpoint failure example"}), 422


@route_blueprint.route('/PutExample', methods=['PUT'])
def put_example(): 
    data = request.get_json()
    return jsonify({"message": "This is a PUT endpoint example", "data_received": data})
    #Failure event
    return jsonify({"error": "This is a PUT endpoint failure example"}), 422


@route_blueprint.route('/DeleteExample', methods=['DELETE'])
def delete_example():
    return jsonify({"message": "This is a DELETE endpoint example"})
    #Failure event
    return jsonify({"error": "This is a DELETE endpoint failure example"}), 404


#Endpoint for elpriser API data fetch and store in JSON file, take date and area code as input 
@route_blueprint.route('/fetch_elpriser', methods=['POST','GET'])
def fetch_elpriser():
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

    # Use the ElpriserService to fetch/parse (ElpriserAPI still used to fetch raw data)
    try:
        from .elpriser_api import ElpriserAPI
    except Exception:
        from elpriser_api import ElpriserAPI
    api = ElpriserAPI(year=year, month=month, day=day, prisklass=prisklass)
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
#Do something different with the data

bp = Blueprint('endpoints', __name__)

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

@route_blueprint.route('/elpriser')
def elpriser_view():
    # locate project root and JSON file
    project_root = Path(__file__).resolve().parents[1]
    raw = ElpriserService.load_persisted(project_root)
    if not raw:
        return "elpriser_data.json not found", 404
    labels, values, summary = ElpriserService.parse_raw_payload(raw)
    return render_template('elpriser.html', labels=labels, values=values, summary=summary)


@route_blueprint.route('/elpriser_data.json', methods=['GET'])
def serve_elpriser_json():
    """Serve the persisted elpriser_data.json from project root.

    This makes it easy for the client to fetch the last-saved payload.
    Returns 404 if file is missing and 500 on read errors.
    """
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


# -------------------- Annotations API --------------------
def _annotations_path():
    project_root = Path(__file__).resolve().parents[1]
    return project_root / 'annotations.json'


def _load_annotations():
    p = _annotations_path()
    if not p.exists():
        return []
    try:
        with p.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
            # expect a list
            return data if isinstance(data, list) else []
    except Exception:
        current_app.logger.exception('Failed to load annotations.json')
        return []


def _save_annotations(items):
    p = _annotations_path()
    try:
        with p.open('w', encoding='utf-8') as fh:
            json.dump(items, fh, ensure_ascii=False, indent=2)
        return True
    except Exception:
        current_app.logger.exception('Failed to save annotations.json')
        return False


# Try to use SQLAlchemy models if available. If not, continue using file fallback
USE_DB = False
try:
    from .models import Annotation, init_db, get_session
    # initialize DB lazily
    try:
        init_db()
        USE_DB = True
    except Exception:
        current_app.logger.exception('Failed to initialize DB; falling back to JSON file')
        USE_DB = False
except Exception:
    # models not available or SQLAlchemy not installed
    USE_DB = False

# create annotations service instance (file-based by default)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANN_SERVICE = AnnotationsService(PROJECT_ROOT)


@route_blueprint.route('/annotations', methods=['GET'])
def get_annotations():
    """Fetch annotations. Optional query params: date=YYYY-MM-DD, year/month/day, prisklass/area."""
    # accept date as single param or year/month/day triple
    date = request.args.get('date')
    if not date:
        y = request.args.get('year')
        m = request.args.get('month')
        d = request.args.get('day')
        if y and m and d:
            date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    area = request.args.get('prisklass') or request.args.get('area')

    if USE_DB:
        try:
            sess = get_session()
            q = sess.query(Annotation)
            if date:
                q = q.filter(Annotation.date == date)
            if area:
                q = q.filter(Annotation.area == area)
            rows = q.all()
            items = []
            for r in rows:
                items.append({
                    'id': r.id,
                    'date': r.date,
                    'area': r.area,
                    'text': r.text,
                    'author': r.author,
                    'created_at': r.created_at.isoformat() if r.created_at else None,
                    'likes': r.likes,
                    'dislikes': r.dislikes,
                    'status': r.status,
                })
            return jsonify({'annotations': items}), 200
        except Exception:
            current_app.logger.exception('DB query failed in get_annotations')
            return jsonify({'error': 'DB query failed'}), 500

    items = ANN_SERVICE.list(date=date, area=area)
    return jsonify({'annotations': items}), 200


@route_blueprint.route('/annotations', methods=['POST'])
def post_annotation():
    """Create a new annotation. JSON body: {date: 'YYYY-MM-DD', area: 'SE3', text: '', author: ''}
    Returns created annotation with id, timestamps, likes/dislikes and status."""
    data = request.get_json(silent=True) or {}
    text = data.get('text')
    date = data.get('date')
    area = data.get('area') or data.get('prisklass')
    author = data.get('author') or 'anonymous'

    if not text or not date or not area:
        return jsonify({'error': 'Missing required fields: text, date, area'}), 422

    if USE_DB:
        try:
            sess = get_session()
            a = Annotation(
                id=str(uuid.uuid4()),
                date=date,
                area=area,
                text=text,
                author=author,
                likes=0,
                dislikes=0,
                status='active'
            )
            sess.add(a)
            sess.commit()
            return jsonify({'annotation': {
                'id': a.id,
                'date': a.date,
                'area': a.area,
                'text': a.text,
                'author': a.author,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'likes': a.likes,
                'dislikes': a.dislikes,
                'status': a.status,
            }}), 201
        except Exception:
            current_app.logger.exception('Failed to persist annotation to DB')
            return jsonify({'error': 'Failed to persist annotation to DB'}), 500

    ann = ANN_SERVICE.create(date=date, area=area, text=text, author=author)
    if not ann:
        return jsonify({'error': 'Failed to persist annotation'}), 500
    return jsonify({'annotation': ann}), 201


@route_blueprint.route('/annotations/<ann_id>/vote', methods=['POST'])
def vote_annotation(ann_id):
    """Vote on an annotation. JSON body: {vote: 'like'|'dislike'}"""
    data = request.get_json(silent=True) or {}
    vote = data.get('vote')
    if vote not in ('like', 'dislike'):
        return jsonify({'error': "vote must be 'like' or 'dislike'"}), 422

    if USE_DB:
        try:
            sess = get_session()
            a = sess.query(Annotation).filter(Annotation.id == ann_id).one_or_none()
            if not a:
                return jsonify({'error': 'Annotation not found'}), 404
            if vote == 'like':
                a.likes = (a.likes or 0) + 1
            else:
                a.dislikes = (a.dislikes or 0) + 1

            d = int(a.dislikes or 0)
            if d >= 5:
                a.status = 'removed'
            elif d >= 3:
                a.status = 'warning'
            else:
                if a.status in ('warning', 'removed') and d < 3:
                    a.status = 'active'

            sess.commit()
            return jsonify({'annotation': {
                'id': a.id,
                'date': a.date,
                'area': a.area,
                'text': a.text,
                'author': a.author,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'likes': a.likes,
                'dislikes': a.dislikes,
                'status': a.status,
            }}), 200
        except Exception:
            current_app.logger.exception('DB vote failed')
            return jsonify({'error': 'DB vote failed'}), 500

    found = ANN_SERVICE.vote(ann_id, vote)
    if not found:
        return jsonify({'error': 'Annotation not found or vote failed'}), 404
    return jsonify({'annotation': found}), 200


@route_blueprint.route('/annotations/<ann_id>/moderate', methods=['PUT'])
def moderate_annotation(ann_id):
    """Manual moderation endpoint. JSON body: {action: 'remove'|'warn'|'restore'}"""
    data = request.get_json(silent=True) or {}
    action = data.get('action')
    if action not in ('remove', 'warn', 'restore'):
        return jsonify({'error': "action must be 'remove', 'warn' or 'restore'"}), 422

    if USE_DB:
        try:
            sess = get_session()
            a = sess.query(Annotation).filter(Annotation.id == ann_id).one_or_none()
            if not a:
                return jsonify({'error': 'Annotation not found'}), 404
            if action == 'remove':
                a.status = 'removed'
            elif action == 'warn':
                a.status = 'warning'
            else:
                a.status = 'active'
            sess.commit()
            return jsonify({'annotation': {
                'id': a.id,
                'date': a.date,
                'area': a.area,
                'text': a.text,
                'author': a.author,
                'created_at': a.created_at.isoformat() if a.created_at else None,
                'likes': a.likes,
                'dislikes': a.dislikes,
                'status': a.status,
            }}), 200
        except Exception:
            current_app.logger.exception('DB moderate failed')
            return jsonify({'error': 'DB moderate failed'}), 500

    found = ANN_SERVICE.moderate(ann_id, action)
    if not found:
        return jsonify({'error': 'Annotation not found or moderation failed'}), 404
    return jsonify({'annotation': found}), 200


# Optional: support function-based registration if preferred
def register_routes(app):
	app.register_blueprint(bp)