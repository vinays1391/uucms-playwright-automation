"""Exam module screen for direct entry of evaluation marks."""

from collections.abc import Mapping, Sequence

from uucms.core.data_driven_form_page import DataDrivenFormPage


class EvaluationMarksPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def enter_marks(self, stage: Mapping[str, object]) -> None:
        self.open_from_menu(stage["menu_path"])
        self.execute_actions(list(stage["filters"]))
        self.click_guarded(str(stage["view_selector"]))
        self.click_guarded(str(stage["enter_marks_selector"]))
        self.execute_actions(list(stage["college_filters"]))
        present = stage.get("present_checkbox")
        if present:
            self.page.locator(str(present)).first.check()
        for field in stage["marks_fields"]:
            self.fill_field(str(field["selector"]), str(field["value"]))
        for _ in range(int(stage.get("save_cycles", 1))):
            self.submit(str(stage["save_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
