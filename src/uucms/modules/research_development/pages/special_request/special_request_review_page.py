"""R&D > Special Requests review screen (Department Chairperson /
Doctoral Committee Chairperson).

Shows the student's details, Request Type, Reason, the uploaded
Supporting Document (View/Download), the preferred faculty list with a
per-preference Approve action (guide change), the Fees Paid status and
the review actions: Approve / Reject with Enter Remarks. Every selector
comes from the test-data file (see
test_data/rnd/special_requests.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.core.data_driven_form_page import DataDrivenFormPage


class SpecialRequestReviewPage(DataDrivenFormPage):
    def expect_student_details(self, details: Sequence[str]) -> None:
        for detail in details:
            expect(self.page.get_by_text(str(detail), exact=True)).to_be_visible()

    def expect_review_sections(self, sections: Sequence[str]) -> None:
        for section in sections:
            expect(self.page.get_by_text(section, exact=True)).to_be_visible()

    def expect_document_available(self, view_selector: str, download_selector: str) -> None:
        expect(self.page.locator(view_selector)).to_be_visible()
        expect(self.page.locator(download_selector)).to_be_visible()

    def expect_preferred_faculty_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def expect_fee_paid_status(self, status: str) -> None:
        expect(self.page.get_by_text(status, exact=True)).to_be_visible()

    def approve(self, approve_selector: str, success_selector: str | None = None) -> None:
        self.click_guarded(approve_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def approve_faculty(self, faculty_selector: str, approve_selector: str,
                        success_selector: str | None = None) -> None:
        """Approve one specific preferred faculty row (per-preference action)."""
        faculty = self.page.locator(faculty_selector)
        faculty.first.wait_for(state="visible")
        approve = self.page.locator(approve_selector)
        approve.first.wait_for(state="visible")
        self._raise_for_validation_dialog()
        approve.first.click()
        self._raise_for_validation_dialog()
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def reject(self, remarks_field: str, remarks: str, reject_selector: str,
               success_selector: str | None = None) -> None:
        self.fill_field(remarks_field, remarks)
        self.click_guarded(reject_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def expect_request_status(self, status: str) -> None:
        expect(self.page.get_by_text(status, exact=True)).to_be_visible()

    def expect_field_value(self, field_selector: str, value: str) -> None:
        field = self.page.locator(field_selector)
        field.first.wait_for(state="visible")
        expect(field.first).to_contain_text(value)

    def expect_allocated_guide(self, check_selector: str, guide: str) -> None:
        check = self.page.locator(check_selector)
        check.first.wait_for(state="visible")
        expect(check.first).to_contain_text(guide)

    def expect_not_allocated(self, check_selector: str, faculties: Sequence[str]) -> None:
        """The other preferred faculty rows are not allocated."""
        check = self.page.locator(check_selector)
        check.first.wait_for(state="visible")
        for faculty in faculties:
            expect(check.first).not_to_contain_text(str(faculty))
