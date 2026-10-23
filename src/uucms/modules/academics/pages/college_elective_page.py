"""College Admin: college curriculum — select electives for the Ph.D
program. Selectors and values come from test_data/academics/program_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CollegeElectivePage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def select_electives(self, stage: Mapping[str, object]) -> None:
        search = self.page.locator(str(stage["search_selector"]))
        search.first.wait_for(state="visible")
        search.first.fill(str(stage["search_term"]))
        action = self.page.get_by_role(
            "link", name=str(stage["select_electives_action"]), exact=True
        )
        index = int(stage.get("select_electives_action_index", 0))
        actual = min(index, max(action.count() - 1, 0)) if index else 0
        action.nth(actual).wait_for(state="visible")
        action.nth(actual).click()
        self.execute_actions(stage["fields"])
        self.page.locator(str(stage["elective_checkbox"])).first.check()
        self.execute_actions(stage.get("final_fields", []))
        self.click_guarded(str(stage["save_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
