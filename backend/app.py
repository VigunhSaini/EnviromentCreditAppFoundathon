"""
app.py
Flask application factory for the Environmental Credits Platform backend.

Usage:
    python app.py              # development server
    flask --app app run        # alternative

Production:
    gunicorn -w 4 "app:create_app()"
"""
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config


def create_app(config_object: type = Config) -> Flask:
    """
    Application factory.

    Args:
        config_object: A config class (defaults to :class:`Config`).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # ------------------------------------------------------------------
    # CORS
    # Allow all origins in development; tighten in production via env var.
    # ------------------------------------------------------------------
    CORS(app, resources={r"/*": {"origins": "*"}})

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from routes.projects import projects_bp
    from routes.verification import verification_bp
    from routes.credits import credits_bp
    from routes.marketplace import marketplace_bp

    app.register_blueprint(projects_bp)
    app.register_blueprint(verification_bp)
    app.register_blueprint(credits_bp)
    app.register_blueprint(marketplace_bp)

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "Environmental Credits API"}), 200

    # ------------------------------------------------------------------
    # Global error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(err):
        return jsonify({"success": False, "error": "Bad request", "detail": str(err)}), 400

    @app.errorhandler(404)
    def not_found(err):
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(err):
        return jsonify({"success": False, "error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
    )
