"""Research And Development > Research Projects > Submission
Configuration screen (Department Chairperson).

The PI/Mentor configures the member-wise progress-report schedule for a
research project: pick the Area of Research (#ddlAreaOfResearch), the
cascaded project (#ddlProject) and click View. The screen then shows the
"Research Project Information" card (Project ID, Project Name, Project
Type, Funding Type, Funding Agency, Estimated Cost, Project Status,
Project Objective) and the member table (Submission from date, Frequency
of submission, Days allowed for submission, Total reports, Projected
Final Report Submission Date) with a per-row Edit action. Every selector
comes from the test-data file (see
test_data/rnd/research_projects.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import RESEARCH_PROJECTS_SUBMISSION_CONFIGURATION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ProjectSubmissionConfigPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(RESEARCH_PROJECTS_SUBMISSION_CONFIGURATION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def expect_screen(self, heading: str, breadcrumb: Sequence[str],
                      area_select: str, project_select: str,
                      view_button: str, back_link: str) -> None:
        """Assert the screen structure: heading, breadcrumb, selects, View, Back."""
        expect(self.page.get_by_text(heading, exact=True)).to_be_visible()
        for crumb in breadcrumb:
            expect(self.page.get_by_text(str(crumb), exact=True)).to_be_visible()
        for control in (area_select, project_select, view_button, back_link):
            expect(self.page.locator(control)).to_be_visible()

    def select_project(self, filters: Sequence[dict]) -> None:
        """Select the Area of Research and the cascaded project."""
        self.execute_actions(list(filters))

    def view_project(self, filters: Sequence[dict], view_button: str) -> None:
        """Select Area of Research / project and click View."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def expect_project_info(self, labels: Sequence[str]) -> None:
        """Assert the 'Research Project Information' card fields."""
        for label in labels:
            expect(self.page.get_by_text(str(label), exact=True)).to_be_visible()

    def row_count(self, row_selector: str) -> int:
        return self.page.locator(row_selector).count()

    def configure_member(self, row_selector: str, actions: Sequence[dict],
                         save_selector: str,
                         success_selector: str | None = None) -> None:
        """Fill the member row's schedule fields inline and save."""
        self.find_row(row_selector)
        self.execute_actions(list(actions))
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def edit_configuration(self, row_selector: str, edit_action: str,
                           actions: Sequence[dict], save_selector: str,
                           success_selector: str | None = None) -> None:
        """Open the row's Edit action, update the schedule and save."""
        self.open_row_action(row_selector, edit_action)
        self.execute_actions(list(actions))
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
