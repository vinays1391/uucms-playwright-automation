"""Exam module screen for a Principal to view hall tickets and eligibility."""

from collections.abc import Mapping, Sequence

from uucms.core.data_driven_form_page import DataDrivenFormPage


class HallTicketPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str], menu_index: int = 0) -> None:
        for item in menu_path:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()

    def view_hall_tickets(self, stage: Mapping[str, object]) -> None:
        self.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.execute_actions(list(stage["filters"]))
        self.click_guarded(str(stage["view_details_selector"]))
        self.click_guarded(str(stage["check_eligibility_selector"]))
        self.expect_saved(str(stage["success_selector"]))
