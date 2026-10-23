"""R&D > Research Progress > Submissions list screen (all roles).

Scholar, Guide, Co-Guide, Department Chairperson and Doctoral Committee
Chairperson share the same list shape: Progress Report ID, submission
deadline, Progress Report Submission Status, Action Pending With and
the row actions (Submit Progress Report / View Progress Report).
Statuses and "Action Pending With" values use the master-table
constants from src/uucms/constants/statuses.py; every selector comes from the
test-data file (see test_data/rnd/progress_report.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import Locator, expect

from uucms.constants.menu_paths.research_development import PROGRESS_REPORT_SUBMISSIONS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ProgressSubmissionsPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(PROGRESS_REPORT_SUBMISSIONS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def apply_filters(self, filters: Sequence[dict]) -> None:
        """Select Academic Year (required), Cycle and, for reviewers, the
        Latest Report Submission Status filter."""
        self.execute_actions(list(filters))

    def expect_row_status(self, row_selector: str, status: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(status)

    def expect_row_pending_with(self, row_selector: str, pending_with: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(pending_with)

    def submit_report(self, row_selector: str, action_selector: str,
                      brief_field: str, brief: str,
                      doc_input: str, doc_path: str,
                      submit_selector: str,
                      success_selector: str | None = None) -> None:
        """Scholar: Submit Progress Report with brief details and document."""
        self.open_row_action(row_selector, action_selector)
        self.fill_field(brief_field, brief)
        self.upload_file(doc_input, doc_path)
        self.submit(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_submit_blank_brief(self, row_selector: str, action_selector: str,
                                   doc_input: str, doc_path: str,
                                   submit_selector: str, message: str) -> None:
        """Submit with Brief details blank: required-field validation."""
        self.open_row_action(row_selector, action_selector)
        self.upload_file(doc_input, doc_path)
        self.submit_expect_validation(submit_selector, message)

    def attempt_submit_without_document(self, row_selector: str, action_selector: str,
                                        brief_field: str, brief: str,
                                        submit_selector: str, message: str) -> None:
        """Submit without the report document: required-field validation."""
        self.open_row_action(row_selector, action_selector)
        self.fill_field(brief_field, brief)
        self.submit_expect_validation(submit_selector, message)

    def attempt_upload_invalid_file(self, row_selector: str, action_selector: str,
                                    doc_input: str, invalid_file: str,
                                    message: str) -> None:
        """Upload an unsupported file type: rejected with an error message."""
        self.open_row_action(row_selector, action_selector)
        field = self.page.locator(doc_input)
        field.first.wait_for(state="attached")
        field.first.set_input_files(str(invalid_file))
        expect(self.page.get_by_text(message)).to_be_visible()

    def expect_deadline_message(self, message: str) -> None:
        """Exact deadline-expired message on the scholar's list."""
        expect(self.page.get_by_text(message)).to_be_visible()

    def read_report_id(self, row_selector: str, id_cell_selector: str) -> str:
        self.find_row(row_selector)
        cell = self.page.locator(id_cell_selector)
        cell.first.wait_for(state="visible")
        return cell.first.inner_text().strip()

    def expect_review_sections(self, sections: Sequence[str]) -> None:
        for section in sections:
            expect(self.page.get_by_text(section, exact=True)).to_be_visible()
