"""State Admin: statewise Program Details and discipline/subject
combination setup for a new Ph.D program. Selectors and values come from
test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class StateProgramPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def create_program_details(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["add_program_button"]))
        self.execute_actions(stage["program_actions"])
        upload_selector = stage.get("go_upload_selector")
        if upload_selector:
            self.upload_file(str(upload_selector), str(stage["go_upload_file"]))
        self.click_guarded(str(stage["add_new_program_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["program_success_selector"]))

    def add_discipline_combination(self, stage: Mapping[str, object]) -> None:
        search = self.page.locator(str(stage["search_selector"]))
        search.first.fill(str(stage["search_term"]))
        links = self.page.get_by_role(
            "link", name=str(stage["add_combination_link"]), exact=True
        )
        index = int(stage.get("add_combination_link_index", 0))
        actual = min(index, max(links.count() - 1, 0)) if index else 0
        links.nth(actual).wait_for(state="visible")
        links.nth(actual).click()
        self.execute_actions(
            stage.get("type_actions", [{"type": "select_value",
                                        "selector": "#SubjectTypeNameList",
                                        "value": "1"}])
        )
        self.page.locator(str(stage["subject_trigger_selector"])).first.click()
        for subject in stage["subject_searches"]:
            self.pick_subject(str(subject["search_selector"]),
                              str(subject["search_term"]))
            self.page.get_by_role("option", name=str(subject["option"])).first.click()
        self.execute_actions(stage["combination_actions"])
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["combination_success_selector"]))

    def pick_subject(self, search_selector: str, search_term: str) -> None:
        search = self.page.locator(search_selector)
        search.first.fill(search_term)
