"""Academics > Areas of Research > Area of Research Mapping to Faculty
and Student: University Admin maps Areas of Research to faculty, views
the mapped areas and modifies (deletes) mappings. Selectors and values
come from test_data/rnd/phd_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class AorFacultyMappingPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str],
                       list_item_selector: str | None = None) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()
        if list_item_selector:
            list_item = self.page.locator(list_item_selector)
            list_item.first.wait_for(state="visible")
            list_item.first.click()

    def select_program(self, filters: Sequence[Mapping[str, object]],
                       view_selector: str) -> None:
        self.execute_actions(list(filters))
        self.click_guarded(view_selector)

    def open_program_row(self, cell_selector: str) -> None:
        self.click_control(cell_selector)

    def open_row_action(self, action_text: str, action_index: int = 0) -> None:
        action = self.page.get_by_text(action_text)
        index = min(action_index, max(action.count() - 1, 0)) if action_index else 0
        action.nth(index).wait_for(state="visible")
        action.nth(index).click()

    def map_areas(self, stage: Mapping[str, object]) -> None:
        self.open_row_action(
            str(stage["map_action"]), int(stage.get("map_action_index", 0))
        )
        self.execute_actions(stage["fields"])
        self.click_guarded(str(stage["add_selector"]))
        self.click_guarded(str(stage["submit_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
        back = stage.get("back_selector")
        if back:
            self.click_control(str(back))

    def view_mapped_areas(self, stage: Mapping[str, object]) -> None:
        self.open_row_action(
            str(stage["view_action"]), int(stage.get("view_action_index", 0))
        )
        self.execute_actions(stage["actions"])
        self.click_guarded(str(stage["view_button"]))
        self.expect_saved(str(stage["success_selector"]))
        self.click_control(str(stage["back_selector"]))

    def modify_and_delete(self, stage: Mapping[str, object]) -> None:
        self.open_row_action(
            str(stage["modify_action"]), int(stage.get("modify_action_index", 0))
        )
        self.execute_actions(stage["actions"])
        self.click_guarded(str(stage["view_button"]))
        self.click_guarded(str(stage["delete_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
        self.click_control(str(stage["back_selector"]))
