"""Tests for POST /api/codename."""

from radspion.codename import (
    DUPLICATE_CODENAME_MESSAGE,
    INVALID_LENGTH_MESSAGE,
    SUCCESS_MESSAGE,
)
from radspion.database import DatabaseRadspionStorage
from radspion.web.api import MISSING_CODENAME_ERROR
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS


def test_codename_success_updates_user(
    testing_storyline_client,
    testing_storyline_storage: DatabaseRadspionStorage,
):
    diana = SAMPLE_AGENTS["diana"]
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana["id"]

    response = testing_storyline_client.post(
        "/api/codename",
        json={"codename": "  Night-Owl  "},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "success", "message": SUCCESS_MESSAGE}

    user = testing_storyline_storage.find_user_by_id(diana["id"])
    assert user is not None
    assert user.codename == "Night-Owl"


def test_codename_same_value_is_success(testing_storyline_client):
    diana = SAMPLE_AGENTS["diana"]
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = diana["id"]

    response = testing_storyline_client.post(
        "/api/codename",
        json={"codename": diana["codename"]},
    )
    assert response.status_code == 200
    assert response.get_json() == {"outcome": "success", "message": SUCCESS_MESSAGE}


def test_codename_duplicate_returns_message(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/codename",
        json={"codename": SAMPLE_AGENTS["alice"]["codename"]},
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "outcome": "invalid",
        "message": DUPLICATE_CODENAME_MESSAGE,
    }


def test_codename_duplicate_is_case_sensitive(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/codename", json={"codename": "alice"})
    assert response.status_code == 200
    assert response.get_json()["outcome"] == "success"


def test_codename_invalid_length_returns_message(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/codename", json={"codename": "abc"})
    assert response.status_code == 200
    assert response.get_json() == {
        "outcome": "invalid",
        "message": INVALID_LENGTH_MESSAGE,
    }


def test_codename_rejects_codename_over_max_length(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/codename", json={"codename": "a" * 21})
    assert response.status_code == 200
    assert response.get_json() == {
        "outcome": "invalid",
        "message": INVALID_LENGTH_MESSAGE,
    }


def test_codename_rejects_missing_body(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/codename", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": MISSING_CODENAME_ERROR}


def test_codename_rejects_empty_codename(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/codename", json={"codename": "   "})
    assert response.status_code == 400


def test_codename_rejects_non_json_body(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/codename",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": MISSING_CODENAME_ERROR}


def test_codename_requires_sign_in(testing_storyline_client):
    response = testing_storyline_client.post("/api/codename", json={"codename": "Night-Owl"})
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
