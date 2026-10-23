"""R&D > Governing Bodies > Set-Up > Create Committees screen.

University Admin (and College Admin) create committees of type Board of
Studies / Doctoral Committee / Panel of Examiners / Research Review
Committee. The Committee ID follows the pattern prefix + University ID +
3-digit code (e.g. BS18001). Every selector comes from the test-data
file (see test_data/rnd/governing_bodies.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import GOVERNING_BODY_CREATE_COMMITTEES
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class CommitteesPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(GOVERNING_BODY_CREATE_COMMITTEES)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def open_create_screen(self, add_screen_action: str) -> None:
        """Open the committee creation form from the committee list (if a
        separate Add/Setup action is required)."""
        self.click_control(add_screen_action)

    def fill_create_form(self, actions: Sequence[dict]) -> None:
        """Fill Committee Type/ID/Name/Name in Kannada/Purpose via test-data actions."""
        self.execute_actions(list(actions))

    def create_committee(self, actions: Sequence[dict], add_selector: str,
                         success_selector: str | None = None) -> None:
        self.fill_create_form(actions)
        self.submit(add_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_create_invalid(self, actions: Sequence[dict], add_selector: str,
                               message: str) -> None:
        """Create with an invalid Committee ID / blank type: validation dialog."""
        self.fill_create_form(actions)
        self.submit_expect_validation(add_selector, message)

    def delete_committee(self, row_selector: str, delete_selector: str,
                         confirm_selector: str,
                         success_selector: str | None = None) -> None:
        """Delete a committee row and confirm the deletion."""
        self.open_row_action(row_selector, delete_selector)
        self.click_guarded(confirm_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def submit_committees(self, submit_selector: str, back_selector: str,
                          success_selector: str | None = None) -> None:
        """Submit the added committees, then Back to the Governing Bodies menu."""
        self.click_guarded(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
        self.click_control(back_selector)

    def expect_member_actions(self, row_selector: str,
                              action_texts: Sequence[str]) -> None:
        """TC-GOVERNINGBODY-008: the Action column offers Map / View / Edit Members."""
        self.find_row(row_selector)
        row = self.page.locator(row_selector).first
        for text in action_texts:
            expect(row.get_by_text(text, exact=True)).to_be_visible()

    def expect_committee_not_created(self, committee_id: str) -> None:
        expect(self.page.get_by_text(committee_id, exact=True)).to_have_count(0)
