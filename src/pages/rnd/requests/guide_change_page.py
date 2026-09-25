"""Guide change placeholder page object."""

from playwright.sync_api import Page

from src.pages.base_page import BasePage


class GuideChangePage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)
