"""R&D: Discipline Wise - Area of Research Mapping screen.

University Admin views, adds and deletes Areas of Research under a
program/discipline. Field, button, row and success selectors come from
the test-data file (see test_data/rnd/area_of_research.example.json).
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import AREA_OF_RESEARCH_MAPPING
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class AreaOfResearchPage(DataDrivenFormPage):
    def open_from_menu(self) -> None:
        MenuPage(self.page, self.page.default_timeout()).open_menu(
            AREA_OF_RESEARCH_MAPPING
        )

    def select_filters(self, actions: Sequence[Mapping[str, object]]) -> None:
        """Select Program Level, Program Name and Discipline."""
        self.execute_actions(list(actions))

    def expect_list_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def expect_row_present(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_be_visible()

    def click_add(self, add_selector: str) -> None:
        self.click_control(add_selector)

    def fill_add_form(self, actions: Sequence[Mapping[str, object]]) -> None:
        """Enter Area of Research Code, Name and Short Form."""
        self.execute_actions(list(actions))

    def submit_add(self, submit_selector: str, success_selector: str) -> None:
        self.submit(submit_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def click_back(self, back_selector: str, list_selector: str) -> None:
        """Click Back and confirm the list screen is back (draft discarded)."""
        self.click_control(back_selector)
        expect(self.page.locator(list_selector)).to_be_visible()

    def delete_area(self, row_selector: str, delete_selector: str,
                    confirm_selector: str) -> None:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        delete = self.page.locator(delete_selector)
        delete.first.wait_for(state="visible")
        delete.first.click()
        confirm = self.page.locator(confirm_selector)
        confirm.first.wait_for(state="visible")
        confirm.first.click()

    def expect_row_removed(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_have_count(0)
