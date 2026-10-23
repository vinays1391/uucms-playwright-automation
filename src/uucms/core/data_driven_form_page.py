"""Base page for data-driven, action-script driven UUCMS forms.

Holds the shared `execute_actions` pattern (fill, select_value,
select_label, select_labels, multiselect_labels, click, check, press,
upload) plus the bootbox validation-dialog guards, so page objects for
form-driven screens do not duplicate the replay logic.
"""

from collections.abc import Mapping, Sequence
import re

from playwright.sync_api import Locator, Page, expect

from uucms.core.base_page import BasePage


class DataDrivenFormPage(BasePage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def execute_actions(self, actions: Sequence[Mapping[str, object]]) -> None:
        for action in actions:
            action_type = str(action.get("type", "")).strip().lower()
            selector = str(action.get("selector", "")).strip()
            value = action.get("value", "")
            if not selector:
                raise ValueError("Every form action needs a selector")

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
            elif action_type == "uncheck":
                locator.uncheck()
            elif action_type == "dblclick":
                locator.dblclick()
            elif action_type == "press":
                locator.press(str(value))
            elif action_type == "upload":
                locator.set_input_files(str(value))
            else:
                raise ValueError(f"Unsupported form action: {action_type}")

    def fill_field(self, selector: str, value: str) -> None:
        field = self.page.locator(selector)
        field.first.wait_for(state="visible")
        field.first.fill(str(value))

    def upload_file(self, selector: str, file_path: str) -> None:
        field = self.page.locator(selector)
        field.first.wait_for(state="attached")
        field.first.set_input_files(str(file_path))

    def click_control(self, selector: str) -> None:
        """Click the first visible element of a test-data selector."""
        control = self.page.locator(selector)
        control.first.wait_for(state="visible")
        control.first.click()

    @staticmethod
    def row_scoped_selector(selector: str, row_text: str | None) -> str:
        """Scope a control selector to the table row containing ``row_text``."""
        name = str(row_text or "").strip()
        if not name:
            return selector
        escaped = name.replace('"', '\\"')
        return f'tr:has-text("{escaped}") >> {selector}'

    def row_locator(self, student: Mapping[str, object]) -> Locator:
        """Locator for a grid row by ``row_text`` (candidate name) or ``row_selector``."""
        name = str(student.get("row_text", "")).strip()
        if name:
            escaped = name.replace('"', '\\"')
            return self.page.locator(f'tr:has-text("{escaped}")')
        return self.page.locator(str(student["row_selector"]))

    def click_guarded(self, selector: str) -> None:
        """Click a control that triggers server-side validation."""
        control = self.page.locator(selector)
        control.first.wait_for(state="visible")
        self._raise_for_validation_dialog()
        control.first.click()
        self._raise_for_validation_dialog()

    def submit(self, selector: str) -> None:
        """Alias of :meth:`click_guarded` for submit controls."""
        self.click_guarded(selector)

    def submit_expect_validation(self, selector: str, message: str) -> None:
        """Click a submit control and assert the expected validation dialog."""
        control = self.page.locator(selector)
        control.first.wait_for(state="visible")
        control.first.click()
        self.expect_validation_dialog(message)

    def expect_saved(self, selector: str) -> None:
        expect(self.page.locator(selector)).to_be_visible()

    def wait_loader_gone(self) -> None:
        """Wait for the transient .loader-modal overlay to disappear."""
        expect(self.page.locator(".loader-modal")).to_have_count(0, timeout=30000)

    def expect_validation_dialog(self, message: str) -> None:
        dialog = self.page.locator(".bootbox.show[role='dialog']")
        expect(dialog).to_be_visible()
        if message:
            expect(dialog).to_contain_text(message)

    def dismiss_validation_dialog(self, ok_selector: str) -> None:
        ok = self.page.locator(ok_selector)
        ok.first.wait_for(state="visible")
        ok.first.click()

    def expect_absent(self, text: str) -> None:
        expect(self.page.get_by_text(text, exact=True)).to_have_count(0)

    def expect_texts_visible(self, texts: Sequence[str]) -> None:
        for text in texts:
            expect(self.page.get_by_text(str(text), exact=True)).to_be_visible()

    def _raise_for_validation_dialog(self) -> None:
        dialog = self.page.locator(".bootbox.show[role='dialog']")
        if dialog.is_visible():
            raise ValueError(f"Application validation dialog: {dialog.inner_text()}")

    def _resolve_labels(self, locator: Locator, requested_labels: list[str]) -> list[str]:
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

    def _sync_multiselect_ui(self, locator: Locator, labels: list[str]) -> None:
        for label in labels:
            option = self.page.get_by_title(label, exact=True)
            if option.count() and option.first.is_visible():
                option.first.click()
        trigger = locator.locator("xpath=following-sibling::div//button")
        if trigger.count() and trigger.first.is_visible():
            trigger.first.press("Escape")
