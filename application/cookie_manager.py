import uuid
from flask import request, make_response, redirect, url_for

class CookieManager:
    """Manages cookie operations for the Flask application"""

    def __init__(self, consent_days=None, user_id_days=None):
        # Use config values if available, otherwise defaults
        try:
            from flask import current_app
            self.consent_days = consent_days or current_app.config.get('COOKIE_CONSENT_DAYS', 365)
            self.user_id_days = user_id_days or current_app.config.get('COOKIE_USER_ID_DAYS', 365)
        except RuntimeError:
            # Outside of app context
            self.consent_days = consent_days or 365
            self.user_id_days = user_id_days or 365

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

        return resp

    def decline_cookies(self):
        """Decline cookies by setting consent to false"""
        resp = make_response(redirect(url_for("index")))
        return self._set_cookie(resp, "consent", "false", self.consent_days)
