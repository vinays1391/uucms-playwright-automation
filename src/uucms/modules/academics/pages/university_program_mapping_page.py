"""University Admin: university-level Program Details mapping — new
program data, discipline/combination mapping, Area of Research mapping
and evaluation system mapping for a Ph.D program. Selectors and values
come from test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class UniversityProgramMappingPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def search_program(self, search_selector: str, search_term: str) -> None:
        self.page.locator(search_selector).first.fill(search_term)

    def map_new_program(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["map_new_program_button"]))
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["add_button"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def map_disciplines(self, stage: Mapping[str, object]) -> None:
        self.search_program(
            str(stage["search_selector"]), str(stage["search_term"])
        )
        self.click_control(str(stage["map_discipline_action"]))
        for row in stage["disciplines"]:
            self.page.locator(str(stage["discipline_selector"])).select_option(
                str(row["discipline"])
            )
            self.page.locator(str(stage["faculty_selector"])).select_option(
                str(row["faculty"])
            )
            self.click_guarded(str(stage["add_discipline_button"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
        self.click_control(str(stage["back_selector"]))

    def map_areas_of_research(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["map_area_link"]))
        for area in stage["areas"]:
            self.execute_actions(area["actions"])
            research_name = str(area.get("research_name", "")).strip()
            if research_name:
                self.fill_field(
                    str(stage["research_name_field"]), research_name
                )
            self.fill_field(
                str(stage["research_short_name_field"]), str(area["research_short_name"])
            )
            self.click_guarded(str(stage["add_selector"]))
            self.click_guarded(str(stage["submit_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def map_evaluation_system(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["map_evaluation_button"]))
        self.execute_actions(stage["actions"])
        self.click_guarded(str(stage["add_button"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
