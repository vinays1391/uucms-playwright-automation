"""R&D Ph.D admission: University Wise Program Details screen.

List of existing Ph.D programs with the row actions Edit, View,
Map Discipline/Combination, Map Areas of Research and Map New Program.
All field, row, action and success selectors come from the test-data
file (see test_data/rnd/admission_program_details.example.json).
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import PROGRAM_DETAILS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class ProgramDetailsPage(DataDrivenFormPage):
    def open_from_menu(self) -> None:
        MenuPage(self.page, self.page.default_timeout()).open_menu(PROGRAM_DETAILS)

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        """Select the list filters (e.g. academic year, program level)."""
        self.execute_actions(list(filters))

    def expect_list_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def expect_row_present(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_be_visible()

    def expect_row_text(self, row_selector: str, text: str) -> None:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        expect(row.first).to_contain_text(text)

    def open_row_action(self, row_selector: str, action_selector: str) -> None:
        """Open a row action (Edit, View, Map ...) identified from test data."""
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        action = self.page.locator(action_selector)
        action.first.wait_for(state="visible")
        action.first.click()

    def edit_program(self, row_selector: str, edit_action: str,
                     field_actions: Sequence[Mapping[str, object]],
                     save_selector: str) -> None:
        """Edit a program: open the Edit action, update fields, save."""
        self.open_row_action(row_selector, edit_action)
        self.execute_actions(list(field_actions))
        self.submit(save_selector)

    def expect_row_updated(self, row_selector: str, values: Sequence[str]) -> None:
        for value in values:
            self.expect_row_text(row_selector, str(value))

    def view_program(self, row_selector: str, view_action: str) -> None:
        """Open the read-only View of a program."""
        self.open_row_action(row_selector, view_action)

    def expect_read_only_view(self, columns: Sequence[str], save_selector: str) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()
        expect(self.page.locator(save_selector)).to_have_count(0)

    def map_discipline(self, row_selector: str, action_selector: str,
                       mapping_actions: Sequence[Mapping[str, object]],
                       submit_selector: str, success_selector: str) -> None:
        self.open_row_action(row_selector, action_selector)
        self.execute_actions(list(mapping_actions))
        self.submit(submit_selector)
        self.expect_saved(success_selector)

    def map_areas_of_research(self, row_selector: str, action_selector: str,
                              mapping_actions: Sequence[Mapping[str, object]],
                              submit_selector: str, success_selector: str) -> None:
        self.open_row_action(row_selector, action_selector)
        self.execute_actions(list(mapping_actions))
        self.submit(submit_selector)
        self.expect_saved(success_selector)

    def open_map_new_program(self, row_selector: str, action_selector: str) -> None:
        """Open the Map New Program screen for a program row."""
        self.open_row_action(row_selector, action_selector)
