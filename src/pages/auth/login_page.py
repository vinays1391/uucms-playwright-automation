"""Authentication page object for login flow."""

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    """Placeholder login page object, to be refined after recording."""

    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)
        self.entry_button = page.get_by_role("button", name="ಲಾಗిన్")
        self.username_input = page.locator("#txtUserName")
        self.password_input = page.locator("#txtPassword")
        self.login_button = page.get_by_role("button", name="Log In")
        self.dashboard_marker = page.locator("#MenuDiv, #userDropdown")

    def open(self, url: str) -> None:
        super().open(url)
        self.entry_button.wait_for(state="visible")

    def login(self, username: str, password: str, captcha: str | None = None) -> None:
        if self.dashboard_marker.first.is_visible():
            return
        if self.entry_button.is_visible():
            self.entry_button.click()
        self.username_input.fill(username)
        self.password_input.fill(password)
        if captcha:
            captcha_input = self.page.locator("#Input_captcha, #txtCaptcha, input[name='captcha']").first
            if captcha_input.count() > 0:
                captcha_input.fill(captcha)
        self.login_button.click()

    def expect_authenticated(self) -> None:
        expect(self.dashboard_marker.first).to_be_visible()
