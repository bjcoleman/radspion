"""UC-006 / UC-038 / UC-039 / UC-040 — cross-page agent journeys."""

from playwright.sync_api import Page, expect
from tests.acceptance.conftest import LiveApp
from tests.acceptance.helpers.auth import expect_landing_requires_sign_in, perform_fake_oauth
from tests.acceptance.helpers.clearance import (
    dismiss_clearance_granted_to_dashboard,
    dismiss_transmission_modal_ok,
    expect_modal_lists_mission_slugs,
    expect_transmission_outcome_heading,
    submit_clearance_confirm_form,
)
from tests.acceptance.helpers.dashboard import expect_mission_on_dashboard
from tests.acceptance.helpers.personnel import (
    dismiss_codename_modal_reload,
    expect_codename_outcome_heading,
    expect_field_status_counts,
    open_personnel_file,
    submit_codename_update,
)
from tests.helpers import SAMPLE_AGENTS


def test_dashboard_requires_sign_in(page: Page, live_app: LiveApp) -> None:
    """Unsigned agents are redirected from the dashboard to the landing page."""
    page.goto(f"{live_app.base_url}/agent/dashboard")

    expect(page).to_have_url(f"{live_app.base_url}/")
    expect_landing_requires_sign_in(page)


def test_clearance_link_signed_in_confirms_grant(page: Page, live_app: LiveApp, login_as) -> None:
    """Signed-in agent confirms clearance from /clearance/<token>."""
    login_as("diana")
    page.goto(f"{live_app.base_url}/clearance/EXAMPLE-CLEARANCE")

    expect(page.get_by_role("heading", name="Clearance request")).to_be_visible()
    submit_clearance_confirm_form(page)
    expect_transmission_outcome_heading(page, "Clearance", "Granted")
    expect_modal_lists_mission_slugs(page, ["es-alpha", "es-beta"])
    dismiss_clearance_granted_to_dashboard(page)

    expect_mission_on_dashboard(page, "es-alpha", "active")
    expect_mission_on_dashboard(page, "es-beta", "active")


def test_clearance_link_oauth_grants_after_sign_in(page: Page, live_app: LiveApp, login_as) -> None:
    """Signed-out agent follows clearance link, signs in, and sees grant modal on dashboard."""
    page.goto(f"{live_app.base_url}/clearance/EXAMPLE-CLEARANCE")
    expect(page.get_by_role("link", name="Sign in with Google")).to_be_visible()

    perform_fake_oauth(login_as, "diana")
    page.goto(f"{live_app.base_url}/agent/dashboard")

    expect_transmission_outcome_heading(page, "Clearance", "Granted")
    dismiss_transmission_modal_ok(page, expect_dashboard_reload=True)
    expect_mission_on_dashboard(page, "es-alpha", "active")


def test_uc_038_personnel_file_field_status(page: Page, live_app: LiveApp, login_as) -> None:
    """Personnel File shows field status counts matching Alice's dashboard state."""
    open_personnel_file(page, live_app.base_url, login_as, "alice")

    expect(page.get_by_role("heading", name="Field Status", level=2)).to_be_visible()
    expect_field_status_counts(page, completed=2, active=2)
    expect(page.locator(".service-record__detail", has_text="ES: Alpha").first).to_be_visible()


def test_uc_039_diana_updates_codename(page: Page, live_app: LiveApp, login_as) -> None:
    """Agent updates codename from the Personnel File."""
    open_personnel_file(page, live_app.base_url, login_as, "diana")

    submit_codename_update(page, "Night-Owl")
    expect_codename_outcome_heading(page, "Codename", "Updated")
    dismiss_codename_modal_reload(page)

    expect(page.locator("#personnel-codename")).to_have_value("Night-Owl")
    expect(page.locator(".site-header__agent-link")).to_have_text("Night-Owl")


def test_uc_040_field_activity_is_public(page: Page, live_app: LiveApp) -> None:
    """Field Activity is public and shows codenames, not email addresses."""
    page.goto(f"{live_app.base_url}/activity")

    expect(page.get_by_role("heading", name="Field Activity", level=1)).to_be_visible()
    expect(page.locator(".site-header--public")).to_be_visible()
    expect(
        page.locator(".activity-leaderboard__agent", has_text=SAMPLE_AGENTS["bob"]["codename"])
    ).to_be_visible()
    expect(page.get_by_text(SAMPLE_AGENTS["diana"]["email"])).to_have_count(0)
