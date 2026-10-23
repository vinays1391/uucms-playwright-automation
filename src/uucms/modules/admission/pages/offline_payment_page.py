"""Candidate offline admission payment screen."""

from collections.abc import Mapping

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class OfflinePaymentPage(DataDrivenFormPage):
    def open_from_menu(self, entry_selector: str, entry_text: str) -> None:
        entry = self.page.locator(entry_selector).get_by_text(entry_text)
        entry.first.wait_for(state="visible")
        entry.first.click()

    def submit_payment(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["view_application_button"]))
        self.click_control(str(stage["offline_payment_link"]))
        self.fill_field(str(stage["challan_field"]), str(stage["challan_value"]))
        self.fill_field(str(stage["amount_field"]), str(stage["amount_value"]))
        payment_day = self.page.get_by_role(
            "link", name=str(stage["payment_date_day"]), exact=True
        )
        payment_day.first.wait_for(state="visible")
        payment_day.first.click()
        self.upload_file(
            str(stage["receipt_upload_selector"]), str(stage["receipt_file"])
        )
        self.submit(str(stage["submit_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))

    def submit_payment_for_application_row(self, stage: Mapping[str, object]) -> None:
        self.click_guarded(str(stage["view_application_button"]))
        self.click_control(str(stage["application_row_action"]))
        self.click_control(str(stage["offline_payment_control"]))
        self.fill_field(str(stage["challan_field"]), str(stage["challan_value"]))
        self.fill_field(str(stage["amount_field"]), str(stage["amount_value"]))
        payment_day = self.page.get_by_role(
            "link", name=str(stage["payment_date_day"]), exact=True
        )
        payment_day.first.wait_for(state="visible")
        payment_day.first.click()
        self.upload_file(
            str(stage["receipt_upload_selector"]), str(stage["receipt_file"])
        )
        self.submit(str(stage["submit_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        resubmit = stage.get("resubmit")
        if resubmit:
            self.fill_field(str(stage["amount_field"]), str(resubmit["amount_value"]))
            self.submit(str(stage["submit_selector"]))
            self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
