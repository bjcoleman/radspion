"""Clearance header form and transmission modal helpers."""

from __future__ import annotations

from playwright.sync_api import Page, expect

INVALID_CLEARANCE_MESSAGE = "Command could not verify this clearance code against agency records."
ALREADY_GRANTED_MESSAGE = "You have already been granted this clearance."


def submit_header_clearance(page: Page, clearance_code: str) -> None:
    """Enter a clearance code in the sticky header and submit."""
    page.get_by_placeholder("Clearance code").fill(clearance_code)
    page.get_by_role("button", name="Request Access").click()


def expect_transmission_outcome_heading(page: Page, line1: str, line2: str) -> None:
    modal = page.locator("[data-transmission-modal]")
    expect(modal).to_be_visible()
    outcome = modal.locator("[data-transmission-outcome]")
    expect(outcome).to_be_visible()
    lines = outcome.locator(".transmission-modal__outcome-heading-line")
    expect(lines.nth(0)).to_have_text(line1)
    expect(lines.nth(1)).to_have_text(line2)


def expect_modal_lists_mission_slugs(page: Page, slugs: list[str]) -> None:
    for slug in slugs:
        expect(page.locator(f".outcome-missions__slug:text-is('({slug})')")).to_be_visible()


def expect_modal_message_contains(page: Page, text: str) -> None:
    expect(page.locator(".transmission-modal__message")).to_contain_text(text)


def submit_clearance_confirm_form(page: Page) -> None:
    """Submit the signed-in clearance landing confirm form."""
    page.locator(".clearance-confirm-form").get_by_role("button", name="Request Access").click()


def dismiss_transmission_modal_ok(page: Page, *, expect_dashboard_reload: bool = False) -> None:
    """Dismiss the outcome modal. Success on the dashboard reloads the page."""
    page.locator(".transmission-modal__ok").click()
    if expect_dashboard_reload:
        expect(page.get_by_role("heading", name="Mission Dashboard")).to_be_visible()
    else:
        expect(page.locator("[data-transmission-modal]")).to_be_hidden()


def dismiss_clearance_granted_to_dashboard(page: Page) -> None:
    """Dismiss clearance success on the clearance landing page (navigates to dashboard)."""
    page.locator(".transmission-modal__ok").click()
    expect(page.get_by_role("heading", name="Mission Dashboard")).to_be_visible()
