"""University Admin: Curriculum (CBCS) — add a new curriculum for the
Ph.D scheme and validate it. Selectors and values come from
test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CurriculumPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def add_curriculum(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["fields"])
        for row in stage["rows"]:
            self.execute_actions(row["actions"])
            self.click_control(str(stage["add_temp_button"]))
        self.execute_actions(stage["program_actions"])
        self.click_control(str(stage["add_temp_programwise"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def validate_curriculum(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["view_curriculum_selector"]))
        self.click_control(str(stage["validate_action"]))
        self.page.locator(str(stage["term_field"])).select_option(str(stage["term_value"]))
        self.click_guarded(str(stage["view_selector"]))
        self.click_guarded(str(stage["validate_button"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
