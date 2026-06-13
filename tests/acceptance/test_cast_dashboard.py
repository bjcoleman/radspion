"""UC-025 / UC-026 / UC-029 / UC-031 — cast dashboard state (read-only)."""

from playwright.sync_api import Page, expect
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.dashboard import (
    STORYLINE_SLUGS,
    expect_group_titles_in_order,
    expect_mission_absent_from_dashboard,
    expect_mission_on_dashboard,
    expect_storyline_missions_absent,
    open_agent_dashboard,
)

BOB_STORYLINE_SLUGS = STORYLINE_SLUGS


def test_uc_025_diana_orientation_only(page: Page, live_app: LiveApp, login_as) -> None:
    """Diana sees basic-training only; no Testing Storyline missions."""
    open_agent_dashboard(page, live_app.base_url, login_as, "diana")

    expect(page.get_by_text("Testing Storyline")).to_have_count(0)
    expect_mission_on_dashboard(page, "basic-training", "active")
    expect_storyline_missions_absent(page)
    expect(page.locator(".dashboard__welcome")).to_be_visible()
    expect(page.get_by_text("Stay Observant")).to_be_visible()
    expect(page.get_by_label("Show completed missions")).to_have_count(0)


def test_uc_026_alice_mid_progress_dashboard(page: Page, live_app: LiveApp, login_as) -> None:
    """Alice: es-alpha completed; es-beta and es-gamma active; es-delta hidden."""
    open_agent_dashboard(page, live_app.base_url, login_as, "alice")

    expect(page.locator(".dashboard__welcome")).to_have_count(0)
    expect(page.get_by_label("Show completed missions")).to_be_visible()
    expect_group_titles_in_order(page, ["Testing Storyline", "Orientation"])
    expect_mission_on_dashboard(page, "es-alpha", "completed")
    expect_mission_on_dashboard(page, "es-beta", "active")
    expect_mission_on_dashboard(page, "es-gamma", "active")
    expect_mission_absent_from_dashboard(page, "es-delta")
    expect_mission_absent_from_dashboard(page, "es-hidden")


def test_uc_029_charlie_partial_branch_dashboard(page: Page, live_app: LiveApp, login_as) -> None:
    """Charlie: es-beta completed; es-alpha active; es-gamma not listed."""
    open_agent_dashboard(page, live_app.base_url, login_as, "charlie")

    expect_mission_on_dashboard(page, "es-beta", "completed")
    expect_mission_on_dashboard(page, "es-alpha", "active")
    expect_mission_absent_from_dashboard(page, "es-gamma")
    expect_mission_absent_from_dashboard(page, "es-delta")
    expect_mission_absent_from_dashboard(page, "es-hidden")


def test_uc_031_bob_all_storyline_missions_completed(
    page: Page,
    live_app: LiveApp,
    login_as,
) -> None:
    """Bob: every es-* mission completed on the dashboard."""
    open_agent_dashboard(page, live_app.base_url, login_as, "bob")

    expect_mission_on_dashboard(page, "basic-training", "completed")
    for slug in BOB_STORYLINE_SLUGS:
        expect_mission_on_dashboard(page, slug, "completed")
