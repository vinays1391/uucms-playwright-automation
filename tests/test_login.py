import pytest
from playwright.sync_api import Page

from src.config.settings import Settings
from src.pages.login_page import LoginPage


@pytest.mark.login
def test_login_succeeds(page: Page, uucms_settings: Settings) -> None:
    settings = uucms_settings
    login_page = LoginPage(page, settings.timeout_ms)
    login_page.open(settings.base_url)
    login_page.login(settings.username, settings.password, settings.captcha)
    login_page.expect_authenticated()
    login_page.logout()
    login_page.expect_logged_out()
