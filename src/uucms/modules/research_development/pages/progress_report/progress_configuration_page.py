"""R&D > Research Progress > Configuration > Research Progress
Submissions screen (Department Chairperson).

The Department Chairperson configures the scholar-wise progress-report
schedule: Submission From Date, Frequency of Submission (Weekly,
bi-weekly, Monthly, Bi-Monthly, three months, six months, Nine Months,
one year), No. of Days from start date, Total Number of Reports and
Projected Final Report Submission Date. Every selector comes from the
test-data file (see test_data/rnd/progress_report.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import PROGRESS_REPORT_CONFIGURATION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ProgressConfigurationPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(PROGRESS_REPORT_CONFIGURATION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def view_scholars(self, filters: Sequence[dict], view_button: str) -> None:
        """Select Academic Year/Cycle and click View List of Scholars."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def configure_scholar(self, row_selector: str, actions: Sequence[dict],
                          save_selector: str,
                          success_selector: str | None = None) -> None:
        """Configure the submission schedule for a scholar row and save."""
        self.find_row(row_selector)
        self.execute_actions(list(actions))
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()

    def edit_configuration(self, row_selector: str, edit_action: str,
                           actions: Sequence[dict], save_selector: str,
                           success_selector: str | None = None) -> None:
        """Edit an existing progress configuration and save."""
        self.open_row_action(row_selector, edit_action)
        self.execute_actions(list(actions))
        self.submit(save_selector)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
