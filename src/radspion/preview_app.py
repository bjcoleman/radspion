"""Minimal Flask app for local mission brief/debrief preview."""

from flask import Flask

from radspion.web.preview import preview_bp

_PREVIEW_SECRET_KEY = "preview-secret-key-not-for-production"
_PREVIEW_PORT = 8001


def create_preview_app(*, storyline: str, mission_slug: str) -> Flask:
    """Create a preview-only Flask app (no database or OAuth)."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = _PREVIEW_SECRET_KEY
    app.config["TESTING"] = False
    app.config["PREVIEW_STORYLINE"] = storyline
    app.config["PREVIEW_MISSION_SLUG"] = mission_slug
    app.register_blueprint(preview_bp)
    return app


def preview_port() -> int:
    return _PREVIEW_PORT
