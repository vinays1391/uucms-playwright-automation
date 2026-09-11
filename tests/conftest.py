import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest

from src.config.settings import Settings
from src.pages.login_page import LoginPage


@pytest.fixture(scope="session")
def uucms_settings() -> Settings:
	return Settings.from_environment()


@pytest.fixture(scope="session")
def browser_name(uucms_settings: Settings) -> str:
	return uucms_settings.browser


@pytest.fixture(scope="session")
def browser_type_launch_args(uucms_settings: Settings) -> dict[str, bool]:
	return {"headless": uucms_settings.headless}


@pytest.fixture
def authenticated_page(page, uucms_settings: Settings):
	login_page = LoginPage(page, uucms_settings.timeout_ms)
	login_page.open(uucms_settings.base_url)
	login_page.login(
		uucms_settings.username,
		uucms_settings.password,
		uucms_settings.captcha,
	)
	login_page.expect_authenticated()
	return page
