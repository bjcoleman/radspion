"""Tests for HTTP routes."""


def test_favicon(client):
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.mimetype == "image/vnd.microsoft.icon"
    assert response.data[:4] == b"\x00\x00\x01\x00"


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode()
    assert 'rel="icon"' in html
    assert "/static/favicon.ico" in html
    assert "Radspion" in html
    assert "Agent Login" in html
    assert "Secure Login" in html
    assert "@moravian.edu" not in html
    assert 'href="/about"' in html
    assert 'href="/privacy"' in html
    assert "transmission-modal.js" in html
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


def test_unknown_route_returns_themed_404(client):
    response = client.get("/no-such-channel")
    assert response.status_code == 404
    html = response.data.decode()
    assert "Transmission Terminated" in html
    assert "ERR-NO-SIGNAL" in html
    assert "Return to secure channel" in html
    assert 'href="/"' in html


def test_api_unknown_route_returns_json_404(client):
    response = client.get("/api/no-such-endpoint")
    assert response.status_code == 404
    assert response.is_json
    assert response.get_json() == {"error": "Not found"}
