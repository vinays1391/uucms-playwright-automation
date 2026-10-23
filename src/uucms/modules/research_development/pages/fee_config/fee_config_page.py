"""R&D > Fee Configuration > Research and Development related Fees screens.

University Admin maintains the R&D fee list per program, request type,
academic year, category, gender and income limit. Fees can be revised
with a Committee Order number/document, viewed read-only, cancelled or
reset. Every selector comes from the test-data file (see
test_data/rnd/fee_config.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import FEE_CONFIGURATION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class FeeConfigPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(FEE_CONFIGURATION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def open_add_new_fee(self, add_action: str) -> None:
        self.click_control(add_action)

    def fill_fee_form(self, actions: Sequence[dict]) -> None:
        """Fill the fee header (program, discipline, AOR, request type,
        academic year) and fee rows (category, gender, income limit,
        amount) via test-data actions."""
        self.execute_actions(list(actions))

    def save_fee(self, actions: Sequence[dict], save_selector: str,
                 success_selector: str | None = None) -> None:
        self.fill_fee_form(actions)
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def attempt_save_fee(self, actions: Sequence[dict], save_selector: str,
                         message: str) -> None:
        """Save with a validation error (e.g. Amount left blank)."""
        self.fill_fee_form(actions)
        self.submit_expect_validation(save_selector, message)

    def cancel_fee_entry(self, cancel_selector: str) -> None:
        """Cancel discards the fee entry; the caller re-checks the list."""
        self.click_control(cancel_selector)

    def open_fee(self, row_selector: str, action_selector: str) -> None:
        """Open a fee row for revision or read-only viewing."""
        self.open_row_action(row_selector, action_selector)

    def revise_fee(self, row_selector: str, action_selector: str,
                   actions: Sequence[dict], save_selector: str,
                   success_selector: str | None = None) -> None:
        """Revise amount, enter Committee Order No and upload the order document."""
        self.open_fee(row_selector, action_selector)
        self.fill_fee_form(actions)
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def reset_fee(self, row_selector: str, reset_selector: str,
                  confirm_selector: str,
                  success_selector: str | None = None) -> None:
        """Reset restores the previous fee configuration."""
        self.open_row_action(row_selector, reset_selector)
        self.click_guarded(confirm_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def expect_view_read_only(self, save_selector: str, cancel_selector: str) -> None:
        """The View screen offers no Save/Cancel actions."""
        expect(self.page.locator(save_selector)).to_have_count(0)
        expect(self.page.locator(cancel_selector)).to_have_count(0)

    def expect_fee_sections(self, sections: Sequence[str]) -> None:
        for section in sections:
            expect(self.page.get_by_text(section, exact=True)).to_be_visible()
