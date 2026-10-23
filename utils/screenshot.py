"""Screenshot helper for failed test captures."""

from pathlib import Path

from playwright.sync_api import Page


def save_screenshot(page: Page, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(target), full_page=True)
