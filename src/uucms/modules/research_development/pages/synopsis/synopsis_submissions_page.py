"""R&D > Synopsis > Submissions list screen.

Role-specific view of the synopsis master table: the Department
Chairperson sets/re-sets the submission deadline, the Student enters or
re-enters the synopsis, and reviewers open the synopsis from their row
action. Statuses and "Action Pending With" values use the master-table
constants from src/uucms/constants/statuses.py; every selector comes from the
test-data file (see test_data/rnd/synopsis.example.json).
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Locator, expect

from uucms.constants.menu_paths.research_development import SYNOPSIS_SUBMISSIONS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class SynopsisSubmissionsPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(SYNOPSIS_SUBMISSIONS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        """Select Academic Year (required) and Cycle."""
        self.execute_actions(list(filters))

    def expect_list_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def find_row(self, row_selector: str) -> Locator:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        return row.first

    def expect_row_status(self, row_selector: str, status: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(status)

    def expect_row_pending_with(self, row_selector: str, pending_with: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(pending_with)

    def expect_row_text(self, row_selector: str, text: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(text)

    def open_row_action(self, row_selector: str, action_selector: str) -> None:
        """Open the row action for a student (Edit Submission details,
        Enter Synopsis details, Re-Enter, Re-Set-Up Deadline, View ...)."""
        self.find_row(row_selector)
        action = self.page.locator(action_selector)
        action.first.wait_for(state="visible")
        action.first.click()

    def expect_action_available(self, row_selector: str, action_selector: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(action_selector)).to_be_visible()

    def expect_action_not_available(self, row_selector: str, action_selector: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(action_selector)).to_have_count(0)

    def set_submission_deadline(self, row_selector: str, action_selector: str,
                                deadline_field: str, deadline: str,
                                save_selector: str) -> None:
        """Department Chairperson: Edit Submission details and set the deadline."""
        self.open_row_action(row_selector, action_selector)
        self.fill_field(deadline_field, deadline)
        self.submit(save_selector)

    def submit_synopsis(self, row_selector: str, action_selector: str,
                        brief_field: str, brief: str,
                        doc_input: str, doc_path: str,
                        submit_selector: str) -> None:
        """Student: Enter/Re-Enter Synopsis details, upload the document, submit."""
        self.open_row_action(row_selector, action_selector)
        self.fill_field(brief_field, brief)
        self.upload_file(doc_input, doc_path)
        self.submit(submit_selector)

    def attempt_submit_blank_brief(self, row_selector: str, action_selector: str,
                                   doc_input: str, doc_path: str,
                                   submit_selector: str, message: str) -> None:
        """Student submits with Brief details blank: required-field validation."""
        self.open_row_action(row_selector, action_selector)
        self.upload_file(doc_input, doc_path)
        self.submit_expect_validation(submit_selector, message)

    def attempt_submit_without_document(self, row_selector: str, action_selector: str,
                                        brief_field: str, brief: str,
                                        submit_selector: str, message: str) -> None:
        """Student submits without the synopsis document: required-field validation."""
        self.open_row_action(row_selector, action_selector)
        self.fill_field(brief_field, brief)
        self.submit_expect_validation(submit_selector, message)

    def open_eligible_students(self, action_selector: str) -> None:
        self.click_control(action_selector)

    def expect_students_listed(self, present: Sequence[str], absent: Sequence[str]) -> None:
        for student in present:
            expect(self.page.get_by_text(str(student), exact=True)).to_be_visible()
        for student in absent:
            expect(self.page.get_by_text(str(student), exact=True)).to_have_count(0)

    def open_old_synopsis_details(self, row_selector: str, action_selector: str) -> None:
        self.open_row_action(row_selector, action_selector)

    def expect_first_previous_submission(self, dropdown_selector: str, marker: str) -> None:
        """The Previous Synopsis Submission dropdown lists the latest (sent back) first."""
        dropdown = self.page.locator(dropdown_selector)
        dropdown.first.wait_for(state="visible")
        first_option = dropdown.locator("option").first
        first_option.wait_for(state="attached")
        expect(first_option).to_contain_text(marker)

    def select_first_previous_submission(self, dropdown_selector: str) -> None:
        dropdown = self.page.locator(dropdown_selector)
        dropdown.first.wait_for(state="visible")
        first_option = dropdown.locator("option").first
        first_option.wait_for(state="visible")
        first_option.click()

    def expect_old_submission_details(self, sections: Sequence[str],
                                      doc_view_selector: str,
                                      doc_download_selector: str) -> None:
        for section in sections:
            expect(self.page.get_by_text(section, exact=True)).to_be_visible()
        for selector in (doc_view_selector, doc_download_selector):
            expect(self.page.locator(selector)).to_be_visible()

    def collect_cell_texts(self, cell_selector: str) -> list[str]:
        """Read every cell matched by a test-data selector (master-table checks)."""
        cells = self.page.locator(cell_selector)
        cells.first.wait_for(state="visible")
        return cells.evaluate_all(
            "els => els.map(el => el.innerText.trim())"
        )
