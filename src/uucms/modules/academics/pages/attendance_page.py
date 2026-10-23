"""Coursework: student attendance entry screen (Registrar view).

Enter the classes conducted and classes attended per lecture row.
Selectors and values come from
test_data/academics/coursework_examination.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class AttendancePage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def enter_attendance(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["edit_selector"]))
        classes_field = str(stage["classes_field"])
        attended_field = str(stage["attended_field"])
        for lecture in stage["lectures"]:
            row = self.page.locator(str(lecture["row_selector"]))
            row.first.wait_for(state="visible")
            row.locator(classes_field).first.fill(str(lecture["classes_value"]))
            row.locator(attended_field).first.fill(str(lecture["attended_value"]))
        student_header = stage.get("student_header_selector")
        if student_header:
            self.click_control(str(student_header))
        self.submit(str(stage["save_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
