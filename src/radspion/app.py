"""Flask application entry point."""

import sys

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from radspion.config import Config, ConfigurationError, load_config
from radspion.database import DatabaseError, DatabaseRadspionStorage
from radspion.google_oauth import GoogleOAuth
from radspion.radspion import Radspion
from radspion.web.agent import agent_bp
from radspion.web.api import api_bp
from radspion.web.auth import auth_bp
from radspion.web.link import link_bp
from radspion.web.main import main_bp


def create_app(*, config: Config, radspion: Radspion, oauth) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.secret_key
    app.config["TESTING"] = config.testing
    app.config["DATABASE_PATH"] = str(config.database_path)
    # Lax allows the session cookie on the top-level redirect back from Google OAuth.
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = config.base_url.startswith("https://")
    app.extensions["radspion"] = radspion
    app.extensions["oauth"] = oauth

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(link_bp)

    @app.errorhandler(404)
    def not_found(_error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_template("errors/404.html"), 404

    return app


def launch() -> Flask:
    """WSGI entry point for gunicorn."""
    load_dotenv()

    try:
        config = load_config()
    except ConfigurationError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    try:
        storage = DatabaseRadspionStorage(config.database_path)
    except DatabaseError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    radspion = Radspion(storage)
    oauth = GoogleOAuth(
        base_url=config.base_url,
        google_client_id=config.google_client_id,
        google_client_secret=config.google_client_secret,
    )
    return create_app(config=config, radspion=radspion, oauth=oauth)


if __name__ == "__main__":  # pragma: no cover
    launch().run(host="127.0.0.1", port=8000, debug=True)  # pragma: no cover
