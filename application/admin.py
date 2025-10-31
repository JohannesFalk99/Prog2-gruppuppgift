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

    if CookieRecord and get_session:
        try:
            sess = get_session()
            qs = sess.query(CookieRecord).order_by(CookieRecord.created_at.desc()).limit(limit).all()
            for r in qs:
                records.append({
                    'id': r.id,
                    'user_id': r.user_id,
                    'user_agent': r.user_agent,
                    'accept_language': r.accept_language,
                    'fingerprint_hash': r.fingerprint_hash,
                    'created_at': r.created_at,
                    'last_seen': getattr(r, 'last_seen', None)
                })
            try:
                stats['cookie_count'] = sess.query(CookieRecord).count()
            except Exception:
                stats['cookie_count'] = len(records)
        except Exception:
            # DB query failed; keep records empty
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
