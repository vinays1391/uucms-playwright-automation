"""Exam module screen for permitting students to take an examination."""

from collections.abc import Mapping, Sequence

from uucms.core.data_driven_form_page import DataDrivenFormPage


class PermitStudentsPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def permit_students(self, stage: Mapping[str, object]) -> None:
        self.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.apply_filters(stage["filters"])
        declaration = stage.get("declaration_checkbox")
        if declaration:
            self.page.locator(str(declaration)).first.check()
        self.submit(str(stage["submit_selector"]))
        self.click_guarded(str(stage["confirm_selector"]))
        self.expect_saved(str(stage["success_selector"]))
