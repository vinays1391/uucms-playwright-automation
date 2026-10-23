"""Ph.D admission: Department Chairperson entrance exam screens.

Enter Ph.D Candidate Entrance (view student details, edit entrance
marks, send for registrar approval) and the Ph.D cut-off marks setup.
Selectors and values come from test_data/admission/phd_admission.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class EntranceExamPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def view_student_details(self, selector: str, row_text: str | None = None) -> None:
        self.click_guarded(self.row_scoped_selector(selector, row_text))

    def set_cut_off_marks(self, stage: Mapping[str, object]) -> None:
        self.open_from_menu(stage["menu_path"])
        self.apply_filters(stage["filters"])
        self.click_guarded(str(stage["edit_action_selector"]))
        self.expect_saved(str(stage["success_selector"]))
        self.click_control(str(stage["back_selector"]))

    def edit_entrance_marks(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["edit_marks_selector"]))
        for field in stage["marks_fields"]:
            self.fill_field(str(field["selector"]), str(field["value"]))
        self.submit(str(stage["save_marks_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))

    def send_for_registrar_approval(self, send_selector: str) -> None:
        self.click_guarded(send_selector)
        self.wait_loader_gone()
