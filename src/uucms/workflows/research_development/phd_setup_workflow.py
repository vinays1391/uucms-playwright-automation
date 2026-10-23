"""University Admin Ph.D setup workflow (R&D lifecycle, Academics screens).

Flow: map an Area of Research to the Ph.D program (Program Details), map
Areas of Research to faculty and review/modify the mapping (Areas of
Research), map a student to a committee, and create the committee
(Research And Development > Set-up). Screen page objects live in the
academics module because the screens are under the Academics menu.
Stage data comes from test_data/rnd/phd_setup.json.
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.academics.pages.aor_faculty_mapping_page import (
    AorFacultyMappingPage,
)
from uucms.modules.academics.pages.committee_setup_page import CommitteeSetupPage
from uucms.modules.academics.pages.program_area_mapping_page import (
    ProgramAreaMappingPage,
)
from uucms.modules.academics.pages.student_committee_mapping_page import (
    StudentCommitteeMappingPage,
)


class PhdSetupWorkflow:
    """Drives the University Admin Ph.D R&D setup across the recorded screens."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.login_as = login_as
        self.program_area = ProgramAreaMappingPage(page, settings.timeout_ms)
        self.faculty_mapping = AorFacultyMappingPage(page, settings.timeout_ms)
        self.student_committee = StudentCommitteeMappingPage(page, settings.timeout_ms)
        self.committee_setup = CommitteeSetupPage(page, settings.timeout_ms)

    def _login(self, stage: Mapping[str, Any]) -> None:
        self.login_as(str(stage["login"]))

    def _open_faculty_screen(self, stage: Mapping[str, Any]) -> None:
        self.faculty_mapping.open_from_menu(
            stage["menu_path"], stage.get("list_item_selector")
        )
        self.faculty_mapping.select_program(
            stage["filters"], str(stage["view_selector"])
        )

    def university_admin_maps_program_area(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.program_area.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.program_area.search_program(
            str(stage["search_selector"]), str(stage["search_term"]),
            str(stage["program_cell"]),
        )
        self.program_area.open_map_area_screen(
            str(stage["map_area_link"]), int(stage.get("map_area_link_index", 0))
        )
        self.program_area.create_research_area(stage)
        self.program_area.delete_research_areas(stage)
        self.program_area.click_control(str(stage["back_selector"]))

    def university_admin_maps_faculty(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_faculty_screen(stage)
        program_row = stage.get("program_row_cell")
        if program_row:
            self.faculty_mapping.open_program_row(str(program_row))
        self.faculty_mapping.map_areas(stage)

    def university_admin_views_mapped_faculty(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_faculty_screen(stage)
        self.faculty_mapping.view_mapped_areas(stage)

    def university_admin_deletes_mapped_faculty(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_faculty_screen(stage)
        self.faculty_mapping.modify_and_delete(stage)

    def university_admin_remaps_faculty(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_faculty_screen(stage)
        self.faculty_mapping.map_areas(stage)

    def university_admin_maps_student_to_committee(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.student_committee.open_from_menu(stage["menu_path"])
        self.student_committee.select_program(
            stage["filters"], str(stage["view_selector"])
        )
        self.student_committee.map_student_to_committee(stage)

    def university_admin_creates_committee(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.committee_setup.open_from_menu(stage["menu_path"])
        self.committee_setup.create_committee(stage)

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        self.university_admin_maps_program_area(data["program_area_mapping"])
        self.university_admin_maps_faculty(data["faculty_mapping"])
        self.university_admin_views_mapped_faculty(data["faculty_mapping_view"])
        self.university_admin_deletes_mapped_faculty(data["faculty_mapping_modify_delete"])
        self.university_admin_remaps_faculty(data["faculty_mapping_remap"])
        self.university_admin_maps_student_to_committee(data["student_committee_mapping"])
        self.university_admin_creates_committee(data["create_committee"])
