"""Coursework: Registrar (Evaluation) Modify Student Courses screen.

Look up the student by registration number, open the registered courses
and submit the modification cycles. Selectors and values come from
test_data/academics/coursework_examination.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CourseModificationPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def modify_student_courses(self, stage: Mapping[str, object]) -> None:
        reg_no = str(stage.get("student_reg_no_value", "")).strip()
        if reg_no:
            self.fill_field(str(stage["student_reg_no_field"]), reg_no)
        self.submit(str(stage["submit_selector"]))
        self.click_guarded(str(stage["course_registration_selector"]))
        for _ in range(int(stage.get("submit_cycles", 1))):
            self.submit(str(stage["submit_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
        self.click_control(str(stage["back_selector"]))
