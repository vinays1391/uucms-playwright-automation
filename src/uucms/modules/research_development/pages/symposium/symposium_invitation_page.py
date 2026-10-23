"""R&D > Symposium > Invite Scholars for Final Viva Voce, Colloquium or
Symposium (Doctoral Committee Chairperson).

Only scholars whose final progress report is submitted and approved are
listed. The DCC chooses the Panel of Examiners, Date and Time, Duration
Allocated (In Minutes), Conduction Mode and Venue/Online Link, then
Sends the Invitation (Yet to Send -> Scheduled). After the event date &
time has passed the row moves to Yet to Upload Details where the DCC
uploads the event details and Approves or Rejects; a Rejected scholar
can be re-invited for the next symposium. Every selector comes from the
test-data file (see test_data/rnd/symposium.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import SYMPOSIUM_INVITATION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class SymposiumInvitationPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(SYMPOSIUM_INVITATION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def view_scholars(self, filters: Sequence[dict], view_button: str) -> None:
        """Select Academic Year/Cycle and click View List of Final Progress
        Report Submitted and Approved Scholars."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def expect_scholars_listed(self, present: Sequence[str], absent: Sequence[str]) -> None:
        self.expect_rows_listed(present, absent)

    def fill_invitation(self, actions: Sequence[dict]) -> None:
        """Panel of Examiners, Date and Time, Duration, Conduction Mode and
        Venue/Online Link via test-data actions."""
        self.execute_actions(list(actions))

    def send_invitation(self, row_selector: str, actions: Sequence[dict],
                        send_selector: str,
                        success_selector: str | None = None) -> None:
        """Send the invitation: status changes from Yet to Send to Scheduled."""
        self.find_row(row_selector)
        self.fill_invitation(actions)
        self.click_guarded(send_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def edit_schedule(self, row_selector: str, edit_action: str,
                      date_time_field: str, date_time: str,
                      duration_field: str, duration: str,
                      save_selector: str,
                      success_selector: str | None = None) -> None:
        """Edit Schedule of a Scheduled (or re-invited) event."""
        self.open_row_action(row_selector, edit_action)
        self.fill_field(date_time_field, date_time)
        self.fill_field(duration_field, duration)
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def open_event_details(self, row_selector: str, upload_action: str) -> None:
        """Open the event details screen (Yet to Upload Details rows)."""
        self.open_row_action(row_selector, upload_action)

    def expect_status(self, row_selector: str, status: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(status)

    def send_re_invitation(self, row_selector: str, re_invite_action: str,
                           actions: Sequence[dict], send_selector: str,
                           success_selector: str | None = None) -> None:
        """Re-invite a Rejected scholar for the next symposium."""
        self.open_row_action(row_selector, re_invite_action)
        self.fill_invitation(actions)
        self.click_guarded(send_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def open_approved_report(self, row_selector: str, view_action: str) -> None:
        """View Approved Final Report action on the DCC list."""
        self.open_row_action(row_selector, view_action)
