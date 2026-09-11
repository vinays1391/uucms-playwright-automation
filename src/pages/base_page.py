from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        self.page = page
        self.page.set_default_timeout(timeout_ms)
        self.page.set_default_navigation_timeout(timeout_ms * 2)

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="commit")
