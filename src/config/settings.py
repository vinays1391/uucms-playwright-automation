from dataclasses import dataclass
import json
import os
from pathlib import Path

from dotenv import load_dotenv


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
        login_data_path = Path(__file__).parents[2] / "test_data" / "loginData.json"
        try:
            login_data = json.loads(login_data_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ConfigurationError(
                f"Missing test data file: {login_data_path}"
            ) from exc
        except json.JSONDecodeError as exc:
            raise ConfigurationError(
                f"Invalid JSON in test data file: {login_data_path}"
            ) from exc

        required = {
            "username": str(login_data.get("username", "")).strip(),
            "password": str(login_data.get("password", "")),
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ConfigurationError(
                "Missing required login test data fields: " + ", ".join(missing)
            )

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
            username=required["username"],
            password=required["password"],
            captcha=str(login_data.get("captcha", "12345")).strip() or None,
            browser=browser,
            headless=os.getenv("UUCMS_HEADLESS", "false").strip().lower() in {"1", "true", "yes"},
            timeout_ms=timeout_ms,
        )


def load_test_data(file_name: str) -> dict:
    data_path = Path(__file__).parents[2] / "test_data" / file_name
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigurationError(f"Missing test data file: {data_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"Invalid JSON in test data file: {data_path}") from exc
    if not isinstance(data, dict):
        raise ConfigurationError(f"Test data must contain a JSON object: {data_path}")
    return data
