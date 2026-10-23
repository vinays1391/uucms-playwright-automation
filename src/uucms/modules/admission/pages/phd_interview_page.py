"""Ph.D admission: Department Chairperson interview screens.

Invite Ph.D candidates for the interview (per-row selection and date) and
enter the interview marks, then send them for Registrar (Admin) approval.
Selectors and values come from test_data/admission/phd_admission.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Locator, Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class PhdInterviewPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def view_student_details(self, selector: str, row_text: str | None = None) -> None:
        self.click_guarded(self.row_scoped_selector(selector, row_text))

    def send_interview_invites(self, stage: Mapping[str, object]) -> None:
        row_expand = stage.get("row_expand_selector")
        checkbox_selector = str(stage.get("checkbox_selector", "#TrChkBoxSelect"))
        for student in stage["students"]:
            row = self.row_locator(student)
            row.first.wait_for(state="visible")
            if row_expand:
                row.locator(str(row_expand)).first.click()
            row.locator(checkbox_selector).first.check()
            self._pick_row_date(row, str(student["date_day"]))
        self.click_guarded(str(stage["send_selector"]))
        for _ in range(int(stage.get("confirmation_count", 1))):
            self.click_guarded(str(stage["confirm_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def enter_interview_marks(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["edit_marks_selector"]))
        for field in stage["marks_fields"]:
            self.fill_field(str(field["selector"]), str(field["value"]))
        self.submit(str(stage["save_marks_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.wait_loader_gone()
        self.click_guarded(str(stage["ok_selector"]))
        self.click_guarded(str(stage["send_registrar_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.wait_loader_gone()
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def _pick_row_date(self, row: Locator, date_day: str) -> None:
        date_cell = row.get_by_placeholder("Click to Select Date")
        if date_cell.count():
            date_cell.first.click()
        day = self.page.get_by_role("link", name=date_day, exact=True)
        day.first.wait_for(state="visible")
        day.first.click()
