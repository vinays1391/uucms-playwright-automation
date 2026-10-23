"""Research And Development > Research Projects > Submissions list
screen (Department Chairperson).

Progress Report Submissions for research project members: filter by
Area of Research and Research Project ID & Name, export the DataTable
(Excel/PDF/Print) and open the row action "View Details", which shows
the modal #reviewModalContainer titled
"View Research Progress Report - <Progress Report ID>" with the
Current Submission Details. Every selector comes from the test-data
file (see test_data/rnd/research_projects.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import RESEARCH_PROJECTS_SUBMISSIONS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ProjectSubmissionsPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(RESEARCH_PROJECTS_SUBMISSIONS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def expect_screen(self, heading: str, breadcrumb: Sequence[str],
                      aor_filter: str, project_filter: str,
                      view_button: str, export_buttons: Sequence[str]) -> None:
        """Assert the screen structure: heading, breadcrumb, filters, exports."""
        expect(self.page.get_by_text(heading, exact=True)).to_be_visible()
        for crumb in breadcrumb:
            expect(self.page.get_by_text(str(crumb), exact=True)).to_be_visible()
        for control in (aor_filter, project_filter, view_button):
            expect(self.page.locator(control)).to_be_visible()
        for button in export_buttons:
            expect(self.page.get_by_text(str(button), exact=True)).to_be_visible()

    def view_submissions(self, filters: Sequence[dict], view_button: str) -> None:
        """Filter by Area of Research / project and click View."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def row_count(self, row_selector: str) -> int:
        return self.page.locator(row_selector).count()

    def view_report_details(self, row_selector: str, view_action: str) -> None:
        """Open the View Details modal for a submission row."""
        self.open_row_action(row_selector, view_action)

    def expect_review_modal(self, modal_selector: str, title: str,
                            field_labels: Sequence[str], section_title: str,
                            detail_labels: Sequence[str]) -> None:
        """Assert the modal title and the Current Submission Details fields."""
        modal = self.page.locator(modal_selector)
        modal.first.wait_for(state="visible")
        expect(modal).to_contain_text(title)
        for label in [*field_labels, section_title, *detail_labels]:
            expect(modal.get_by_text(str(label), exact=True)).to_be_visible()

    def close_modal(self, close_selector: str, modal_selector: str) -> None:
        """Close the modal and assert it is no longer visible."""
        self.click_control(close_selector)
        expect(self.page.locator(modal_selector)).not_to_be_visible()
