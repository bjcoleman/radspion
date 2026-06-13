"""Tests for POST /api/missions/<slug>/submit."""

from radspion.web.api import INVALID_SUBMIT_MESSAGE
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS


def test_submit_success(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "COMPLETE es-beta"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert data["new_missions"] == []


def test_submit_success_with_new_missions(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["charlie"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    assert len(data["new_missions"]) == 1
    assert data["new_missions"][0]["slug"] == "es-gamma"


def test_submit_invalid_returns_message(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "WRONG"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "invalid", "message": INVALID_SUBMIT_MESSAGE}


def test_submit_already_done(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["bob"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data


def test_submit_not_listed_returns_404(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-alpha/submit",
        json={"completion_data": "COMPLETE es-alpha"},
    )
    assert response.status_code == 404


def test_submit_rejects_missing_code(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post("/api/missions/es-beta/submit", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing completion_data"}


def test_submit_rejects_empty_code(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "   "},
    )
    assert response.status_code == 400


def test_submit_rejects_non_json_body(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post(
        "/api/missions/es-beta/submit",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing completion_data"}


def test_submit_requires_sign_in(testing_storyline_client):
    response = testing_storyline_client.post(
        "/api/missions/es-beta/submit",
        json={"completion_data": "COMPLETE es-beta"},
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
