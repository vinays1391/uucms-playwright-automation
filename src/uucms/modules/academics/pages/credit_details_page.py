"""University Admin: Credit Details — term/semester credits (with program
freeze) and course-type credits (with validation). Selectors and values
come from test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CreditDetailsPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def add_term_credits(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["add_term_credit_button"]))
        self.execute_actions(stage["fields"])
        self.fill_field(str(stage["min_credit_field"]), str(stage["min_credit"]))
        self.fill_field(str(stage["max_credit_field"]), str(stage["max_credit"]))
        self.click_control(str(stage["row_add_selector"]))
        self.execute_actions(stage["program_actions"])
        self.click_control(str(stage["add_temp_programwise"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def freeze_program(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["view_selector"]))
        for click in stage["freeze_clicks"]:
            self.click_control(str(click))
            self.click_guarded(str(stage["confirm_selector"]))
            self.wait_loader_gone()
        self.expect_saved(str(stage["success_selector"]))

    def add_course_type_credits(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["fields"])
        for course_type in stage["course_types"]:
            self.execute_actions(course_type["actions"])
            credit = course_type.get("credit")
            if credit is not None:
                self.fill_field(str(stage["credit_field"]), str(credit))
            self.click_control(str(stage["row_add_selector"]))
        self.execute_actions(stage["program_actions"])
        self.click_control(str(stage["add_temp_programwise"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def validate_credits(self, stage: Mapping[str, object]) -> None:
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["view_selector"]))
        action = self.page.get_by_text(str(stage["validate_action"]))
        index = int(stage.get("validate_action_index", 0))
        actual = min(index, max(action.count() - 1, 0)) if index else 0
        action.nth(actual).wait_for(state="visible")
        action.nth(actual).click()
        self.page.locator(str(stage["term_field"])).select_option(str(stage["term_value"]))
        self.click_guarded(str(stage["view_selector"]))
        self.click_guarded(str(stage["validate_button"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
