"""Flask application entry point."""

import sys

from dotenv import load_dotenv
from flask import Flask

from radspion.config import Config, ConfigurationError, load_config
from radspion.database import DatabaseError, DatabaseRadspionStorage
from radspion.radspion import Radspion
from radspion.web.api import api_bp
from radspion.web.main import main_bp


def create_app(*, config: Config, radspion: Radspion) -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.secret_key
    app.config["TESTING"] = config.testing
    app.config["DATABASE_PATH"] = str(config.database_path)
    app.extensions["radspion"] = radspion

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
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
    return create_app(config=config, radspion=radspion)


if __name__ == "__main__":  # pragma: no cover
    launch().run(host="127.0.0.1", port=8000, debug=True)  # pragma: no cover
