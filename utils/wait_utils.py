"""Generic wait helper functions."""

from playwright.sync_api import Page


def wait_for_selector(page: Page, selector: str, timeout_ms: int = 15000) -> None:
    page.locator(selector).wait_for(state="visible", timeout=timeout_ms)
