"""Create and complete the candidate application form."""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class ApplicationPage(DataDrivenFormPage):
    def open_create_application(self, entry_selector: str, entry_text: str,
                                create_button: str) -> None:
        entry = self.page.locator(entry_selector).get_by_text(entry_text)
        entry.first.wait_for(state="visible")
        entry.first.click()
        self.click_guarded(create_button)

    def select_program(self, actions: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(actions))

    def complete_application(self, actions: Sequence[Mapping[str, object]],
                             submit_selector: str, discipline_selector: str,
                             discipline_value: str, preview_submit_selector: str,
                             declaration_checkbox: str, confirm_selector: str,
                             ok_selector: str, success_selector: str) -> None:
        self.execute_actions(list(actions))
        self.submit(submit_selector)
        self.page.locator(discipline_selector).select_option(discipline_value)
        self.click_guarded(preview_submit_selector)
        self.page.locator(declaration_checkbox).check()
        self.click_guarded(confirm_selector)
        self.click_guarded(ok_selector)
        self.expect_saved(success_selector)
