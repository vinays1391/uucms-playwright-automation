"""Menu navigation helper for UUCMS features."""

from playwright.sync_api import Page

from src.pages.base_page import BasePage


class MenuPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def open_menu(self, menu_path: list[str]) -> None:
        """Open a nested menu item by path names."""
        for item in menu_path:
            self.page.get_by_role("link", name=item, exact=True).click()
