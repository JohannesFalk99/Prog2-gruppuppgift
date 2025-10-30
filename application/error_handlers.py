from flask import jsonify, render_template, current_app, request
import logging

class ErrorHandler:
    """Centralized error handling for the Flask application"""

    @staticmethod
    def register_error_handlers(app):
        """Register all error handlers with the Flask app"""

        @app.errorhandler(400)
        def bad_request(error):
            return ErrorHandler._json_error(400, "Bad Request", str(error))

        @app.errorhandler(401)
        def unauthorized(error):
            return ErrorHandler._render_error_page(401, "Unauthorized")

        @app.errorhandler(403)
        def forbidden(error):
            return ErrorHandler._render_error_page(403, "Forbidden")

        @app.errorhandler(404)
        def not_found(error):
            return ErrorHandler._render_error_page(404, "Page Not Found")

        @app.errorhandler(422)
        def unprocessable_entity(error):
            return ErrorHandler._json_error(422, "Unprocessable Entity", str(error))

        @app.errorhandler(500)
        def internal_server_error(error):
            current_app.logger.exception("Internal server error")
            return ErrorHandler._render_error_page(500, "Internal Server Error")

        @app.errorhandler(Exception)
        def handle_unexpected_error(error):
            current_app.logger.exception(f"Unexpected error: {error}")
            return ErrorHandler._render_error_page(500, "Internal Server Error")

    @staticmethod
    def _json_error(status_code, message, detail=None):
        """Return JSON error response for API requests"""
        if request.path.startswith('/api/') or request.is_json:
            response = {'error': message}
            if detail:
                response['detail'] = detail
            return jsonify(response), status_code
        else:
            # For non-API requests, render HTML error page
            return ErrorHandler._render_error_page(status_code, message)

    @staticmethod
    def _render_error_page(status_code, message):
        """Render HTML error page"""
        try:
            return render_template(f'{status_code}.html'), status_code
        except Exception:
            # Fallback if custom error template doesn't exist
            return render_template('error.html', error_code=status_code, error_message=message), status_code


class APIError(Exception):
    """Custom exception for API errors"""

    def __init__(self, message, status_code=400, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


def handle_api_error(error):
    """Handle APIError exceptions"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
