from dataclasses import dataclass
import json
import os
from pathlib import Path

from dotenv import load_dotenv

from uucms.auth.login_data import load_login_data
from uucms.auth.role_manager import RoleManager


class ConfigurationError(ValueError):
    """Raised when required runtime configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    base_url: str
    username: str
    password: str
    captcha: str | None
    browser: str
    headless: bool
    timeout_ms: int

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        repository_root = Path(__file__).resolve().parents[1]
        try:
            login_data = load_login_data(repository_root)
        except ValueError as exc:
            raise ConfigurationError(str(exc)) from exc

        try:
            default_credentials = RoleManager(login_data).credentials_for()
        except ValueError as exc:
            raise ConfigurationError(str(exc)) from exc

        base_url = os.getenv("UUCMS_BASE_URL", "").strip()
        if not base_url:
            raise ConfigurationError("Missing required environment variable: UUCMS_BASE_URL")

        browser = os.getenv("UUCMS_BROWSER", "chromium").strip().lower()
        if browser not in {"chromium", "firefox", "webkit"}:
            raise ConfigurationError("UUCMS_BROWSER must be chromium, firefox, or webkit")

        try:
            timeout_ms = int(os.getenv("UUCMS_TIMEOUT_MS", "15000"))
        except ValueError as exc:
            raise ConfigurationError("UUCMS_TIMEOUT_MS must be an integer") from exc
        if timeout_ms <= 0:
            raise ConfigurationError("UUCMS_TIMEOUT_MS must be greater than zero")

        return cls(
            base_url=base_url,
            username=default_credentials.username,
            password=default_credentials.password,
            captcha=str(login_data.get("captcha", "12345")).strip() or None,
            browser=browser,
            headless=os.getenv("UUCMS_HEADLESS", "false").strip().lower() in {"1", "true", "yes"},
            timeout_ms=timeout_ms,
        )


def load_test_data(file_name: str) -> dict:
    repository_root = Path(__file__).resolve().parents[1]
    data_path = repository_root / "test_data" / file_name
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Missing test data file: {data_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in test data file: {data_path}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Test data must contain a JSON object: {data_path}")
    return data
