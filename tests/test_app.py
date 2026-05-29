"""Tests for HTTP routes."""


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode()
    assert "Radspion" in html
    assert "New Agents" in html
    assert 'name="access_code"' in html
    assert "Validate" in html
    assert "Secure Login" in html
    assert "@moravian.edu" not in html
    assert 'href="/about"' in html
    assert 'href="/privacy"' in html
    assert "transmission-modal.js" in html
    assert "landing-access.js" in html
    assert "data-transmission-modal" in html


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
