"""Academics program setup test cases: Ph.D program and curriculum setup across admin roles."""

import pytest

from config.settings import load_test_data
from utils.json_reader import require_fields
from uucms.workflows.program_setup_workflow import ProgramSetupWorkflow

DATA_FILE = "academics/program_setup.json"
DATA_PATH = f"test_data/{DATA_FILE}"

FULL_FLOW_STAGES = (
    "state_program_creation", "map_new_program", "map_disciplines",
    "map_areas_of_research", "map_evaluation_system", "scheme_creation",
    "map_program_course_types", "course_creation", "term_credit_details",
    "course_type_credit_details", "curriculum_creation",
    "college_elective_selection",
)


def _require_setup_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _workflow(page, uucms_settings, login_as) -> ProgramSetupWorkflow:
    return ProgramSetupWorkflow(page, uucms_settings, login_as)


@pytest.mark.academics
def test_program_setup_state_admin_creates_program(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-001: state admin creates the statewise Ph.D program details and the first discipline/combination."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "state_program_creation.login", "state_program_creation.menu_path",
        "state_program_creation.add_program_button",
        "state_program_creation.program_actions",
        "state_program_creation.go_upload_file",
        "state_program_creation.add_new_program_selector",
        "state_program_creation.confirm_selector",
        "state_program_creation.ok_selector",
        "state_program_creation.program_success_selector",
        "state_program_creation.search_selector",
        "state_program_creation.search_term",
        "state_program_creation.add_combination_link",
        "state_program_creation.subject_trigger_selector",
        "state_program_creation.subject_searches",
        "state_program_creation.combination_actions",
        "state_program_creation.submit_selector",
        "state_program_creation.combination_success_selector",
    )
    _workflow(page, uucms_settings, login_as).state_admin_creates_program(
        data["state_program_creation"]
    )


@pytest.mark.academics
def test_program_setup_maps_new_program(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-002: university admin maps the new Ph.D program at university level."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "map_new_program.login", "map_new_program.menu_path",
        "map_new_program.map_new_program_button", "map_new_program.fields",
        "map_new_program.add_button", "map_new_program.confirm_selector",
        "map_new_program.ok_selector", "map_new_program.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_new_program(
        data["map_new_program"]
    )


@pytest.mark.academics
def test_program_setup_maps_disciplines(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-003: university admin maps the program discipline/combination rows."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "map_disciplines.login", "map_disciplines.menu_path",
        "map_disciplines.search_selector", "map_disciplines.search_term",
        "map_disciplines.map_discipline_action",
        "map_disciplines.discipline_selector",
        "map_disciplines.faculty_selector", "map_disciplines.disciplines",
        "map_disciplines.add_discipline_button",
        "map_disciplines.confirm_selector", "map_disciplines.ok_selector",
        "map_disciplines.back_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_disciplines(
        data["map_disciplines"]
    )


@pytest.mark.academics
def test_program_setup_maps_areas_of_research(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-004: university admin creates the Area of Research mappings for the Ph.D program."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "map_areas_of_research.login", "map_areas_of_research.menu_path",
        "map_areas_of_research.map_area_link", "map_areas_of_research.areas",
        "map_areas_of_research.research_short_name_field",
        "map_areas_of_research.add_selector",
        "map_areas_of_research.submit_selector",
        "map_areas_of_research.confirm_selector",
        "map_areas_of_research.ok_selector",
        "map_areas_of_research.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_areas_of_research(
        data["map_areas_of_research"]
    )


@pytest.mark.academics
def test_program_setup_maps_evaluation_system(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-005: university admin maps the evaluation system to the Ph.D program."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "map_evaluation_system.login", "map_evaluation_system.menu_path",
        "map_evaluation_system.map_evaluation_button",
        "map_evaluation_system.actions", "map_evaluation_system.add_button",
        "map_evaluation_system.confirm_selector",
        "map_evaluation_system.ok_selector",
        "map_evaluation_system.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_evaluation_system(
        data["map_evaluation_system"]
    )


@pytest.mark.academics
def test_program_setup_creates_scheme(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-006: university admin creates the new Ph.D scheme under Schemes & Course Types."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "scheme_creation.login", "scheme_creation.menu_path",
        "scheme_creation.add_scheme_button",
        "scheme_creation.scheme_name_field", "scheme_creation.scheme_name",
        "scheme_creation.scheme_code_field", "scheme_creation.scheme_code",
        "scheme_creation.fields", "scheme_creation.add_new_scheme_selector",
        "scheme_creation.confirm_selector", "scheme_creation.ok_selector",
        "scheme_creation.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_creates_scheme(
        data["scheme_creation"]
    )


