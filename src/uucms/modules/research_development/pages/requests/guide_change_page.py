"""R&D > Special Requests > Add New Request wizard (student side).

Covers the guide/co-guide allocation and change flows plus the other
request types (mode of study, maternity leave, extension of expected
end date, additional year of extension):

    Step 1: student details (read-only) + Request Type +
            Special Circumstance (special-circumstance types only) +
            Reason + Supporting Document  ->  Next
    Step 2: Choose Preferred Faculty (vacancy-matrix filtered)
    Step 3: Online Fee Details (Amount to be Paid, Pay Fees)

The approval route is Student -> Guide/Co-Guide -> Department
Chairperson -> Doctoral Committee (participants vary by request type).
Every selector comes from the test-data file (see
test_data/rnd/special_requests.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.core.data_driven_form_page import DataDrivenFormPage
from uucms.modules.research_development.pages.special_request.special_requests_page import SpecialRequestsPage


class GuideChangePage(DataDrivenFormPage):
    """Student-side Add New Request wizard."""

    def open_wizard(self, add_action: str) -> None:
        SpecialRequestsPage(self.page, self.page.default_timeout()).open_add_request(add_action)

    def expect_student_details(self, details: Sequence[str]) -> None:
        """Name, USN, program, discipline, AOR, term/year, existing guide."""
        SpecialRequestsPage(self.page, self.page.default_timeout()).expect_read_only_details(details)

    def choose_request_type(self, request_type_select: str, request_type: str) -> None:
        select = self.page.locator(request_type_select)
        select.first.wait_for(state="visible")
        select.first.select_option(label=request_type)

    def enter_request_details(self, actions: Sequence[dict]) -> None:
        """Fill request-specific fields (reason, dates, mode of study,
        projected year, ...) and upload the supporting document."""
        self.execute_actions(list(actions))

    def expect_special_circumstance_options(self, select_selector: str,
                                            options: Sequence[str]) -> None:
        """The Special Circumstance list loads only for the two
        special-circumstance request types."""
        SpecialRequestsPage(self.page, self.page.default_timeout()).expect_select_options(
            select_selector, options
        )

    def expect_special_circumstance_absent(self, select_selector: str) -> None:
        expect(self.page.locator(select_selector)).to_have_count(0)

    def proceed_next(self, next_selector: str) -> None:
        self.click_guarded(next_selector)

    def attempt_proceed_next(self, next_selector: str, message: str) -> None:
        """Next with a validation error (blank reason / request type, ...)."""
        self.submit_expect_validation(next_selector, message)

    def expect_preferred_faculty_columns(self, columns: Sequence[str]) -> None:
        SpecialRequestsPage(self.page, self.page.default_timeout()).expect_list_columns(columns)

    def expect_preferred_faculty(self, present: Sequence[str],
                                 absent: Sequence[str]) -> None:
        SpecialRequestsPage(self.page, self.page.default_timeout()).expect_rows_listed(
            present, absent
        )

    def collect_research_faculty_types(self, cell_selector: str) -> list[str]:
        return SpecialRequestsPage(self.page, self.page.default_timeout()).collect_cell_texts(cell_selector)

    def expect_no_offline_payment(self, offline_option_selector: str) -> None:
        """Only online fee payment is allowed; no offline/counter option."""
        expect(self.page.locator(offline_option_selector)).to_have_count(0)

    def expect_fee_amount(self, fee_amount_selector: str, amount: str) -> None:
        """The Amount to be Paid is loaded from the fee configuration."""
        fee = self.page.locator(fee_amount_selector)
        fee.first.wait_for(state="visible")
        expect(fee.first).to_contain_text(str(amount))

    def pay_fees(self, pay_selector: str, payment_actions: Sequence[dict] | None = None,
                 success_selector: str | None = None) -> None:
        """Complete the online payment (payment gateway steps from a recording)."""
        if payment_actions:
            self.execute_actions(list(payment_actions))
        self.click_guarded(pay_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
