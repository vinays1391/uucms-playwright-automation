from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)
        self.entry_button = page.get_by_role("button", name="ಲಾಗಿನ್")
        self.university_tab = page.locator("#pills-university-tab")
        self.university_role_tab = page.get_by_role("tab", name="University", exact=True)
        self.username_input = page.locator("#txtUserName")
        self.password_input = page.locator("#txtPassword")
        self.login_button = page.get_by_role("button", name="Log In")
        self.dashboard_marker = page.locator("#MenuDiv, #userDropdown")
        self.user_menu = page.locator("#userDropdown")
        self.logout_link = page.get_by_role("link", name="Logout")
        self.captcha_inputs = page.locator(
            "#Input_captcha, #txtCaptcha, input[name='captcha'], "
            "input[id*='captcha' i], input[name*='captcha' i]"
        )

    def open(self, url: str) -> None:
        super().open(url)
        self.entry_button.wait_for(state="visible")

    def login(self, username: str, password: str, captcha: str | None = None) -> None:
        if self.dashboard_marker.first.is_visible():
            return

        if self.entry_button.is_visible():
            self.entry_button.click()
            self.page.wait_for_url("**/Login/Index*")

        if self.university_role_tab.is_visible():
            self.university_role_tab.click()
        elif self.university_tab.is_visible():
            self.university_tab.click()

        self.username_input.click()
        self.username_input.press("Control+A")
        self.username_input.type(username)
        self.password_input.click()
        self.password_input.press("Control+A")
        self.password_input.type(password)

        if captcha and self.captcha_inputs.count() > 0:
            self.captcha_inputs.first.click()
            self.captcha_inputs.first.press("Control+A")
            self.captcha_inputs.first.type(captcha)

        self.login_button.click()

    def expect_authenticated(self) -> None:
        expect(self.dashboard_marker.first).to_be_visible()

    def logout(self) -> None:
        self.user_menu.click()
        self.logout_link.click()

    def expect_logged_out(self) -> None:
        expect(self.username_input).to_be_visible()
