"""Research And Development > Research Projects > Research Projects
Details screen (Department Chairperson).

The list screen ("Research Project" heading) filters the research
projects by the Area of Research multi-select and offers the
"Create a New Research Project" link. The create form (breadcrumb
"Home / Create Research Project") captures the project ID/name,
objective, project type (Internal/External), funding type
(Funding/Non-Funding), funding agency, estimated cost/duration,
remarks and the two proposal documents. For an Internal project the
external funding-agency list is not loaded. Every selector comes from
the test-data file (see test_data/rnd/research_projects.example.json).
"""

from collections.abc import Sequence

from playwright.sync_api import expect

from uucms.constants.menu_paths.research_development import RESEARCH_PROJECTS_DETAILS
from uucms.modules.common.menu_page import MenuPage
from uucms.core.list_screen_page import ListScreenPage


class ResearchProjectsDetailsPage(ListScreenPage):
    def open_from_menu(self, menu_path: Sequence[str] | None = None) -> None:
        path = list(menu_path) if menu_path else list(RESEARCH_PROJECTS_DETAILS)
        MenuPage(self.page, self.page.default_timeout()).open_menu(path)

    def expect_list_screen(self, heading: str, create_link: str, view_button: str) -> None:
        """Assert the list screen structure: heading, create link, View."""
        expect(self.page.get_by_text(heading, exact=True)).to_be_visible()
        for control in (create_link, view_button):
            expect(self.page.locator(control)).to_be_visible()

    def view_projects(self, filters: Sequence[dict], view_button: str) -> None:
        """Filter by Area of Research and list the matching projects."""
        self.execute_actions(list(filters))
        self.click_control(view_button)

    def open_create_form(self, create_link: str) -> None:
        """Open the Create Research Project form from the list screen."""
        self.click_control(create_link)

    def expect_create_form(self, heading: str, breadcrumb: Sequence[str],
                           field_labels: Sequence[str], field_selectors: Sequence[str],
                           upload_hint: str, submit_selector: str, back_selector: str) -> None:
        """Smoke-check the Create Research Project form structure."""
        expect(self.page.get_by_text(heading, exact=True)).to_be_visible()
        for crumb in breadcrumb:
            expect(self.page.get_by_text(str(crumb), exact=True)).to_be_visible()
        for label in field_labels:
            expect(self.page.get_by_text(str(label), exact=True)).to_be_visible()
        for selector in field_selectors:
            expect(self.page.locator(str(selector))).to_be_visible()
        expect(self.page.get_by_text(upload_hint)).not_to_have_count(0)
        expect(self.page.locator(submit_selector)).to_be_visible()
        expect(self.page.locator(back_selector)).to_be_visible()

    def fill_create_form(self, actions: Sequence[dict]) -> None:
        """Fill the create form from the data-driven action list."""
        self.execute_actions(list(actions))

    def submit_project(self, submit_selector: str, success_selector: str) -> None:
        """Submit the create form and assert the success element."""
        self.submit(submit_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def expect_funding_agency_not_loaded(self, funding_agency_select: str) -> None:
        """An Internal project must not offer external funding agencies."""
        select = self.page.locator(funding_agency_select)
        if select.count() == 0 or not select.first.is_visible():
            return  # the control itself is not loaded
        options = [
            option for option in self.collect_select_options(funding_agency_select)
            if option.strip()
        ]
        assert not options, (
            f"Funding agency options loaded for an Internal project: {options}"
        )
