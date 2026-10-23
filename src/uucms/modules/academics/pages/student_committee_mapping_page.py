"""Academics > Areas of Research > Area of Research Mapping to: Map
Student to Committee screen (University Admin). Selectors and values
come from test_data/rnd/phd_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class StudentCommitteeMappingPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def select_program(self, filters: Sequence[Mapping[str, object]],
                       view_selector: str) -> None:
        self.execute_actions(list(filters))
        self.click_guarded(view_selector)

    def map_student_to_committee(self, stage: Mapping[str, object]) -> None:
        action = self.page.get_by_text(str(stage["map_student_action"]))
        index = int(stage.get("map_student_action_index", 0))
        actual = min(index, max(action.count() - 1, 0)) if index else 0
        action.nth(actual).wait_for(state="visible")
        action.nth(actual).click()
        self.execute_actions(stage["fields"])
        self.select_student(
            str(stage["student_select_selector"]), str(stage["student_option"])
        )
        self.execute_actions(stage["committee_fields"])
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def select_student(self, select_selector: str, option_name: str) -> None:
        self.page.locator(select_selector).first.click()
        option = self.page.get_by_role("option", name=option_name)
        option.first.wait_for(state="visible")
        option.first.click()
