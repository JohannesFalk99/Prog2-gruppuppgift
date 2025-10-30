from flask import Flask
import application.endpoints as endpoints

# Create a minimal Flask app that uses the repository templates directory
app = Flask(__name__, template_folder='application/templates')
# register blueprints defined in endpoints so url_for(...) in templates works
if hasattr(endpoints, 'bp'):
    try:
        app.register_blueprint(endpoints.bp)
    except Exception:
        pass
if hasattr(endpoints, 'route_blueprint'):
    try:
        app.register_blueprint(endpoints.route_blueprint)
    except Exception:
        pass

with app.test_request_context('/'):
    resp = endpoints.elpriser_view()
    if isinstance(resp, str):
        print('RENDERED_CHARS:', len(resp))
    else:
        try:
            print('RENDERED_CHARS:', len(resp.get_data(as_text=True)))
        except Exception:
            print('RENDERED_TYPE:', type(resp))
