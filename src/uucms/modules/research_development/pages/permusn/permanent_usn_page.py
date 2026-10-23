"""R&D permanent USN screens.

University Admin forwards the provisional USN of a synopsis-approved
student; the Superintendent and Registrar (Admin) work the approval
queue; the student is then notified and treated as a Ph.D scholar.
Screen, row, action and success selectors come from the test-data file
(see test_data/rnd/permanent_usn.example.json).
"""

from collections.abc import Mapping, Sequence
import re

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import PERMANENT_USN
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class PermanentUsnPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(PERMANENT_USN)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def expect_row_present(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_be_visible()

    def expect_row_text(self, row_selector: str, text: str) -> None:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        expect(row.first).to_contain_text(text)

    def expect_students_listed(self, present: Sequence[str], absent: Sequence[str]) -> None:
        for student in present:
            expect(self.page.get_by_text(str(student), exact=True)).to_be_visible()
        for student in absent:
            expect(self.page.get_by_text(str(student), exact=True)).to_have_count(0)

    def send_for_approval(self, row_selector: str, send_selector: str,
                          success_selector: str) -> None:
        """University Admin: send the provisional USN for Superintendent approval."""
        self.expect_row_present(row_selector)
        self.click_guarded(send_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def open_request(self, row_selector: str, action_selector: str) -> None:
        """Open a pending permanent-USN request in the approval queue."""
        self.expect_row_present(row_selector)
        action = self.page.locator(action_selector)
        action.first.wait_for(state="visible")
        action.first.click()

    def approve_request(self, row_selector: str, action_selector: str,
                        approve_selector: str, success_selector: str | None = None) -> None:
        """Superintendent / Registrar (Admin): approve the request."""
        self.open_request(row_selector, action_selector)
        self.click_guarded(approve_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def reject_request(self, row_selector: str, action_selector: str,
                       remarks_field: str, remarks: str,
                       reject_selector: str, success_selector: str | None = None) -> None:
        """Superintendent: reject the request with remarks."""
        self.open_request(row_selector, action_selector)
        self.fill_field(remarks_field, remarks)
        self.click_guarded(reject_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def read_permanent_usn(self, usn_selector: str) -> str:
        usn = self.page.locator(usn_selector)
        usn.first.wait_for(state="visible")
        return usn.first.inner_text().strip()

    def expect_usn_format(self, usn: str, pattern: str) -> None:
        if not re.fullmatch(pattern, usn):
            raise ValueError(
                f"Permanent USN {usn!r} does not match the configured "
                f"format {pattern!r}"
            )

    def expect_usn_different_from(self, usn: str, other_usn: str) -> None:
        if usn == other_usn:
            raise ValueError(
                f"Permanent USN {usn!r} is not different from {other_usn!r}"
            )

    def collect_usns(self, usn_cell_selector: str) -> list[str]:
        """Read every USN cell of a list (for uniqueness verification)."""
        cells = self.page.locator(usn_cell_selector)
        cells.first.wait_for(state="visible")
        return cells.evaluate_all(
            "els => els.map(el => el.innerText.trim())"
        )

    def expect_notification(self, notification_selector: str, text: str | None = None) -> None:
        notification = self.page.locator(notification_selector)
        notification.first.wait_for(state="visible")
        if text:
            expect(notification.first).to_contain_text(text)

    def expect_scholar_status(self, profile_selector: str, status_text: str) -> None:
        profile = self.page.locator(profile_selector)
        profile.first.wait_for(state="visible")
        expect(profile.first).to_contain_text(status_text)
