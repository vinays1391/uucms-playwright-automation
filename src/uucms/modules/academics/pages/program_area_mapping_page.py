"""Academics > Program Details: University Admin maps an Area of Research
to the Ph.D program (create research area under a discipline, and delete
existing mappings). Selectors and values come from
test_data/rnd/phd_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class ProgramAreaMappingPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def search_program(self, search_selector: str, search_term: str,
                       program_cell: str) -> None:
        search = self.page.locator(search_selector)
        search.first.click()
        search.first.fill(search_term)
        cell = self.page.get_by_role("cell", name=program_cell)
        cell.first.wait_for(state="visible")
        cell.first.click()

    def open_map_area_screen(self, link_name: str, link_index: int = 0) -> None:
        links = self.page.get_by_role("link", name=link_name, exact=True)
        index = min(link_index, max(links.count() - 1, 0)) if link_index else 0
        links.nth(index).wait_for(state="visible")
        links.nth(index).click()

    def create_research_area(self, stage: Mapping[str, object]) -> None:
        discipline = stage.get("discipline_button")
        if discipline:
            self.click_guarded(str(discipline))
        self.fill_field(str(stage["research_name_field"]), str(stage["research_name"]))
        self.fill_field(
            str(stage["research_short_name_field"]),
            str(stage["research_short_name"]),
        )
        self.click_guarded(str(stage["add_selector"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def delete_research_areas(self, stage: Mapping[str, object]) -> None:
        count = int(stage.get("delete_count", 0))
        if not count:
            return
        delete = self.page.get_by_text(str(stage["delete_text"]))
        index = int(stage.get("delete_index", 0))
        for _ in range(count):
            actual = min(index, max(delete.count() - 1, 0)) if index else 0
            delete.nth(actual).click()
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["submit_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
