"""Research And Development > Research Projects > Progress Completion
screen (Department Chairperson).

Member Progress Completion Marking: select the Area of Research
(#ddlAreaOfResearch) and the cascaded project (#ddlProject), click
View Project Members, review the PI-approved project member progress
records (empty state when none exist) and tick the Select checkboxes to
mark the chosen members as completion. Every selector comes from the
test-data file (see test_data/rnd/research_projects.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import RESEARCH_PROJECTS_PROGRESS_COMPLETION
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ProjectProgressCompletionPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(RESEARCH_PROJECTS_PROGRESS_COMPLETION)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def expect_screen(self, heading: str, breadcrumb: Sequence[str],
                      area_select: str, project_select: str,
                      view_members_button: str, back_link: str) -> None:
        """Assert the screen structure: heading, breadcrumb, selects, buttons."""
        expect(self.page.get_by_text(heading, exact=True)).to_be_visible()
        for crumb in breadcrumb:
            expect(self.page.get_by_text(str(crumb), exact=True)).to_be_visible()
        for control in (area_select, project_select, view_members_button, back_link):
            expect(self.page.locator(control)).to_be_visible()

    def view_project_members(self, filters: Sequence[dict],
                             view_members_button: str) -> None:
        """Select Area of Research / project and click View Project Members."""
        self.execute_actions(list(filters))
        self.click_control(view_members_button)

    def row_count(self, row_selector: str) -> int:
        return self.page.locator(row_selector).count()

    def expect_empty_state(self, empty_text: str) -> None:
        """Assert the documented empty-state text for a project without
        PI-approved member progress records."""
        expect(self.page.get_by_text(empty_text, exact=True)).to_be_visible()

    def expect_members_or_empty(self, empty_text: str,
                                row_selector: str | None = None) -> None:
        """Empty table shows the documented empty state; otherwise at
        least one member row is listed."""
        empty = self.page.get_by_text(empty_text, exact=True)
        if empty.count() > 0:
            expect(empty.first).to_be_visible()
            return
        if row_selector:
            expect(self.page.locator(row_selector).first).to_be_visible()

    def mark_completion(self, checkboxes: Sequence[str], mark_button: str,
                        success_selector: str | None = None) -> None:
        """Tick the member Select checkboxes and mark them as completion."""
        for checkbox in checkboxes:
            control = self.page.locator(checkbox)
            control.first.wait_for(state="visible")
            control.first.check()
        self.submit(mark_button)
        if success_selector:
            expect(self.page.locator(success_selector)).to_be_visible()
