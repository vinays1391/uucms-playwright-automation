"""R&D > PhD Scholars > Convocation Eligibility > PhD Scholars –
Eligible for Convocation (Registrar (Evaluation)).

Only scholars whose Final Viva Voce, Colloquium or Symposium is
Approved are listed. The Registrar (Evaluation) marks scholars as
eligible (multi-select) and submits; after the convocation notification
is configured and the scholar has paid the applicable Indian/Foreign
fee, the scholar appears in the Convocation eligibility list. PDC and
degree/convocation certificate printing are supported from this area.
Every selector comes from the test-data file (see
test_data/rnd/convocation.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import CONVOCATION_ELIGIBILITY
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ConvocationEligibilityPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(CONVOCATION_ELIGIBILITY)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def view_scholars(self, filters: Sequence[dict], view_button: str) -> None:
        """Select Academic Year/Cycle and click View List of Scholars."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def expect_scholars_listed(self, present: Sequence[str], absent: Sequence[str]) -> None:
        self.expect_rows_listed(present, absent)

    def mark_eligible(self, check_selectors: Sequence[str], submit_selector: str,
                      success_selector: str | None = None) -> None:
        """Tick the Mark as eligible checkboxes (multi-select) and submit."""
        for check_selector in check_selectors:
            check = self.page.locator(check_selector)
            check.first.wait_for(state="visible")
            check.first.check()
        self.click_guarded(submit_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def open_scholar_details(self, row_selector: str, view_action: str) -> None:
        self.open_row_action(row_selector, view_action)

    def expect_eligibility_details(self, fields: Sequence[str]) -> None:
        for field in fields:
            expect(self.page.get_by_text(field, exact=True)).to_be_visible()

    def print_pdc(self, row_selector: str, pdc_action: str,
                  success_selector: str | None = None) -> None:
        """Print the Provisional Degree Certificate for the scholar."""
        self.open_row_action(row_selector, pdc_action)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def issue_degree_certificate(self, row_selector: str, issue_action: str,
                                 print_action: str | None = None,
                                 success_selector: str | None = None) -> None:
        """Issue (and print) the degree/convocation certificate."""
        self.open_row_action(row_selector, issue_action)
        if print_action:
            self.click_control(print_action)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
