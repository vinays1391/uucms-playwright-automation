import pytest
from playwright.sync_api import Page

from config.settings import Settings
from uucms.auth.login_page import LoginPage
from uucms.auth.role_manager import RoleManager


def _role_credentials(role: str, role_manager: RoleManager) -> tuple[str, str]:
    try:
        credentials = role_manager.credentials_for(role)
    except ValueError as exc:
        pytest.fail(
            f"Configure the {role!r} role in "
            "test_data/login/LoginData.json and set its password environment "
            f"variable before running this test: {exc}"
        )
    if "REPLACE_WITH" in credentials.username:
        pytest.fail(
            f"Replace the placeholder username for {role!r} in "
            "test_data/login/LoginData.json before running this test."
        )
    return credentials.username, credentials.password


@pytest.mark.login
def test_login_succeeds(page: Page, uucms_settings: Settings) -> None:
    settings = uucms_settings
    login_page = LoginPage(page, settings.timeout_ms)
    login_page.open(settings.base_url)
    login_page.login(settings.username, settings.password, settings.captcha)
    login_page.expect_authenticated()
    login_page.logout()
    login_page.expect_logged_out()


@pytest.mark.login
@pytest.mark.parametrize(
    "role",
    ["candidate", "department_chairperson", "registrar_admin"],
)
def test_role_login(
    page: Page,
    uucms_settings: Settings,
    role_manager: RoleManager,
    role: str,
) -> None:
    settings = uucms_settings
    username, password = _role_credentials(role, role_manager)
    login_page = LoginPage(page, settings.timeout_ms)
    login_page.open(settings.base_url)
    login_page.login(username, password, settings.captcha)
    login_page.expect_authenticated()
    login_page.logout()
    login_page.expect_logged_out()
