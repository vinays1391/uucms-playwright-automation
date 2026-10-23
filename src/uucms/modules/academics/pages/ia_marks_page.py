"""Coursework: Internal Assessment Marks entry screen."""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class IaMarksPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def enter_marks(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["edit_selector"]))
        for field in stage["marks_fields"]:
            self.fill_field(str(field["selector"]), str(field["value"]))
        self.submit(str(stage["save_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
        self.click_control(str(stage["back_selector"]))
