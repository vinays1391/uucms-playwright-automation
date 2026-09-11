from collections.abc import Mapping
import re

from playwright.sync_api import Page, expect

from src.pages.base_page import BasePage


class CreateNotificationPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def open_from_menu(self) -> None:
        exam_link = self.page.get_by_role("link", name="Exam", exact=True)
        exam_link.wait_for(state="visible")
        exam_link.click()

        notification_links = self.page.get_by_role(
            "link", name="Exam Notification"
        )
        notification_links.first.wait_for(state="visible")
        notification_links.first.click()
        if notification_links.count() > 1:
            notification_links.nth(1).wait_for(state="visible")
            notification_links.nth(1).click()

        add_link = self.page.get_by_role(
            "link", name="Add New Exam Notification"
        )
        add_link.wait_for(state="visible")
        add_link.click()

    def execute_actions(self, actions: list[Mapping[str, object]]) -> None:
        for action in actions:
            action_type = str(action.get("type", "")).strip().lower()
            selector = str(action.get("selector", "")).strip()
            value = action.get("value", "")
            if not selector:
                raise ValueError("Every notification action needs a selector")

            locator = self.page.locator(selector)
            if action_type == "fill":
                locator.fill(str(value))
            elif action_type == "select_value":
                locator.select_option(str(value))
            elif action_type == "select_label":
                locator.select_option(label=self._resolve_labels(locator, [str(value)])[0])
            elif action_type == "select_labels":
                labels = [item.strip() for item in str(value).split(",") if item.strip()]
                if not labels:
                    raise ValueError(f"Action needs at least one label: {selector}")
                resolved_labels = self._resolve_labels(locator, labels)
                locator.select_option(label=resolved_labels)
                self._sync_multiselect_ui(locator, resolved_labels)
            elif action_type == "multiselect_labels":
                labels = [item.strip() for item in str(value).split(",") if item.strip()]
                if not labels:
                    raise ValueError(f"Action needs at least one label: {selector}")
                trigger = next(
                    (locator.nth(index) for index in range(locator.count()) if locator.nth(index).is_visible()),
                    locator.first,
                )
                trigger.click()
                menu = trigger.locator("xpath=..//div[contains(@class, 'multiselect-container')]")
                for label in labels:
                    option = menu.get_by_title(label, exact=True)
                    if option.count() > 0:
                        option.first.click()
                    else:
                        checkbox = menu.get_by_role("checkbox", name=label, exact=True)
                        if checkbox.count() > 0:
                            checkbox.first.check()
                        else:
                            menu.get_by_text(label, exact=True).click()
            elif action_type == "click":
                self._raise_for_validation_dialog()
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        candidate.click()
                        self._raise_for_validation_dialog()
                        break
                else:
                    locator.first.click()
                    self._raise_for_validation_dialog()
            elif action_type == "check":
                locator.check()
            elif action_type == "press":
                locator.press(str(value))
            elif action_type == "upload":
                locator.set_input_files(str(value))
            else:
                raise ValueError(f"Unsupported notification action: {action_type}")

    def expect_saved(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()

    def _raise_for_validation_dialog(self) -> None:
        dialog = self.page.locator(".bootbox.show[role='dialog']")
        if dialog.is_visible():
            raise ValueError(f"Application validation dialog: {dialog.inner_text()}")

    def _resolve_labels(self, locator, requested_labels: list[str]) -> list[str]:
        options = locator.locator("option")
        options.first.wait_for(state="attached")
        for requested in requested_labels:
            exact_option = options.filter(
                has_text=re.compile(f"^{re.escape(requested.strip())}$")
            )
            expect(exact_option).to_have_count(1)
        available = options.evaluate_all(
            "els => els.map(option => ({label: option.textContent, value: option.value}))"
        )
        resolved = []
        for requested in requested_labels:
            match = next(
                (
                    option["label"].strip()
                    for option in available
                    if option["label"].strip().casefold() == requested.strip().casefold()
                ),
                None,
            )
            if match is None:
                labels = ", ".join(option["label"].strip() for option in available)
                raise ValueError(
                    f"Option {requested!r} was not found. Available options: {labels}"
                )
            resolved.append(match)
        return resolved

    def _sync_multiselect_ui(self, locator, labels: list[str]) -> None:
        for label in labels:
            option = self.page.get_by_title(label, exact=True)
            if option.count() and option.first.is_visible():
                option.first.click()
        trigger = locator.locator("xpath=following-sibling::div//button")
        if trigger.count() and trigger.first.is_visible():
            trigger.first.press("Escape")