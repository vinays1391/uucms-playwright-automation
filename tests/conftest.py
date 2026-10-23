import sys
from collections.abc import Callable
from pathlib import Path

from playwright.sync_api import Page

repository_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repository_root))
sys.path.insert(0, str(repository_root / "src"))

import pytest

from config.settings import Settings
from uucms.auth.login_data import load_login_data
from uucms.auth.login_page import LoginPage
from uucms.auth.role_manager import RoleManager


@pytest.fixture(scope="session")
def uucms_settings() -> Settings:
	return Settings.from_environment()


@pytest.fixture(scope="session")
def login_data() -> dict:
	return load_login_data(repository_root)


@pytest.fixture(scope="session")
def role_manager(login_data: dict) -> RoleManager:
	return RoleManager(login_data)


@pytest.fixture(scope="session")
def browser_name(uucms_settings: Settings) -> str:
	return uucms_settings.browser


@pytest.fixture(scope="session")
def browser_type_launch_args(uucms_settings: Settings) -> dict[str, bool]:
	return {"headless": uucms_settings.headless}


@pytest.fixture
def login_as(
	page, uucms_settings: Settings, role_manager: RoleManager
) -> Callable[[str], Page]:
	"""Return a reusable role switcher backed by the centralized role registry."""
	current_role: str | None = None

	def _login(role: str = "default") -> Page:
		nonlocal current_role
		credentials = role_manager.credentials_for(role)
		login_page = LoginPage(page, uucms_settings.timeout_ms)
		if current_role == role and login_page.dashboard_marker.first.is_visible():
			return page
		if login_page.dashboard_marker.first.is_visible():
			login_page.logout()
		login_page.open(uucms_settings.base_url)
		login_page.login(
			credentials.username,
			credentials.password,
			uucms_settings.captcha,
		)
		login_page.expect_authenticated()
		current_role = role
		return page

	return _login


@pytest.fixture
def authenticated_page(page: Page, login_as: Callable[[str], Page]) -> Page:
	"""Authenticate as the default configured user using the shared role login."""
	return login_as("default")


@pytest.fixture
def rnd_login(login_as: Callable[[str], Page]) -> Callable[[str], Page]:
	"""Compatibility alias; new tests should use the generic login_as fixture."""
	return login_as
