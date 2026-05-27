"""Flask application entry point."""

from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.get("/")
    def hello_world() -> str:
        return "Hello, World!"

    return app


def launch() -> Flask:
    """WSGI entry point for gunicorn."""
    return create_app()


if __name__ == "__main__":
    launch().run(host="127.0.0.1", port=8000, debug=True)
