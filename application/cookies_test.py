def set_cookie(response, key, value, days_expire=7):
    """Stub: implemented in app.py"""
    pass

def get_cookie(key):
    """Stub: implemented in app.py"""
    pass

def delete_cookie(response, key):
    """Stub: implemented in app.py"""
    pass

def has_cookie_consent():
    """Stub: implemented in app.py"""
    pass

def accept_cookies():
    """Stub: implemented in app.py"""
    pass

def decline_cookies():
    """Stub: implemented in app.py"""
    pass

def require_admin(f):
    """Stub: implemented in app.py"""
    pass

def record_view():
    """Stub: implemented in app.py"""
    pass
    
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
