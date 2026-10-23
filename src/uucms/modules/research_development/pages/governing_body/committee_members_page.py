"""R&D > Governing Bodies > Map / View / Edit Members to Committee screens.

Faculty (teaching staff only) are mapped to a committee with a Committee
Member Type (Chairperson, Member, Member Secretary), a phone number and
an email id. Only one Chairperson is allowed per committee. Every
selector comes from the test-data file (see
test_data/rnd/governing_bodies.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import GOVERNING_BODY_MAP_MEMBERS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class CommitteeMembersPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(GOVERNING_BODY_MAP_MEMBERS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def open_map_members(self, row_selector: str, map_action: str) -> None:
        """From the committee list: open Map Members to Committee."""
        self.open_row_action(row_selector, map_action)

    def open_view_members(self, row_selector: str, view_action: str) -> None:
        self.open_row_action(row_selector, view_action)

    def open_edit_members(self, row_selector: str, edit_action: str) -> None:
        self.open_row_action(row_selector, edit_action)

    def fill_mapping_form(self, actions: Sequence[dict]) -> None:
        """Fill the mapping form: filters, committee, faculty, member type,
        phone and email via test-data actions."""
        self.execute_actions(list(actions))

    def map_member(self, actions: Sequence[dict], add_selector: str,
                   map_selector: str, success_selector: str | None = None) -> None:
        """Add the member row and Map it to the committee."""
        self.fill_mapping_form(actions)
        self.submit(add_selector)
        self.click_guarded(map_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_add_member(self, actions: Sequence[dict], add_selector: str,
                           message: str) -> None:
        """Add a member row with a validation error (blank employee, second
        Chairperson, ...)."""
        self.fill_mapping_form(actions)
        self.submit_expect_validation(add_selector, message)

    def edit_contact_details(self, actions: Sequence[dict], save_selector: str,
                             success_selector: str | None = None) -> None:
        """Edit Members to Committee: update phone/email and save."""
        self.fill_mapping_form(actions)
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def delete_mapped_member(self, row_selector: str, delete_selector: str,
                             confirm_selector: str,
                             success_selector: str | None = None) -> None:
        self.open_row_action(row_selector, delete_selector)
        self.click_guarded(confirm_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
