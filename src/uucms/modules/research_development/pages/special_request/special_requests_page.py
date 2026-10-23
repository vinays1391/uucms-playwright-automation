"""R&D > Special Requests > Allocation/change request list screens.

The student views their own submitted requests; the Department
Chairperson and the Doctoral Committee Chairperson view the list of
Students/PhD Scholars. The Add New Request wizard itself is driven by
GuideChangePage. Every selector comes from the test-data file (see
test_data/rnd/special_requests.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import SPECIAL_REQUESTS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class SpecialRequestsPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(SPECIAL_REQUESTS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def open_add_request(self, add_action: str) -> None:
        """Click the Add New Request action on the list screen."""
        self.click_control(add_action)

    def view_my_requests(self, filters: Sequence[dict], view_button: str) -> None:
        """Student: select Academic Year and click View my requests."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def view_students_list(self, filters: Sequence[dict], view_button: str) -> None:
        """Department Chairperson / DCC: View List of Students/PhD Scholars."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def open_request_details(self, row_selector: str, view_action: str) -> None:
        self.open_row_action(row_selector, view_action)

    def release_request(self, row_selector: str, release_action: str,
                        confirm_selector: str | None = None) -> None:
        """Cancel/release a submitted request (releases the locked seat)."""
        self.open_row_action(row_selector, release_action)
        if confirm_selector:
            self.click_guarded(confirm_selector)

    def expect_request_status(self, row_selector: str, status: str) -> None:
        self.find_row(row_selector)
        expect(self.page.locator(row_selector).first).to_contain_text(status)

    def expect_request_types(self, request_type_select: str,
                             present: Sequence[str],
                             absent: Sequence[str]) -> None:
        """Assert which request types the dropdown offers to this student."""
        select = self.page.locator(request_type_select)
        select.first.wait_for(state="visible")
        for label in present:
            expect(select.get_by_text(str(label), exact=True)).to_be_visible()
        for label in absent:
            expect(select.get_by_text(str(label), exact=True)).to_have_count(0)

    def expect_field_visible(self, field_selector: str, text: str | None = None) -> None:
        field = self.page.locator(field_selector)
        field.first.wait_for(state="visible")
        if text:
            expect(field.first).to_contain_text(text)

    def expect_field_absent(self, field_selector: str) -> None:
        expect(self.page.locator(field_selector)).to_have_count(0)

    def expect_read_only_details(self, details: Sequence[str]) -> None:
        """Student details displayed read-only on the wizard first step."""
        for detail in details:
            expect(self.page.get_by_text(str(detail), exact=True)).to_be_visible()
