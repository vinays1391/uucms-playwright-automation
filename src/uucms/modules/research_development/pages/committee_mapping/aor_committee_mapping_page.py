"""R&D > Governing Bodies > Mapped Areas of Research screens.

University Admin maps Areas of Research to (Doctoral) Committees and to
students; the mapped committee chairperson then sees the reports of the
mapped students. Modification is restricted once the student has taken
admission, completed course work and submitted the synopsis. Every
selector comes from the test-data file (see
test_data/rnd/committee_mapping.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import MAPPED_AREAS_OF_RESEARCH
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class AorCommitteeMappingPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(MAPPED_AREAS_OF_RESEARCH)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def open_mapping_screen(self, row_selector: str, action_selector: str) -> None:
        """Open one of the row actions: Map / View / Modify Mapped Areas of
        Research to Committees and Students."""
        self.open_row_action(row_selector, action_selector)

    def add_mapping(self, actions: Sequence[dict], add_selector: str,
                    submit_selector: str,
                    success_selector: str | None = None) -> None:
        """Map an Area of Research to a Committee and a Student."""
        self.fill_mapping_form(actions)
        self.submit(add_selector)
        self.click_guarded(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def fill_mapping_form(self, actions: Sequence[dict]) -> None:
        self.execute_actions(list(actions))

    def attempt_add_mapping(self, actions: Sequence[dict], add_selector: str,
                            message: str) -> None:
        """Add with a mandatory-field validation error (Committee Type blank)."""
        self.fill_mapping_form(actions)
        self.submit_expect_validation(add_selector, message)

    def view_mappings(self, actions: Sequence[dict], view_button: str) -> None:
        """View mapped rows with (multi-select) filter actions."""
        self.execute_actions(list(actions))
        self.click_control(view_button)

    def modify_mapping(self, committee_select: str, new_committee: str,
                       submit_selector: str,
                       success_selector: str | None = None) -> None:
        """Modify screen: change the committee for the selected AOR and submit."""
        select = self.page.locator(committee_select)
        select.first.wait_for(state="visible")
        select.first.select_option(label=new_committee)
        self.click_guarded(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_modify_mapping(self, committee_select: str, new_committee: str,
                               submit_selector: str, message: str) -> None:
        """Modify after synopsis submission: blocked with a validation message."""
        select = self.page.locator(committee_select)
        select.first.wait_for(state="visible")
        select.first.select_option(label=new_committee)
        self.submit_expect_validation(submit_selector, message)

    def expect_read_only_view(self, delete_action_selector: str,
                              submit_action_selector: str) -> None:
        """The View screen offers no Delete/Submit actions."""
        expect(self.page.locator(delete_action_selector)).to_have_count(0)
        expect(self.page.locator(submit_action_selector)).to_have_count(0)
