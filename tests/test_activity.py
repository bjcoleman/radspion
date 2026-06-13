"""Tests for Field Activity page and aggregates."""

from datetime import UTC, datetime

from radspion.activity import format_activity_relative_time
from radspion.database import DatabaseRadspionStorage
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS


def test_activity_page_is_public(schema_only_client):
    response = schema_only_client.get("/activity")

    assert response.status_code == 200
    body = response.data.decode()
    assert 'class="page page--activity"' in body
    assert "Field Activity" in body
    assert "site-header--public" in body
    assert "← Mission Dashboard" not in body
    assert "No agents have completed missions yet." in body
    assert "No storylines configured yet." in body
    assert "No clearance grants recorded yet." in body
    assert "No missions completed yet." in body


def test_activity_page_shows_storyline_seed_data(testing_storyline_client):
    response = testing_storyline_client.get("/activity")
    body = response.data.decode()

    assert response.status_code == 200
    assert SAMPLE_AGENTS["bob"]["codename"] in body
    assert "Top Agents" in body
    assert "Storylines" in body
    assert "Recent Clearances Granted" in body
    assert "Recent Missions Completed" in body
    assert "Orientation" in body
    assert "Testing Storyline" in body


def test_activity_signed_in_uses_agent_header(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.get("/activity")
    body = response.data.decode()

    assert response.status_code == 200
    assert "site-header--public" not in body
    assert SAMPLE_AGENTS["alice"]["codename"] in body
    assert "clearance-redeem.js" in body
    assert body.count("← Mission Dashboard") == 2


def test_get_field_activity_orders_storylines_and_leaderboard(
    testing_storyline_storage: DatabaseRadspionStorage,
):
    activity = testing_storyline_storage.get_field_activity()

    assert activity.top_agents[0].codename == SAMPLE_AGENTS["bob"]["codename"]
    assert activity.top_agents[0].completed_count >= activity.top_agents[-1].completed_count
    assert activity.storylines[-1].name == "Orientation"
    assert activity.recent_completions
    assert activity.recent_clearances


def test_format_activity_relative_time():
    now = datetime(2026, 6, 8, 15, 0, tzinfo=UTC)
    iso, label = format_activity_relative_time(
        "2026-06-08 14:35:00",
        now=now,
    )
    assert iso.startswith("2026-06-08T14:35:00")
    assert label == "25m"
