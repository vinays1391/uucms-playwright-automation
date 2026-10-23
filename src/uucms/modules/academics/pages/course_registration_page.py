"""Coursework: student course registration screen.

Select the registration scheme, choose the courses for the term and
submit. Selectors and values come from
test_data/academics/coursework_examination.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CourseRegistrationPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def select_scheme(self, stage: Mapping[str, object]) -> None:
        self.page.locator(str(stage["scheme_selector"])).select_option(
            str(stage["scheme_value"])
        )
        self.submit(str(stage["save_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))

    def register_courses(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["course_list_selector"]))
        for selector in stage.get("row_action_clicks", []):
            self.click_control(str(selector))
        for course in stage["courses"]:
            row = self.page.locator(str(course["row_selector"]))
            row.first.wait_for(state="visible")
            row.locator(str(course["checkbox_selector"])).first.check()
        self.submit(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
