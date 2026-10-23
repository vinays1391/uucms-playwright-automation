"""Exam module screen for assigning/approving students at exam centers."""

from collections.abc import Mapping, Sequence

from uucms.core.data_driven_form_page import DataDrivenFormPage


class ExamCenterPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def approve_students(self, stage: Mapping[str, object]) -> None:
        self.open_from_menu(stage["menu_path"])
        self.execute_actions(list(stage["filters"]))
        exam_month = stage.get("exam_month_selector")
        if exam_month:
            self.click_control(str(exam_month))
        self.click_guarded(str(stage["confirm_selector"]))
        self.expect_saved(str(stage["success_selector"]))
