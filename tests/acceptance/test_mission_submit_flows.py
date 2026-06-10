"""UC-021 / UC-022 / UC-028 / UC-032 — mission data submission via transmission modal."""

from playwright.sync_api import Page, expect
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.clearance import (
    dismiss_transmission_modal_ok,
    expect_modal_lists_mission_slugs,
    expect_modal_message_contains,
    expect_transmission_outcome_heading,
)
from tests.acceptance.helpers.dashboard import (
    expect_mission_absent_from_dashboard,
    expect_mission_on_dashboard,
    expect_storyline_missions_absent,
)
from tests.acceptance.helpers.mission_detail import (
    INVALID_SUBMIT_MESSAGE,
    dismiss_data_accepted_reload_mission,
    expect_mission_page_status,
    open_mission,
    submit_mission_data,
)


def test_uc_028_alice_completes_es_beta(page: Page, live_app: LiveApp, login_as) -> None:
    """Alice submits correct data for es-beta; mission completes; es-delta stays hidden."""
    open_mission(page, live_app.base_url, login_as, "alice", "es-beta")

    submit_mission_data(page, "COMPLETE es-beta")
    expect_transmission_outcome_heading(page, "Data", "Accepted")
    dismiss_data_accepted_reload_mission(page)

    page.goto(f"{live_app.base_url}/agent/dashboard")
    expect_mission_on_dashboard(page, "es-beta", "completed")
    expect_mission_absent_from_dashboard(page, "es-delta")


def test_uc_022_alice_wrong_mission_data(page: Page, live_app: LiveApp, login_as) -> None:
    """Wrong data on es-beta shows verification failed; mission stays active."""
    open_mission(page, live_app.base_url, login_as, "alice", "es-beta")

    submit_mission_data(page, "WRONG-DATA")
    expect_transmission_outcome_heading(page, "Verification", "Failed")
    expect_modal_message_contains(page, INVALID_SUBMIT_MESSAGE)
    dismiss_transmission_modal_ok(page)

    expect_mission_page_status(page, "active")
    expect(page.locator("form.recovered-data-form")).to_be_visible()


def test_uc_032_es_delta_lists_after_both_branches(page: Page, live_app: LiveApp, login_as) -> None:
    """Completing es-beta then es-gamma lists es-delta."""
    open_mission(page, live_app.base_url, login_as, "alice", "es-beta")

    submit_mission_data(page, "COMPLETE es-beta")
    expect_transmission_outcome_heading(page, "Data", "Accepted")
    dismiss_data_accepted_reload_mission(page)

    page.goto(f"{live_app.base_url}/agent/dashboard")
    expect_mission_absent_from_dashboard(page, "es-delta")

    open_mission(page, live_app.base_url, login_as, "alice", "es-gamma")
    submit_mission_data(page, "COMPLETE es-gamma")
    expect_transmission_outcome_heading(page, "Data", "Accepted")
    expect_modal_lists_mission_slugs(page, ["es-delta"])
    dismiss_data_accepted_reload_mission(page)

    page.goto(f"{live_app.base_url}/agent/dashboard")
    expect_mission_on_dashboard(page, "es-delta", "active")


def test_diana_completes_basic_training(page: Page, live_app: LiveApp, login_as) -> None:
    """Diana completes orientation basic-training; no storyline missions appear."""
    open_mission(page, live_app.base_url, login_as, "diana", "basic-training")

    submit_mission_data(page, "WELCOME-AGENT-OK")
    expect_transmission_outcome_heading(page, "Data", "Accepted")
    dismiss_data_accepted_reload_mission(page)

    page.goto(f"{live_app.base_url}/agent/dashboard")
    expect_mission_on_dashboard(page, "basic-training", "completed")
    expect_storyline_missions_absent(page)
