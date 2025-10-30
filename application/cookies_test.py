import uuid
from flask import request, make_response, redirect, url_for

def set_cookie(response, key, value, days_expire=365):
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
    """Sätt consent=true och en unik användar-ID-cookie"""
    resp = make_response(redirect(url_for("index")))
    resp = set_cookie(resp, "consent", "true", days_expire=365)

    # Om ingen user_id finns, skapa en
    if not request.cookies.get("user_id"):
        user_id = str(uuid.uuid4())
        resp = set_cookie(resp, "user_id", user_id, days_expire=365)

    return resp

def decline_cookies():
    resp = make_response(redirect(url_for("index")))
    return set_cookie(resp, "consent", "false", days_expire=365)
