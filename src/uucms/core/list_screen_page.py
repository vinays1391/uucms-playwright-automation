"""Shared base for R&D list screens (R&D Phase 2).

Combines the data-driven form helpers from DataDrivenFormPage with the
row-lookup, row-action and list-column assertions used by the Phase-2
list screens (governing bodies, committee mapping, fee configuration,
special requests, progress reports, symposium and convocation). Every
selector comes from the matching test_data/rnd/*.json file.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Locator, expect

from uucms.core.data_driven_form_page import DataDrivenFormPage


class ListScreenPage(DataDrivenFormPage):
    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        """Apply the list's filter actions (select_label, multiselect_labels, ...)."""
        self.execute_actions(list(filters))

    def expect_list_columns(self, columns: Sequence[str]) -> None:
        for column in columns:
            expect(self.page.get_by_text(column, exact=True)).to_be_visible()

    def find_row(self, row_selector: str) -> Locator:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        return row.first

    def expect_row_text(self, row_selector: str, text: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(text)

    def expect_row_values(self, row_selector: str, values: Sequence[str]) -> None:
        """Assert that every value is visible inside the row."""
        self.find_row(row_selector)
        row = self.page.locator(row_selector).first
        for value in values:
            expect(row).to_contain_text(str(value))

    def expect_row_absent(self, row_selector: str) -> None:
        expect(self.page.locator(row_selector)).to_have_count(0)

    def open_row_action(self, row_selector: str, action_selector: str) -> None:
        """Open a row action (Map, View, Edit, Submit, ...) on a list screen."""
        self.find_row(row_selector)
        action = self.page.locator(action_selector)
        action.first.wait_for(state="visible")
        action.first.click()

    def expect_action_available(self, row_selector: str, action_selector: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(action_selector)).to_be_visible()

    def expect_action_not_available(self, row_selector: str, action_selector: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(action_selector)).to_have_count(0)

    def expect_rows_listed(self, present: Sequence[str], absent: Sequence[str]) -> None:
        """Assert text-based row presence/absence (USNs, names, IDs)."""
        for value in present:
            expect(self.page.get_by_text(str(value), exact=True)).to_be_visible()
        for value in absent:
            expect(self.page.get_by_text(str(value), exact=True)).to_have_count(0)

    def collect_select_options(self, select_selector: str) -> list[str]:
        """Read the visible option labels of a native dropdown."""
        select = self.page.locator(select_selector)
        select.first.wait_for(state="visible")
        return [
            option.strip()
            for option in select.first.locator("option").evaluate_all(
                "els => els.map(option => option.textContent.trim())"
            )
            if option
        ]

    def expect_select_options(self, select_selector: str,
                              expected_options: Sequence[str]) -> None:
        """Assert a dropdown offers exactly the documented options."""
        options = self.collect_select_options(select_selector)
        missing = [option for option in expected_options if option not in options]
        if missing:
            raise ValueError(
                f"Dropdown {select_selector} is missing options {missing}; "
                f"available: {options}"
            )

    def expect_options_in_container(self, container_selector: str,
                                    present: Sequence[str],
                                    absent: Sequence[str]) -> None:
        """Assert option labels inside an opened (multiselect) list container."""
        container = self.page.locator(container_selector)
        container.first.wait_for(state="visible")
        for label in present:
            expect(container.get_by_title(str(label), exact=True)
                   .or_(container.get_by_text(str(label), exact=True))).to_be_visible()
        for label in absent:
            expect(container.get_by_title(str(label), exact=True)
                   .or_(container.get_by_text(str(label), exact=True))).to_have_count(0)

    def read_cell_text(self, cell_selector: str) -> str:
        cell = self.page.locator(cell_selector)
        cell.first.wait_for(state="visible")
        return cell.first.inner_text().strip()

    def collect_cell_texts(self, cell_selector: str) -> list[str]:
        """Read every cell matched by a test-data selector."""
        cells = self.page.locator(cell_selector)
        cells.first.wait_for(state="visible")
        return cells.evaluate_all(
            "els => els.map(el => el.innerText.trim())"
        )
