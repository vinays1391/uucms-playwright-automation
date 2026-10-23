"""University Admin: Course Design/Structure — add new course/paper
details with offering department, credit and evaluation components.
Selectors and values come from test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CourseDesignPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def add_courses(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["add_course_button"]))
        for course in stage["courses"]:
            trigger = self.page.locator(str(stage["department_trigger_selector"]))
            trigger.first.click()
            search = self.page.locator(str(stage["department_search_selector"]))
            search.first.fill(str(course["department_search_term"]))
            option = self.page.get_by_role("option", name=str(course["department_option"]))
            option.first.wait_for(state="visible")
            option.first.click()
            self.execute_actions(course["fields"])
            self.click_control(str(stage["basic_add_selector"]))
        self.execute_actions(stage["credit_fields"])
        self.click_control(str(stage["credit_add_selector"]))
        self.click_control(str(stage["next_selector"]))
        for component in stage["evaluation_components"]:
            self.execute_actions(component["fields"])
            self.click_control(str(stage["evaluation_add_selector"]))
        self.click_control(str(stage["next_selector"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
