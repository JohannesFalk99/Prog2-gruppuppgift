import uuid
from flask import request, make_response, redirect, url_for, current_app
import hashlib
from pathlib import Path
from datetime import datetime

class CookieManager:
    """Manages cookie operations for the Flask application"""

    def __init__(self, consent_days=None, user_id_days=None):
        # Use config values if available, otherwise defaults
        try:
            from flask import current_app
            # Default cookie lifetimes changed to 7 days for assignment
            self.consent_days = consent_days or current_app.config.get('COOKIE_CONSENT_DAYS', 7)
            self.user_id_days = user_id_days or current_app.config.get('COOKIE_USER_ID_DAYS', 7)
        except RuntimeError:
            # Outside of app context
            self.consent_days = consent_days or 7
            self.user_id_days = user_id_days or 7

    def _set_cookie(self, response, key, value, days_expire=None):
        """Set a cookie with proper security settings"""
        if days_expire is None:
            days_expire = self.consent_days
        max_age = days_expire * 24 * 60 * 60
        response.set_cookie(key, value, max_age=max_age, httponly=True, samesite="Lax")
        return response

    def get_cookie(self, key):
        """Get a cookie value"""
        return request.cookies.get(key)

    def delete_cookie(self, response, key):
        """Delete a cookie"""
        response.delete_cookie(key)
        return response

    def has_consent(self):
        """Check if user has given cookie consent"""
        return self.get_cookie("consent") == "true"

    def get_user_id(self):
        """Get the user's ID from cookies"""
        return self.get_cookie("user_id")

    def accept_cookies(self):
        """Accept cookies and set consent + user ID"""
        resp = make_response(redirect(url_for("index")))
        resp = self._set_cookie(resp, "consent", "true", self.consent_days)

        # Create user ID if it doesn't exist
        if not self.get_user_id():
            user_id = str(uuid.uuid4())
            resp = self._set_cookie(resp, "user_id", user_id, self.user_id_days)
            # attempt to persist cookie acceptance and fingerprint to DB
            try:
                from .models import CookieRecord, get_session
                ua = request.headers.get('User-Agent')
                al = request.headers.get('Accept-Language')
                # lightweight fingerprint: hash of user-agent + accept-language
                fp_src = (ua or '') + '|' + (al or '')
                fp_hash = hashlib.sha256(fp_src.encode('utf-8')).hexdigest()
                sess = get_session()
                cr = CookieRecord(id=str(uuid.uuid4()), user_id=user_id, user_agent=ua, accept_language=al, fingerprint_hash=fp_hash, views=0, annotations_count=0, created_at=datetime.utcnow(), last_seen=datetime.utcnow())
                sess.add(cr)
                sess.commit()
            except Exception:
                # DB not available or commit failed; ignore and proceed
                current_app.logger.debug('CookieManager: DB not available or failed to persist CookieRecord')
                pass

        return resp

    def decline_cookies(self):
        """Decline cookies by setting consent to false"""
        resp = make_response(redirect(url_for("index")))
        return self._set_cookie(resp, "consent", "false", self.consent_days)

    def record_view(self):
        """Record a page view for the current user_id in the DB (if available).

        This will increment `views` and update `last_seen` for the CookieRecord
        associated with the current `user_id` cookie.
        """
        try:
            uid = self.get_user_id()
            if not uid:
                return
            from .models import CookieRecord, get_session
            sess = get_session()
            cr = sess.query(CookieRecord).filter(CookieRecord.user_id == uid).one_or_none()
            if cr:
                # tolerate None values
                cr.views = (cr.views or 0) + 1
                cr.last_seen = datetime.utcnow()
                sess.commit()
        except Exception:
            # DB not available or write failed; do not raise
            try:
                current_app.logger.debug('CookieManager.record_view: DB write failed')
            except Exception:
                pass
            return
