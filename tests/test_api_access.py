"""Tests for POST /api/access."""

from radspion.web.api import INVALID_ACCESS_MESSAGE
from radspion.web.session_keys import SESSION_REGISTRATION_CLEARED
from tests.fakes.storage import InMemoryRadspionStorage


def _client_with_codes(codes: set[str]):
    from radspion.app import create_app
    from radspion.config import load_config
    from radspion.radspion import Radspion
    from tests.fakes.google_oauth import FakeGoogleOAuth

    config = load_config(testing=True)
    radspion = Radspion(InMemoryRadspionStorage(codes))
    return create_app(config=config, radspion=radspion, oauth=FakeGoogleOAuth()).test_client()


def test_access_success_sets_session():
    client = _client_with_codes({"SECRET-CODE"})
    response = client.post("/api/access", json={"access_code": "  SECRET-CODE "})
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "success"}
    with client.session_transaction() as session:
        assert session[SESSION_REGISTRATION_CLEARED] is True


def test_access_invalid_returns_message():
    client = _client_with_codes({"SECRET-CODE"})
    response = client.post("/api/access", json={"access_code": "WRONG"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "invalid"
    assert data["message"] == INVALID_ACCESS_MESSAGE
    with client.session_transaction() as session:
        assert SESSION_REGISTRATION_CLEARED not in session


def test_access_rejects_missing_code():
    client = _client_with_codes({"SECRET-CODE"})
    response = client.post("/api/access", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing access_code"}


def test_access_rejects_empty_code():
    client = _client_with_codes({"SECRET-CODE"})
    response = client.post("/api/access", json={"access_code": "   "})
    assert response.status_code == 400


def test_access_rejects_non_json_body():
    client = _client_with_codes({"SECRET-CODE"})
    response = client.post(
        "/api/access",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
