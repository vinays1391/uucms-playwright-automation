"""Menu navigation helper for UUCMS features."""

from playwright.sync_api import Page

from uucms.core.base_page import BasePage


class MenuPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def open_menu(self, menu_path: list[str]) -> None:
        """Open a nested menu item by path names."""
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def is_menu_visible(self, menu_path: list[str]) -> bool:
        """True when the first menu item of the path is visible to this role."""
        link = self.page.get_by_role("link", name=menu_path[0], exact=True)
        return link.count() > 0 and link.first.is_visible()

    def expect_menu_absent(self, menu_path: list[str]) -> None:
        """Assert a menu item is not available to the logged-in role."""
        expect(self.page.get_by_role("link", name=menu_path[0], exact=True)).to_have_count(0)
