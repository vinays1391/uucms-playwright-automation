"""Admission page object placeholder for the Ph.D flow."""

from playwright.sync_api import Page

from src.pages.base_page import BasePage


class PhDAdmissionPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)
        self.page_title = page.locator("body")
