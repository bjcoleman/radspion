"""Tests for Agent Personnel File."""

import sqlite3

from radspion.database import DatabaseRadspionStorage
from radspion.personnel import format_personnel_date
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS


def test_personnel_requires_login(testing_storyline_client):
    response = testing_storyline_client.get("/agent/personnel")

    assert response.status_code == 302
    assert response.location.endswith("/")


def test_personnel_page_shows_agent_record(testing_storyline_client):
    alice = SAMPLE_AGENTS["alice"]
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = alice["id"]

    response = testing_storyline_client.get("/agent/personnel")
    body = response.data.decode()

    assert response.status_code == 200
    assert 'class="page page--personnel"' in body
    assert "clearance-redeem.js" in body
    assert "Agent Personnel File" in body
    assert alice["display_name"] in body
    assert alice["email"] in body
    assert alice["codename"] in body
    assert 'href="/agent/personnel"' in body
    assert "site-header__agent-link--current" in body
    assert "Missions completed" in body
    assert "Active missions" in body
    assert body.count('<dd class="personnel-stats__value">2</dd>') == 2
    assert "Welcome to Radspion" in body
    assert "ES: Alpha" in body
    assert "Enlisted" in body
    assert "Personnel file opened" in body
    assert "Mission Completed" in body
    assert "Clearance Granted" in body
    assert "confidential_your_eyes_only.png" in body
    assert "personnel-codename.js" in body
    assert "data-personnel-codename-form" in body
    assert 'name="codename"' in body
    assert "readonly" not in body
    assert ">Update</button>" in body


def test_get_personnel_file_counts_and_service_record(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    alice_id = SAMPLE_AGENTS["alice"]["id"]

    personnel = testing_storyline_storage.get_personnel_file(alice_id)

    assert personnel is not None
    assert personnel.display_name == SAMPLE_AGENTS["alice"]["display_name"]
    assert personnel.email == SAMPLE_AGENTS["alice"]["email"]
    assert personnel.codename == SAMPLE_AGENTS["alice"]["codename"]
    assert personnel.missions_completed == 2
    assert personnel.active_missions == 2
    assert personnel.service_record[0].verb in {
        "Mission Completed",
        "Clearance Granted",
        "Enlisted",
    }
    verbs = {entry.verb for entry in personnel.service_record}
    assert "Enlisted" in verbs
    assert "Mission Completed" in verbs
    assert "Clearance Granted" in verbs


def test_service_record_enlisted_is_last_when_timestamps_tie(
    testing_storyline_db_path,
    testing_storyline_storage: DatabaseRadspionStorage,
):
    """Enlisted must be the oldest row even when listed_at matches created_at."""
    tied = "2026-06-08 10:00:00"
    with sqlite3.connect(testing_storyline_db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            "INSERT INTO users (id, email, google_subject_id, display_name, codename, created_at) "
            "VALUES (99, 'new@moravian.edu', 'google-new', 'New Agent', 'AGENT0099', ?)",
            (tied,),
        )
        conn.execute(
            """
            INSERT INTO agent_mission_status (
                user_id, mission_id, status, listed_at, listed_via, completed_at
            ) VALUES (99, 1, 'completed', ?, 'open', '2026-06-08 11:00:00')
            """,
            (tied,),
        )
        conn.commit()

    personnel = testing_storyline_storage.get_personnel_file(99)

    assert personnel is not None
    assert [entry.verb for entry in personnel.service_record] == [
        "Mission Completed",
        "Clearance Granted",
        "Enlisted",
    ]


def test_format_personnel_date():
    iso, label = format_personnel_date("2026-04-12 08:00:00")
    assert iso == "2026-04-12"
    assert label == "Apr 12, 2026"
