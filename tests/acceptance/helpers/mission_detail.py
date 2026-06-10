"""Mission detail page helpers for acceptance tests."""

from __future__ import annotations

from playwright.sync_api import Page, expect

INVALID_SUBMIT_MESSAGE = (
    "We received your transmission, but the recovered data does not match mission parameters."
)


def open_mission(page: Page, base_url: str, login_as, agent_key: str, slug: str) -> None:
    """Sign in and open a mission detail page."""
    login_as(agent_key)
    page.goto(f"{base_url}/agent/missions/{slug}")
    expect(page.locator("h1.mission-detail__title")).to_be_visible()


def submit_mission_data(page: Page, completion_data: str) -> None:
    """Submit recovered data from the active mission form."""
    page.locator("#recovered-data-input").fill(completion_data)
    page.get_by_role("button", name="Submit data").click()


def expect_mission_page_status(page: Page, status: str) -> None:
    expect(page.locator(f".mission-detail__meta .status-badge--{status}")).to_be_visible()


def dismiss_data_accepted_reload_mission(page: Page) -> None:
    """Dismiss a successful data transmission; mission detail reloads as completed."""
    page.locator(".transmission-modal__ok").click()
    expect_mission_page_status(page, "completed")
