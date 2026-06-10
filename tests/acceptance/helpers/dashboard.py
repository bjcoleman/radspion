"""Dashboard assertions for acceptance tests."""

from __future__ import annotations

from playwright.sync_api import Page, expect

STORYLINE_SLUGS = ("es-alpha", "es-beta", "es-gamma", "es-delta", "es-hidden")


def open_agent_dashboard(page: Page, base_url: str, login_as, agent_key: str) -> None:
    """Sign in and open the mission dashboard."""
    login_as(agent_key)
    page.goto(f"{base_url}/agent/dashboard")
    expect(page.get_by_role("heading", name="Mission Dashboard")).to_be_visible()


def mission_list_item(page: Page, slug: str):
    return page.locator(f'li.mission-list__item:has(.mission-card__slug:text-is("{slug}"))')


def mission_group_for_slug(page: Page, slug: str):
    return page.locator(f'details[data-mission-group]:has(.mission-card__slug:text-is("{slug}"))')


def expand_mission_group(page: Page, slug: str) -> None:
    """Open the story-arc section so missions inside collapsed groups are visible."""
    group = mission_group_for_slug(page, slug)
    if not group.evaluate("element => element.open"):
        group.locator("summary").click()


def expect_mission_on_dashboard(page: Page, slug: str, status: str) -> None:
    expand_mission_group(page, slug)
    item = mission_list_item(page, slug)
    expect(item).to_be_visible()
    expect(item).to_have_attribute("data-mission-status", status)


def expect_mission_absent_from_dashboard(page: Page, slug: str) -> None:
    expect(mission_list_item(page, slug)).to_have_count(0)


def expect_group_titles_in_order(page: Page, titles: list[str]) -> None:
    loc = page.locator(".mission-group__title")
    expect(loc).to_have_count(len(titles))
    for index, title in enumerate(titles):
        expect(loc.nth(index)).to_have_text(title)


def expect_storyline_missions_absent(page: Page) -> None:
    for slug in STORYLINE_SLUGS:
        expect_mission_absent_from_dashboard(page, slug)


def set_show_completed_missions(page: Page, *, shown: bool) -> None:
    toggle = page.locator("[data-show-completed]")
    if shown:
        toggle.check()
    else:
        toggle.uncheck()


def expect_mission_hidden_on_dashboard(page: Page, slug: str) -> None:
    expect(mission_list_item(page, slug)).to_be_hidden()
