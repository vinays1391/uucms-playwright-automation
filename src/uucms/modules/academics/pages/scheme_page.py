"""University Admin: Schemes & Course Types — create a new scheme and map
programs with course types to it. Selectors and values come from
test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class SchemePage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def add_scheme(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["add_scheme_button"]))
        self.fill_field(str(stage["scheme_name_field"]), str(stage["scheme_name"]))
        self.fill_field(str(stage["scheme_code_field"]), str(stage["scheme_code"]))
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["add_new_scheme_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def map_program_course_types(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["actions"])
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
