import importlib
from flask import Flask, render_template, request, make_response
import pandas_test
import cookies_test as ct

app = Flask(__name__)

# How to use blueprints:
# - Create a module `endpoints.py` next to this file.
# - In that module export a Blueprint named `bp`, e.g.:
#     from flask import Blueprint, render_template
#     bp = Blueprint('endpoints', __name__)
#     @bp.route('/data')
#     def data(): return render_template('data.html')
# - This app will automatically import `endpoints` and register `bp`.

# Register endpoints from endpoints.py (supports Blueprint 'bp' or function 'register_routes'
# or module-level route decorators). Tries relative import first, then absolute.
try:
	# same-package import (when application is a package)
	from . import endpoints as _endpoints
except Exception:
	try:
		import endpoints as _endpoints
	except Exception:
		_endpoints = None

if _endpoints:
	if hasattr(_endpoints, 'bp'):
		app.register_blueprint(_endpoints.bp)
	elif hasattr(_endpoints, 'register_routes'):
		_endpoints.register_routes(app)
	else:
		# module-level decorators will have been registered on import
		pass

	# If endpoints defines a blueprint named 'route_blueprint', register it as well
	if hasattr(_endpoints, 'route_blueprint'):
		app.register_blueprint(_endpoints.route_blueprint)

@app.route("/")
def index():
    consent = ct.has_cookie_consent()
    user_id = ct.get_cookie("user_id")
    return render_template("index.html", consent=consent, user_id=user_id)

# @app.route('/data')
# def data():
#     return render_template('data.html')

# @app.route('/profile')
# def profile():
#     return render_template('profile.html')

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html')

#e

# @app.route('/settings')
# def settings():
#     return render_template('settings.html')
#how to use blueprints?


# ----- Cookie stuff ----- #
@app.route("/set")
def set_cookie():
    return ct.accept_cookies()

@app.route("/get")
def get_cookie():
    user_id = request.cookies.get("user_id")
    return f"user_id = {user_id}" if user_id else "NO cookies claimed!"

@app.route("/delete")
def delete_cookie():
    resp = make_response("Cookie deleted!")
    resp.delete_cookie("user_id")
    return resp

@app.route("/accept_cookies")
def set_cookie_route():
    return ct.accept_cookies()
#Ta bort alla cookies
@app.route("/decline_cookies")
def decline_cookies():
    return ct.decline_cookies()
#-------------------------------#

# ----- pandas test ----- #
@app.route("/pandas")
def pandas_view():
    graph_html = pandas_test.build_chart()   
    return render_template("pandas.html", graph_html=graph_html)


if __name__ == '__main__':
	app.run(debug=True)
