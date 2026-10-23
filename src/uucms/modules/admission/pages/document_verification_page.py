"""Ph.D admission: Verify Document screen.

Preview the invited student's application, review each uploaded document,
set the verification date, map the Ph.D details (discipline, area of
research, guide, category, quota, research student type) and submit.
Selectors and values come from test_data/admission/phd_admission.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class DocumentVerificationPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def apply_filters(self, filters: Sequence[Mapping[str, object]]) -> None:
        self.execute_actions(list(filters))

    def verify_documents(self, stage: Mapping[str, object]) -> None:
        row_text = str(stage.get("row_text", "")).strip()
        if row_text:
            escaped = row_text.replace('"', '\\"')
            row = self.page.locator(f'tr:has-text("{escaped}")')
        else:
            row = self.page.locator(str(stage["preview_row_selector"]))
        row.first.wait_for(state="visible")
        row.locator(str(stage["preview_button"])).first.click()
        ok_selector = str(stage["document_ok_selector"])
        for document in stage["documents"]:
            self.click_guarded(str(document))
            self.click_guarded(ok_selector)
        date_field = self.page.get_by_role("textbox", name="Click to Select Date")
        date_field.first.wait_for(state="visible")
        date_field.first.click()
        day = self.page.get_by_role(
            "link", name=str(stage["verification_date_day"]), exact=True
        )
        day.first.wait_for(state="visible")
        day.first.click()
        self.execute_actions(stage["phd_mapping"])
        self.submit(str(stage["submit_selector"]))
        self.wait_loader_gone()
        self.expect_saved(str(stage["success_selector"]))
