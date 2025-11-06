from pathlib import Path
import json

def get_admin_dashboard_data(project_root: Path = None, limit: int = 200):
    """Return a dict with records, annotations and stats for the admin dashboard.

    This helper isolates DB access and JSON fallback logic so route handlers stay
    small and focused.
    """
    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]

    records = []
    annotations = []
    stats = {
        'cookie_count': 0,
        'annotation_count': 0,
    }

    # Try to load cookie records from DB if available
    try:
        from .models import CookieRecord, Annotation, get_session
    except Exception:
        try:
            from models import CookieRecord, Annotation, get_session
        except Exception:
            CookieRecord = None
            Annotation = None
            get_session = None

    # Always try JSON fallback first since we know DB is not working with Python 3.13
    try:
        cookie_records_file = project_root / "cookie_records.json"
        if cookie_records_file.exists():
            with open(cookie_records_file, 'r', encoding='utf-8') as f:
                json_records = json.load(f)
                for r in json_records:
                    # Trim data for better display
                    user_id = r.get('user_id', '')
                    fingerprint = r.get('fingerprint_hash', '')
                    user_agent = r.get('user_agent', '')
                    
                    records.append({
                        'id': r.get('id'),
                        'user_id': user_id[:5] + '...' if len(user_id) > 5 else user_id,
                        'user_id_full': user_id,  # Keep full for tooltip or details
                        'user_agent': user_agent[:50] + '...' if len(user_agent) > 50 else user_agent,
                        'user_agent_full': user_agent,  # Keep full for tooltip
                        'accept_language': r.get('accept_language'),
                        'fingerprint_hash': fingerprint[:8] + '...' if len(fingerprint) > 8 else fingerprint,
                        'fingerprint_full': fingerprint,  # Keep full for tooltip
                        'created_at': r.get('created_at'),
                        'last_seen': r.get('last_seen'),
                        'views': r.get('views', 0),
                        'annotations_count': r.get('annotations_count', 0)
                    })
                stats['cookie_count'] = len(records)
                print(f"DEBUG: Loaded {len(records)} records from JSON") # Debug output
    except Exception as e:
        print(f"DEBUG: JSON fallback failed: {e}")  # Debug output
        
    # If JSON didn't work, try DB as secondary fallback
    if not records and CookieRecord and get_session:
        try:
            sess = get_session()
            qs = sess.query(CookieRecord).order_by(CookieRecord.created_at.desc()).limit(limit).all()
            for r in qs:
                # Trim data for better display
                user_id = r.user_id or ''
                fingerprint = r.fingerprint_hash or ''
                user_agent = r.user_agent or ''
                
                records.append({
                    'id': r.id,
                    'user_id': user_id[:5] + '...' if len(user_id) > 5 else user_id,
                    'user_id_full': user_id,  # Keep full for tooltip
                    'user_agent': user_agent[:50] + '...' if len(user_agent) > 50 else user_agent,
                    'user_agent_full': user_agent,  # Keep full for tooltip
                    'accept_language': r.accept_language,
                    'fingerprint_hash': fingerprint[:8] + '...' if len(fingerprint) > 8 else fingerprint,
                    'fingerprint_full': fingerprint,  # Keep full for tooltip
                    'created_at': r.created_at,
                    'last_seen': getattr(r, 'last_seen', None),
                    'views': getattr(r, 'views', 0),
                    'annotations_count': getattr(r, 'annotations_count', 0)
                })
            try:
                stats['cookie_count'] = sess.query(CookieRecord).count()
            except Exception:
                stats['cookie_count'] = len(records)
            print(f"DEBUG: Loaded {len(records)} records from DB") # Debug output
        except Exception as e:
            print(f"DEBUG: DB fallback failed: {e}")  # Debug output
            records = []

    # Load annotations (prefer service to support JSON fallback)
    try:
        try:
            from .services.annotations_service import AnnotationsService
        except Exception:
            from services.annotations_service import AnnotationsService

        svc = AnnotationsService(project_root, use_db=(get_session is not None))
        annotations = svc.list()
        stats['annotation_count'] = len(annotations)
    except Exception:
        # fallback: read annotations.json directly
        try:
            p = project_root / 'annotations.json'
            if p.exists():
                with p.open('r', encoding='utf-8') as fh:
                    loaded = json.load(fh)
                    annotations = loaded if isinstance(loaded, list) else []
                    stats['annotation_count'] = len(annotations)
        except Exception:
            annotations = []

    return {
        'records': records,
        'annotations': annotations,
        'stats': stats,
    }
