"""R&D Ph.D admission: online fee payment invitation and offline payment approval.

The student must be mapped to an Area of Research with the Guide/Co-Guide
mapped under it before the online fee payment invitation can be sent and
before an offline payment can be approved. Screen and action selectors
come from the test-data file.
"""

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import (
    OFFLINE_PAYMENT_APPROVAL,
    ONLINE_FEE_PAYMENT,
)
from uucms.modules.common.menu_page import MenuPage
from uucms.core.data_driven_form_page import DataDrivenFormPage


class FeePaymentPage(DataDrivenFormPage):
    def open_online_fee_invitation(self) -> None:
        MenuPage(self.page, self.page.default_timeout()).open_menu(ONLINE_FEE_PAYMENT)

    def open_offline_payment_approval(self) -> None:
        MenuPage(self.page, self.page.default_timeout()).open_menu(OFFLINE_PAYMENT_APPROVAL)

    def open_student_screen(self, row_selector: str, action_selector: str) -> None:
        """Open the fee invitation / offline payment screen for a student row."""
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        action = self.page.locator(action_selector)
        action.first.wait_for(state="visible")
        action.first.click()

    def send_invitation(self, send_selector: str, success_selector: str) -> None:
        self.click_guarded(send_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def expect_invitation_blocked(self, send_selector: str, message: str) -> None:
        self.submit_expect_validation(send_selector, message)

    def expect_payment_approval_blocked(self, approve_selector: str, message: str) -> None:
        self.submit_expect_validation(approve_selector, message)

    def expect_row_text(self, row_selector: str, text: str) -> None:
        row = self.page.locator(row_selector)
        row.first.wait_for(state="visible")
        expect(row.first).to_contain_text(text)
