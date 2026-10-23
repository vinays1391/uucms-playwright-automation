"""R&D > Symposium > Invitation for Final Viva Voce, Colloquium or
Symposium (Scholar).

The scholar sees the invited event with its Status (Scheduled, Yet to
Upload Details, Approved) and read-only details: student information,
panel of examiners, research title, event type, date & time, duration,
venue/online link, conduction mode and the uploaded media/supporting
documents (View/Download). Every selector comes from the test-data
file (see test_data/rnd/symposium.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import SYMPOSIUM_SCHOLAR_INVITATION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class SymposiumScholarInvitationPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(SYMPOSIUM_SCHOLAR_INVITATION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def expect_status(self, row_selector: str, status: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(status)

    def open_details(self, row_selector: str, view_action: str) -> None:
        self.open_row_action(row_selector, view_action)

    def expect_read_only_details(self, fields: Sequence[str]) -> None:
        for field in fields:
            expect(self.page.get_by_text(field, exact=True)).to_be_visible()

    def expect_documents_available(self, view_selector: str,
                                   download_selector: str) -> None:
        expect(self.page.locator(view_selector)).to_be_visible()
        expect(self.page.locator(download_selector)).to_be_visible()
