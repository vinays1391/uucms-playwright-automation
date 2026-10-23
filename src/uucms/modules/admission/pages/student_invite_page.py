"""Ph.D admission: Student Invite screen.

Select the invited students, set the interview date per row and send the
invites. Selectors and values come from
test_data/admission/phd_admission.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Locator, Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class StudentInvitePage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def view_student_details(self, selector: str, row_text: str | None = None) -> None:
        self.click_guarded(self.row_scoped_selector(selector, row_text))

    def confirm_invites(self, stage: Mapping[str, object]) -> None:
        checkbox_selector = str(stage.get("checkbox_selector", "role=checkbox"))
        for student in stage["students"]:
            row = self.row_locator(student)
            row.first.wait_for(state="visible")
            row.locator(checkbox_selector).first.check()
        select_all = stage.get("select_all_selector")
        if select_all:
            self.page.locator(str(select_all)).first.check()
        for student in stage["students"]:
            row = self.row_locator(student)
            self._pick_row_date(row, str(student["date_day"]))
        self.click_guarded(str(stage["send_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def _pick_row_date(self, row: Locator, date_day: str) -> None:
        date_cell = row.get_by_placeholder("Click to Select Date")
        if date_cell.count():
            date_cell.first.click()
        day = self.page.get_by_role("link", name=date_day, exact=True)
        day.first.wait_for(state="visible")
        day.first.click()
