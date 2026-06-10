"""Additional acceptance scenarios — provisioning, 404, dashboard toggle."""

from playwright.sync_api import Page, expect
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.auth import sign_in_oauth_user
from tests.acceptance.helpers.dashboard import (
    expect_mission_hidden_on_dashboard,
    expect_mission_on_dashboard,
    expect_storyline_missions_absent,
    open_agent_dashboard,
    set_show_completed_missions,
)


def test_new_agent_first_sign_in_provisions_and_syncs(page: Page, live_app: LiveApp) -> None:
    """First OAuth sign-in creates the agent with default codename and lists basic-training."""
    sign_in_oauth_user(
        page,
        live_app,
        google_subject_id="google-brand-new",
        email="brand-new@example.com",
        display_name="Brand New Agent",
    )
    page.goto(f"{live_app.base_url}/agent/dashboard")

    expect(page.get_by_role("heading", name="Mission Dashboard")).to_be_visible()
    expect(page.locator(".site-header__agent-link")).to_have_text("AGENT0001")
    expect_mission_on_dashboard(page, "basic-training", "active")
    expect_storyline_missions_absent(page)


def test_unlisted_mission_returns_404(page: Page, live_app: LiveApp, login_as) -> None:
    """Charlie cannot open es-gamma directly when it is not listed on the dashboard."""
    login_as("charlie")
    page.goto(f"{live_app.base_url}/agent/missions/es-gamma")

    expect(page.get_by_role("heading", name="Transmission Terminated", level=1)).to_be_visible()
    expect(page.get_by_text("ERR-NO-SIGNAL")).to_be_visible()


def test_dashboard_toggle_hides_completed_missions(page: Page, live_app: LiveApp, login_as) -> None:
    """Show completed missions toggle hides and restores Bob's completed missions."""
    open_agent_dashboard(page, live_app.base_url, login_as, "bob")

    set_show_completed_missions(page, shown=False)
    expect_mission_hidden_on_dashboard(page, "es-alpha")
    expect_mission_hidden_on_dashboard(page, "basic-training")

    set_show_completed_missions(page, shown=True)
    expect_mission_on_dashboard(page, "es-alpha", "completed")
    expect_mission_on_dashboard(page, "basic-training", "completed")