@pytest.mark.academics
def test_program_setup_maps_program_course_types(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-007: university admin maps the program with its course types to the Ph.D scheme."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "map_program_course_types.login", "map_program_course_types.menu_path",
        "map_program_course_types.actions",
        "map_program_course_types.submit_selector",
        "map_program_course_types.confirm_selector",
        "map_program_course_types.ok_selector",
        "map_program_course_types.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_program_course_types(
        data["map_program_course_types"]
    )


@pytest.mark.academics
def test_program_setup_creates_courses(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-008: university admin creates the course/paper details with credit and evaluation components."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "course_creation.login", "course_creation.menu_path",
        "course_creation.add_course_button",
        "course_creation.department_trigger_selector",
        "course_creation.department_search_selector",
        "course_creation.courses", "course_creation.basic_add_selector",
        "course_creation.credit_fields", "course_creation.credit_add_selector",
        "course_creation.next_selector",
        "course_creation.evaluation_components",
        "course_creation.evaluation_add_selector",
        "course_creation.submit_selector", "course_creation.confirm_selector",
        "course_creation.ok_selector", "course_creation.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_creates_courses(
        data["course_creation"]
    )


@pytest.mark.academics
def test_program_setup_configures_term_credits(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-009: university admin configures the term/semester credit details and freezes the program."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "term_credit_details.login", "term_credit_details.menu_path",
        "term_credit_details.add_term_credit_button",
        "term_credit_details.fields", "term_credit_details.min_credit_field",
        "term_credit_details.min_credit", "term_credit_details.max_credit_field",
        "term_credit_details.max_credit", "term_credit_details.row_add_selector",
        "term_credit_details.program_actions",
        "term_credit_details.add_temp_programwise",
        "term_credit_details.submit_selector",
        "term_credit_details.confirm_selector",
        "term_credit_details.ok_selector",
        "term_credit_details.success_selector",
        "term_credit_details.freeze",
    )
    _workflow(page, uucms_settings, login_as).university_admin_configures_term_credits(
        data["term_credit_details"]
    )


@pytest.mark.academics
def test_program_setup_configures_course_type_credits(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-010: university admin configures the course-type credit details and validates them."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "course_type_credit_details.login",
        "course_type_credit_details.menu_path",
        "course_type_credit_details.fields",
        "course_type_credit_details.course_types",
        "course_type_credit_details.credit_field",
        "course_type_credit_details.row_add_selector",
        "course_type_credit_details.program_actions",
        "course_type_credit_details.add_temp_programwise",
        "course_type_credit_details.submit_selector",
        "course_type_credit_details.confirm_selector",
        "course_type_credit_details.ok_selector",
        "course_type_credit_details.success_selector",
        "course_type_credit_details.validate",
    )
    _workflow(page, uucms_settings, login_as).university_admin_configures_course_type_credits(
        data["course_type_credit_details"]
    )


@pytest.mark.academics
def test_program_setup_creates_curriculum(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-011: university admin creates the CBCS curriculum rows and validates the curriculum."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "curriculum_creation.login", "curriculum_creation.menu_path",
        "curriculum_creation.fields", "curriculum_creation.rows",
        "curriculum_creation.add_temp_button",
        "curriculum_creation.program_actions",
        "curriculum_creation.add_temp_programwise",
        "curriculum_creation.submit_selector",
        "curriculum_creation.confirm_selector",
        "curriculum_creation.ok_selector",
        "curriculum_creation.success_selector",
        "curriculum_creation.validate",
    )
    _workflow(page, uucms_settings, login_as).university_admin_creates_curriculum(
        data["curriculum_creation"]
    )


@pytest.mark.academics
def test_program_setup_college_admin_selects_electives(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-012: college admin selects the Ph.D program electives with the allocation method."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "college_elective_selection.login",
        "college_elective_selection.search_selector",
        "college_elective_selection.search_term",
        "college_elective_selection.select_electives_action",
        "college_elective_selection.fields",
        "college_elective_selection.elective_checkbox",
        "college_elective_selection.final_fields",
        "college_elective_selection.save_selector",
        "college_elective_selection.confirm_selector",
        "college_elective_selection.ok_selector",
        "college_elective_selection.success_selector",
    )
    _workflow(page, uucms_settings, login_as).college_admin_selects_electives(
        data["college_elective_selection"]
    )


@pytest.mark.academics
def test_program_setup_full_flow(page, uucms_settings, login_as):
    """TC-PROGRAMSETUP-013: full state-to-college Ph.D program and curriculum setup flow."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        *[f"{stage}.login" for stage in FULL_FLOW_STAGES],
    )
    _workflow(page, uucms_settings, login_as).run_full_flow(data)
