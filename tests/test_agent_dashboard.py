"""Tests for agent dashboard and mission detail stub."""

from radspion.content_files import load_welcome_memo_markdown
from radspion.database import DatabaseRadspionStorage
from radspion.markdown_render import render_mission_markdown
from radspion.radspion import Radspion
from radspion.web.session_keys import SESSION_USER_ID
from tests.helpers import SAMPLE_AGENTS, group_titles_in_order


def test_dashboard_lists_basic_training_after_sync(
    testing_storyline_storage: DatabaseRadspionStorage,
    testing_storyline_client,
):
    user = testing_storyline_storage.create_user(
        email="new-agent@example.com",
        google_subject_id="google-new",
        display_name="New Agent",
    )
    Radspion(testing_storyline_storage).sync_mission_status(user.id)

    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = user.id

    response = testing_storyline_client.get("/agent/dashboard")
    body = response.data.decode()

    assert response.status_code == 200
    assert "Mission Dashboard" in body
    assert "dashboard__welcome" in body
    assert "basic-training" in body
    assert "Orientation" in body


def test_dashboard_group_order_descending_group_id(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    response = testing_storyline_client.get("/agent/dashboard")
    titles = group_titles_in_order(response.data.decode())

    assert titles == ["Testing Storyline", "Orientation"]


def test_dashboard_includes_clearance_form_and_transmission_modal(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    body = testing_storyline_client.get("/agent/dashboard").data.decode()

    assert 'placeholder="Clearance code"' in body
    assert "Request Access" in body
    assert "clearance-form" in body
    assert "disabled" not in body.split("clearance-form")[1].split("</form>")[0]
    assert "data-transmission-modal" in body
    assert "clearance-form.js" in body
    assert "transmission-modal.js" in body
    assert 'name="clearance_code"' in body
    assert "clearance-redeem.js" in body


def test_dashboard_shows_welcome_memo_when_no_missions_completed(testing_storyline_client):
    source = load_welcome_memo_markdown()
    assert source is not None
    welcome_html = render_mission_markdown(source)

    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    body = testing_storyline_client.get("/agent/dashboard").data.decode()

    assert "dashboard__welcome" in body
    assert 'aria-label="Welcome memo from Radspion Command"' in body
    assert welcome_html in body
    assert "Show completed missions" not in body


def test_dashboard_hides_welcome_memo_after_first_completion(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    body = testing_storyline_client.get("/agent/dashboard").data.decode()

    assert "dashboard__welcome" not in body
    assert "Show completed missions" in body


def test_dashboard_footer_links_field_activity(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["alice"]["id"]

    body = testing_storyline_client.get("/agent/dashboard").data.decode()

    assert 'href="/activity"' in body
    assert "Field Activity" in body
    assert "<!-- ORUTNRSOAN -->" in body


def test_clearance_then_dashboard_lists_storyline_missions(testing_storyline_client):
    with testing_storyline_client.session_transaction() as sess:
        sess[SESSION_USER_ID] = SAMPLE_AGENTS["diana"]["id"]

    clearance = testing_storyline_client.post(
        "/api/clearance",
        json={"clearance_code": "EXAMPLE-CLEARANCE"},
    )
    assert clearance.status_code == 200
    assert clearance.get_json()["outcome"] == "success"

    body = testing_storyline_client.get("/agent/dashboard").data.decode()
    assert "es-alpha" in body
    assert "es-beta" in body
    assert "Testing Storyline" in body
