"""Academics program setup orchestration across admin roles.

Flow: State Admin creates the statewise Ph.D program details and the
first discipline/subject combination; University Admin maps the program
at university level (program data, disciplines, Areas of Research,
evaluation system), creates the scheme, maps programs with course
types, designs the courses, configures term and course-type credit
details (freeze + validate), and builds the CBCS curriculum; College
Admin selects the electives. Stage data comes from
test_data/academics/program_setup.json.
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.academics.pages.college_elective_page import CollegeElectivePage
from uucms.modules.academics.pages.course_design_page import CourseDesignPage
from uucms.modules.academics.pages.credit_details_page import CreditDetailsPage
from uucms.modules.academics.pages.curriculum_page import CurriculumPage
from uucms.modules.academics.pages.scheme_page import SchemePage
from uucms.modules.academics.pages.state_program_page import StateProgramPage
from uucms.modules.academics.pages.university_program_mapping_page import (
    UniversityProgramMappingPage,
)


class ProgramSetupWorkflow:
    """Drives the state-to-college Ph.D program and curriculum setup."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.login_as = login_as
        self.state_program = StateProgramPage(page, settings.timeout_ms)
        self.program_mapping = UniversityProgramMappingPage(page, settings.timeout_ms)
        self.scheme = SchemePage(page, settings.timeout_ms)
        self.course_design = CourseDesignPage(page, settings.timeout_ms)
        self.credit_details = CreditDetailsPage(page, settings.timeout_ms)
        self.curriculum = CurriculumPage(page, settings.timeout_ms)
        self.college_elective = CollegeElectivePage(page, settings.timeout_ms)

    def _login(self, stage: Mapping[str, Any]) -> None:
        self.login_as(str(stage["login"]))

    def _open_university_program_details(self, stage: Mapping[str, Any]) -> None:
        self.program_mapping.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )

    def state_admin_creates_program(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.state_program.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.state_program.create_program_details(stage)
        self.state_program.add_discipline_combination(stage)

    def university_admin_maps_new_program(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_university_program_details(stage)
        self.program_mapping.map_new_program(stage)

    def university_admin_maps_disciplines(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_university_program_details(stage)
        self.program_mapping.map_disciplines(stage)

    def university_admin_maps_areas_of_research(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_university_program_details(stage)
        self.program_mapping.map_areas_of_research(stage)

    def university_admin_maps_evaluation_system(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self._open_university_program_details(stage)
        self.program_mapping.map_evaluation_system(stage)

    def university_admin_creates_scheme(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.scheme.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.scheme.add_scheme(stage)

    def university_admin_maps_program_course_types(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.scheme.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.scheme.map_program_course_types(stage)

    def university_admin_creates_courses(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.course_design.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.course_design.add_courses(stage)

    def university_admin_configures_term_credits(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.credit_details.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.credit_details.add_term_credits(stage)
        freeze = stage.get("freeze")
        if freeze:
            self.credit_details.freeze_program(freeze)

    def university_admin_configures_course_type_credits(
        self, stage: Mapping[str, Any]
    ) -> None:
        self._login(stage)
        self.credit_details.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.credit_details.add_course_type_credits(stage)
        validate = stage.get("validate")
        if validate:
            self.credit_details.validate_credits(validate)

    def university_admin_creates_curriculum(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.curriculum.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.curriculum.add_curriculum(stage)
        validate = stage.get("validate")
        if validate:
            self.curriculum.validate_curriculum(validate)

    def college_admin_selects_electives(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        menu_path = stage.get("menu_path")
        if menu_path:
            self.college_elective.open_from_menu(
                menu_path, int(stage.get("menu_index", 0))
            )
        self.college_elective.select_electives(stage)

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        self.state_admin_creates_program(data["state_program_creation"])
        self.university_admin_maps_new_program(data["map_new_program"])
        self.university_admin_maps_disciplines(data["map_disciplines"])
        self.university_admin_maps_areas_of_research(data["map_areas_of_research"])
        self.university_admin_maps_evaluation_system(data["map_evaluation_system"])
        self.university_admin_creates_scheme(data["scheme_creation"])
        self.university_admin_maps_program_course_types(data["map_program_course_types"])
        self.university_admin_creates_courses(data["course_creation"])
        self.university_admin_configures_term_credits(data["term_credit_details"])
        self.university_admin_configures_course_type_credits(
            data["course_type_credit_details"]
        )
        self.university_admin_creates_curriculum(data["curriculum_creation"])
        self.college_admin_selects_electives(data["college_elective_selection"])
