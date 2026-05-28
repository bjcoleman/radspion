"""Flask application entry point."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/privacy")
    def privacy():
        return render_template("privacy.html")

    return app


def launch() -> Flask:
    """WSGI entry point for gunicorn."""
    return create_app()


if __name__ == "__main__":
    launch().run(host="127.0.0.1", port=8000, debug=True)
