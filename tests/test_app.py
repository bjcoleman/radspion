"""Tests for the Flask application."""

import pytest

from radspion.app import create_app, launch


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_hello_world(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.data == b"Hello, World!"


def test_launch_returns_flask_app():
    app = launch()
    assert app.name == "radspion.app"
