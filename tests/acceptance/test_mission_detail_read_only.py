"""UC-017 / UC-018 — mission detail read-only state (active vs completed)."""

from playwright.sync_api import Page, expect
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.dashboard import open_agent_dashboard


def test_uc_017_alice_active_mission_hides_completion_data(
    page: Page,
    live_app: LiveApp,
    login_as,
) -> None:
    """Active es-beta shows submit form; completion data is not in archives."""
    open_agent_dashboard(page, live_app.base_url, login_as, "alice")
    page.goto(f"{live_app.base_url}/agent/missions/es-beta")

    expect(page.locator("h1.mission-detail__title")).to_have_text("ES: Beta")
    expect(page.get_by_role("heading", name="Mission Brief", level=2)).to_be_visible()
    expect(page.get_by_role("heading", name="Recovered Data", level=2)).to_be_visible()
    expect(page.locator("form.recovered-data-form")).to_be_visible()
    expect(page.get_by_role("button", name="Submit data")).to_be_visible()
    expect(page.locator("pre.recovered-data__value")).to_have_count(0)


def test_uc_018_bob_completed_mission_shows_recovered_data(
    page: Page,
    live_app: LiveApp,
    login_as,
) -> None:
    """Completed es-alpha shows agency archives and debrief."""
    open_agent_dashboard(page, live_app.base_url, login_as, "bob")
    page.goto(f"{live_app.base_url}/agent/missions/es-alpha")

    expect(page.locator("h1.mission-detail__title")).to_have_text("ES: Alpha")
    expect(page.locator("form.recovered-data-form")).to_have_count(0)
    expect(page.locator("pre.recovered-data__value")).to_have_text("COMPLETE es-alpha")
    expect(page.get_by_role("heading", name="Mission Debrief", level=2)).to_be_visible()
