"""Environment configuration helpers for browser and runtime settings."""

from dataclasses import dataclass


@dataclass
class EnvironmentSettings:
    base_url: str = "http://123.63.4.210:5010/"
    browser: str = "chromium"
    headless: bool = False
    timeout_ms: int = 15000


def get_environment_settings() -> EnvironmentSettings:
    return EnvironmentSettings()
