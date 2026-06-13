"""Tests for POST /api/clearance."""

import sqlite3

from radspion.web.api import INVALID_CLEARANCE_MESSAGE
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS


def test_clearance_success_returns_new_missions(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "EXAMPLE-CLEARANCE"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "success"
    slugs = {mission["slug"] for mission in data["new_missions"]}
    assert slugs == {"es-alpha", "es-beta"}
    assert data["new_missions"][0]["group_name"] == "Testing Storyline"


def test_clearance_sets_listed_via_and_shared_listed_at(
    testing_storyline_client,
    testing_storyline_db_path,
):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    testing_storyline_client.post("/api/clearance", json={"clearance_code": "EXAMPLE-CLEARANCE"})

    with sqlite3.connect(testing_storyline_db_path) as conn:
        rows = conn.execute(
            """
            SELECT ams.listed_via, ams.listed_at
            FROM agent_mission_status ams
            JOIN missions m ON m.id = ams.mission_id
            JOIN users u ON u.id = ams.user_id
            WHERE u.id = ? AND m.slug IN ('es-alpha', 'es-beta')
            ORDER BY m.slug ASC
            """,
            (SAMPLE_AGENTS["diana"]["id"],),
        ).fetchall()

    assert len(rows) == 2
    assert rows[0][0] == "clearance"
    assert rows[1][0] == "clearance"
    assert rows[0][1] == rows[1][1]


def test_clearance_invalid_returns_message(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "ZZ-INVALID"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"outcome": "invalid", "message": INVALID_CLEARANCE_MESSAGE}


def test_clearance_already_done(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "EXAMPLE-CLEARANCE"},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["outcome"] == "already_done"
    assert data["new_missions"] == []
    assert "message" in data


def test_clearance_rejects_missing_code(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post("/api/clearance", json={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing clearance_code"}


def test_clearance_rejects_empty_code(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "   "},
    )
    assert response.status_code == 400


def test_clearance_rejects_non_json_body(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    response = testing_storyline_client.post(
        "/api/clearance",
        data="not json",
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing clearance_code"}


def test_clearance_requires_sign_in(testing_storyline_client):
    response = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "EXAMPLE-CLEARANCE"},
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Unauthorized"}
