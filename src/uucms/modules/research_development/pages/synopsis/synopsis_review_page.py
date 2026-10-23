"""R&D synopsis review screen (Guide / Co-Guide / Department Chairperson /
Doctoral Committee Chairperson).

The screen shows the student's brief details and uploaded synopsis, the
"Synopsis Review Remarks" of every preceding reviewer (cross-display),
and the review actions: Approve, Send Back and Reject (where available).
All selectors come from the test-data file.
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.core.data_driven_form_page import DataDrivenFormPage


class SynopsisReviewPage(DataDrivenFormPage):
    def expect_document_available(self, view_selector: str, download_selector: str) -> None:
        expect(self.page.locator(view_selector)).to_be_visible()
        expect(self.page.locator(download_selector)).to_be_visible()

    def expect_review_sections(self, sections: Sequence[str]) -> None:
        """Assert the cross-display sections (e.g. 'Synopsis Review Remarks of the Guide')."""
        for section in sections:
            expect(self.page.get_by_text(section, exact=True)).to_be_visible()

    def expect_remarks_visible(self, remarks: Sequence[str]) -> None:
        for remark in remarks:
            expect(self.page.get_by_text(str(remark))).to_be_visible()

    def approve(self, remarks_field: str, remarks: str,
                approve_selector: str, success_selector: str | None = None) -> None:
        """Record review remarks and approve the synopsis at this stage."""
        self.fill_field(remarks_field, remarks)
        self.click_guarded(approve_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def send_back(self, remarks_field: str, remarks: str,
                  send_back_selector: str, success_selector: str | None = None) -> None:
        """Send the synopsis back to the Student with remarks."""
        self.fill_field(remarks_field, remarks)
        self.click_guarded(send_back_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def reject(self, remarks_field: str, remarks: str,
               reject_selector: str, success_selector: str | None = None) -> None:
        """Reject the synopsis with remarks (Guide provision)."""
        self.fill_field(remarks_field, remarks)
        self.click_guarded(reject_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def upload_pre_register_colloquium(self, file_input: str, file_path: str,
                                       submit_selector: str,
                                       success_selector: str | None = None) -> None:
        """Doctoral Committee Chairperson: attach Pre-Register Colloquium details."""
        self.upload_file(file_input, file_path)
        self.click_guarded(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def expect_communication_trail(self, entries: Sequence[str]) -> None:
        """View Synopsis Details: every approve/send-back/reject entry is visible."""
        for entry in entries:
            expect(self.page.get_by_text(str(entry))).to_be_visible()
