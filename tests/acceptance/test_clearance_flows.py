"""UC-019 / UC-019b / UC-020 / UC-027 — clearance via header form + transmission modal."""

from playwright.sync_api import Page
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.clearance import (
    ALREADY_GRANTED_MESSAGE,
    INVALID_CLEARANCE_MESSAGE,
    dismiss_transmission_modal_ok,
    expect_modal_lists_mission_slugs,
    expect_modal_message_contains,
    expect_transmission_outcome_heading,
    submit_header_clearance,
)
from tests.acceptance.helpers.dashboard import (
    expect_mission_absent_from_dashboard,
    expect_mission_on_dashboard,
    expect_storyline_missions_absent,
    open_agent_dashboard,
)


def test_uc_019_diana_grants_example_clearance(page: Page, live_app: LiveApp, login_as) -> None:
    """Valid EXAMPLE-CLEARANCE lists es-alpha and es-beta on the dashboard."""
    open_agent_dashboard(page, live_app.base_url, login_as, "diana")

    submit_header_clearance(page, "EXAMPLE-CLEARANCE")
    expect_transmission_outcome_heading(page, "Clearance", "Granted")
    expect_modal_lists_mission_slugs(page, ["es-alpha", "es-beta"])
    dismiss_transmission_modal_ok(page, expect_dashboard_reload=True)

    expect_mission_on_dashboard(page, "es-alpha", "active")
    expect_mission_on_dashboard(page, "es-beta", "active")
    expect_mission_absent_from_dashboard(page, "es-gamma")


def test_uc_027_diana_grants_hidden_clearance(page: Page, live_app: LiveApp, login_as) -> None:
    """HIDDEN-CLEARANCE lists only es-hidden."""
    open_agent_dashboard(page, live_app.base_url, login_as, "diana")

    submit_header_clearance(page, "HIDDEN-CLEARANCE")
    expect_transmission_outcome_heading(page, "Clearance", "Granted")
    expect_modal_lists_mission_slugs(page, ["es-hidden"])
    dismiss_transmission_modal_ok(page, expect_dashboard_reload=True)

    expect_mission_on_dashboard(page, "es-hidden", "active")
    expect_mission_absent_from_dashboard(page, "es-alpha")
    expect_mission_absent_from_dashboard(page, "es-beta")


def test_uc_019b_alice_example_clearance_already_done(
    page: Page,
    live_app: LiveApp,
    login_as,
) -> None:
    """Re-submitting EXAMPLE-CLEARANCE when already granted shows already_done."""
    open_agent_dashboard(page, live_app.base_url, login_as, "alice")

    submit_header_clearance(page, "EXAMPLE-CLEARANCE")
    expect_transmission_outcome_heading(page, "Previously", "Granted")
    expect_modal_message_contains(page, ALREADY_GRANTED_MESSAGE)
    dismiss_transmission_modal_ok(page)

    expect_mission_on_dashboard(page, "es-alpha", "completed")
    expect_mission_on_dashboard(page, "es-beta", "active")
    expect_mission_on_dashboard(page, "es-gamma", "active")


def test_uc_019b_bob_hidden_clearance_already_done(page: Page, live_app: LiveApp, login_as) -> None:
    """Re-submitting HIDDEN-CLEARANCE when es-hidden is already completed."""
    open_agent_dashboard(page, live_app.base_url, login_as, "bob")

    submit_header_clearance(page, "HIDDEN-CLEARANCE")
    expect_transmission_outcome_heading(page, "Previously", "Granted")
    expect_modal_message_contains(page, ALREADY_GRANTED_MESSAGE)
    dismiss_transmission_modal_ok(page)

    expect_mission_on_dashboard(page, "es-hidden", "completed")


def test_uc_020_diana_invalid_clearance_code(page: Page, live_app: LiveApp, login_as) -> None:
    """Unknown clearance code shows verification failed; dashboard unchanged."""
    open_agent_dashboard(page, live_app.base_url, login_as, "diana")

    submit_header_clearance(page, "NOT-A-REAL-CODE")
    expect_transmission_outcome_heading(page, "Verification", "Failed")
    expect_modal_message_contains(page, INVALID_CLEARANCE_MESSAGE)
    dismiss_transmission_modal_ok(page)

    expect_storyline_missions_absent(page)
