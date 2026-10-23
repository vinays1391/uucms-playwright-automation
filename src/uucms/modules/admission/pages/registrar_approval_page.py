"""Registrar (Admin) Ph.D request approval screen."""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class RegistrarApprovalPage(DataDrivenFormPage):
    def open_request(self, stage: Mapping[str, object]) -> None:
        menu_index = int(stage.get("menu_index", 0))
        for item in stage["menu_path"]:
            links = self.page.get_by_role("link", name=item, exact=True)
            index = min(menu_index, max(links.count() - 1, 0)) if menu_index else 0
            links.nth(index).wait_for(state="visible")
            links.nth(index).click()
        filters = stage.get("filters")
        if filters:
            self.execute_actions(list(filters))
        view_selector = stage.get("view_student_details_selector")
        if view_selector:
            self.click_guarded(
                self.row_scoped_selector(str(view_selector), stage.get("row_text"))
            )
        request_row = stage.get("request_row")
        if request_row:
            row = self.page.locator(str(request_row))
            row.first.wait_for(state="visible")

    def approve_or_reject(self, stage: Mapping[str, object]) -> None:
        action = str(stage.get("action", "approve")).strip().casefold()
        if action == "approve":
            self.click_guarded(str(stage["approve_selector"]))
        elif action == "reject":
            self.click_guarded(str(stage["reject_selector"]))
        else:
            raise ValueError(
                f"Unsupported registrar action {action!r}; expected 'approve' or 'reject'"
            )
        remarks_field = stage.get("remarks_field")
        if remarks_field:
            self.fill_field(str(remarks_field), str(stage.get("remarks_value", "")))
        submit_selector = stage.get("submit_selector")
        if submit_selector:
            self.submit(str(submit_selector))
        self.wait_loader_gone()
        for confirm in stage.get("confirms", []):
            self.click_guarded(str(confirm))
        self.expect_saved(str(stage["success_selector"]))
