"""R&D Ph.D admission: Mapping of Area of Research to Faculty screen.

University Admin maps Areas of Research to faculty (Guide, Co-Guide,
Principal Investigator, Mentor). The mapping form supports multiple
employee rows, each added with the Add control and saved with Submit.
Filters, form fields, row actions and success selectors come from the
test-data file (see test_data/rnd/faculty_mapping.example.json).
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import FACULTY_AOR_MAPPING
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class FacultyMappingPage(DataDrivenFormPage):
    def open_from_menu(self) -> None:
        MenuPage(self.page, self.page.default_timeout()).open_menu(FACULTY_AOR_MAPPING)

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        """Select Academic Year (required), Program Level and Program Name."""
        self.execute_actions(list(filters))

    def click_view(self, view_selector: str) -> None:
        self.click_control(view_selector)

    def expect_list_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def expect_list_not_loaded(self, list_selector: str) -> None:
        expect(self.page.locator(list_selector)).to_have_count(0)

    def expect_select_options(self, select_selector: str, present: Sequence[str],
                              absent: Sequence[str] = ()) -> None:
        """Assert which labels are offered by a dropdown (discipline/employee/department rules)."""
        select = self.page.locator(select_selector)
        select.first.wait_for(state="visible")
        options = select.locator("option")
        options.first.wait_for(state="attached")
        labels = options.evaluate_all(
            "els => els.map(option => option.textContent.trim())"
        )
        for label in present:
            if str(label) not in labels:
                raise ValueError(
                    f"Option {label!r} missing from {select_selector}. "
                    f"Available options: {labels}"
                )
        for label in absent:
            if str(label) in labels:
                raise ValueError(
                    f"Option {label!r} should not be in {select_selector}. "
                    f"Available options: {labels}"
                )

    def open_list_action(self, action_selector: str) -> None:
        """Open a list-level action (Map / View Mapped / Modify Mapped)."""
        self.click_control(action_selector)

    def fill_mapping_form(self, actions: Sequence[Mapping[str, object]]) -> None:
        """Fill the mapping form; each employee row ends with an Add click."""
        self.execute_actions(list(actions))

    def submit_mapping(self, submit_selector: str, success_selector: str) -> None:
        self.submit(submit_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def expect_mapped_rows(self, values: Sequence[str]) -> None:
        """Assert the saved mapping is displayed (code, name, dept, employee, type)."""
        for value in values:
            expect(self.page.get_by_text(str(value))).to_be_visible()

    def select_area_codes(self, actions: Sequence[Mapping[str, object]]) -> None:
        """Multi-select Area of Research Codes for View Mapped / Print."""
        self.execute_actions(list(actions))

    def click_print(self, print_selector: str, print_view_selector: str) -> None:
        self.click_control(print_selector)
        expect(self.page.locator(print_view_selector)).to_be_visible()

    def delete_mapping(self, row_selector: str, delete_selector: str,
                       confirm_selector: str, submit_selector: str) -> None:
        """Modify Mapped: delete an eligible mapping row and submit."""
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        delete = self.page.locator(delete_selector)
        delete.first.wait_for(state="visible")
        delete.first.click()
        confirm = self.page.locator(confirm_selector)
        confirm.first.wait_for(state="visible")
        confirm.first.click()
        self.submit(submit_selector)

    def expect_mapping_removed(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_have_count(0)

    def attempt_delete_blocked(self, row_selector: str, delete_selector: str,
                               message: str) -> None:
        """Delete a mapping that must be blocked (student/project in use)."""
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        delete = self.page.locator(delete_selector)
        delete.first.wait_for(state="visible")
        delete.first.click()
        self.expect_validation_dialog(message)

    def expect_mapping_still_present(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_be_visible()

    def back_discards_draft(self, back_selector: str, list_selector: str) -> None:
        """Click Back on the mapping form and confirm the list screen is back."""
        self.click_control(back_selector)
        expect(self.page.locator(list_selector)).to_be_visible()
