"""Tests for the Flask application."""

import pytest

from radspion.app import create_app, launch


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Radspion" in html
    assert "Sign in with Google" in html
    assert "@moravian.edu" in html
    assert 'href="/about"' in html
    assert 'href="/privacy"' in html


def test_about(client):
    response = client.get("/about")
    assert response.status_code == 200
    html = response.data.decode()
    assert "What is Radspion?" in html
    assert "Moravian University" in html
    assert 'href="/"' in html


def test_privacy(client):
    response = client.get("/privacy")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Privacy Policy" in html
    assert "Google" in html
    assert 'href="/privacy"' in html


def test_launch_returns_flask_app():
    app = launch()
    assert app.name == "radspion.app"
