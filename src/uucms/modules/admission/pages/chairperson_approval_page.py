"""Department Chairperson Ph.D candidate review and approval screen."""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class ChairpersonApprovalPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def view_student_details(self, selector: str, row_text: str | None = None) -> None:
        self.click_guarded(self.row_scoped_selector(selector, row_text))

    def review_and_approve(self, stage: Mapping[str, object]) -> None:
        row_text = str(stage.get("row_text", "")).strip() or None
        for _ in range(int(stage.get("approval_cycles", 1))):
            self.click_guarded(str(stage["review_action_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["approve_selector"]))
            self.click_guarded(str(stage["confirm_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
            self.apply_filters(stage["filters"])
            self.view_student_details(
                str(stage["view_student_details_selector"]), row_text
            )
