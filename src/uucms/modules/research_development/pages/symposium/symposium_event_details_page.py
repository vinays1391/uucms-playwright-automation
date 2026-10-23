"""R&D symposium event details screen (Doctoral Committee Chairperson).

Shows the student details, Department, Panel of Examiners, Research
Title Name, event type, date & time, duration, venue/online link and
conduction mode, plus the mandatory fields Media of the Scholar's
Event (Upload), Enter Media Link and Upload Supporting Document with
the Approve / Reject actions. Every selector comes from the test-data
file (see test_data/rnd/symposium.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.core.data_driven_form_page import DataDrivenFormPage


class SymposiumEventDetailsPage(DataDrivenFormPage):
    def expect_event_details(self, fields: Sequence[str]) -> None:
        for field in fields:
            expect(self.page.get_by_text(field, exact=True)).to_be_visible()

    def choose_event_type(self, event_type_select: str, event_type: str) -> None:
        select = self.page.locator(event_type_select)
        select.first.wait_for(state="visible")
        select.first.select_option(label=event_type)

    def upload_details(self, media_input: str, media_path: str,
                       media_link_field: str, media_link: str,
                       support_input: str, support_path: str) -> None:
        """Upload Media of the Scholar's Event, enter the Media Link and
        upload the Supporting Document."""
        self.upload_file(media_input, media_path)
        self.fill_field(media_link_field, media_link)
        self.upload_file(support_input, support_path)

    def approve(self, approve_selector: str, success_selector: str | None = None) -> None:
        self.click_guarded(approve_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_approve(self, approve_selector: str, message: str) -> None:
        """Approve with mandatory details missing: validation error."""
        self.submit_expect_validation(approve_selector, message)

    def reject(self, reject_selector: str, success_selector: str | None = None) -> None:
        self.click_guarded(reject_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
