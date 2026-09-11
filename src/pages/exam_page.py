from collections.abc import Mapping

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class ExamPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def open_module(self, module_url: str) -> None:
        self.open(module_url)

    def fill_fields(self, fields: list[Mapping[str, str]]) -> None:
        for field in fields:
            selector = field.get("selector", "").strip()
            value = field.get("value", "")
            if not selector:
                raise ValueError("Every Exam field needs a selector")
            self.page.locator(selector).fill(value)

    def submit(self, selector: str) -> None:
        self.page.locator(selector).click()

    def expect_completed(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()
