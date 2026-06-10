"""Agent Personnel File helpers."""

from __future__ import annotations

from playwright.sync_api import Page, expect


def open_personnel_file(page: Page, base_url: str, login_as, agent_key: str) -> None:
    login_as(agent_key)
    page.goto(f"{base_url}/agent/personnel")
    expect(page.get_by_role("heading", name="Agent Personnel File", level=1)).to_be_visible()


def expect_field_status_counts(page: Page, *, completed: int, active: int) -> None:
    completed_value = (
        page.locator(".personnel-stats__item")
        .filter(has_text="Missions completed")
        .locator(".personnel-stats__value")
    )
    active_value = (
        page.locator(".personnel-stats__item")
        .filter(has_text="Active missions")
        .locator(".personnel-stats__value")
    )
    expect(completed_value).to_have_text(str(completed))
    expect(active_value).to_have_text(str(active))


def submit_codename_update(page: Page, codename: str) -> None:
    page.locator("#personnel-codename").fill(codename)
    page.get_by_role("button", name="Update").click()


def expect_codename_outcome_heading(page: Page, line1: str, line2: str) -> None:
    modal = page.locator("[data-codename-modal]")
    expect(modal).to_be_visible()
    lines = modal.locator(".transmission-modal__outcome-heading-line")
    expect(lines.nth(0)).to_have_text(line1)
    expect(lines.nth(1)).to_have_text(line2)


def dismiss_codename_modal_reload(page: Page) -> None:
    page.locator("[data-codename-modal] .transmission-modal__ok").click()
    expect(page.get_by_role("heading", name="Agent Personnel File", level=1)).to_be_visible()
