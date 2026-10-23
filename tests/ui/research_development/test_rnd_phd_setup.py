"""R&D Ph.D setup test cases: University Admin setup via the Academics screens."""

import pytest

from config.settings import load_test_data
from utils.json_reader import require_fields
from uucms.workflows.research_development.phd_setup_workflow import PhdSetupWorkflow

DATA_FILE = "rnd/phd_setup.json"
DATA_PATH = f"test_data/{DATA_FILE}"

FULL_FLOW_STAGES = (
    "program_area_mapping", "faculty_mapping", "faculty_mapping_view",
    "faculty_mapping_modify_delete", "faculty_mapping_remap",
    "student_committee_mapping", "create_committee",
)


def _require_setup_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _workflow(page, uucms_settings, login_as) -> PhdSetupWorkflow:
    return PhdSetupWorkflow(page, uucms_settings, login_as)


@pytest.mark.rnd
def test_rnd_setup_maps_program_area(page, uucms_settings, login_as):
    """TC-RNDSETUP-001: university admin maps an Area of Research to the Ph.D program (create research area, delete existing mappings)."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "program_area_mapping.login", "program_area_mapping.menu_path",
        "program_area_mapping.search_selector", "program_area_mapping.search_term",
        "program_area_mapping.program_cell", "program_area_mapping.map_area_link",
        "program_area_mapping.research_name_field",
        "program_area_mapping.research_name",
        "program_area_mapping.research_short_name_field",
        "program_area_mapping.research_short_name",
        "program_area_mapping.add_selector", "program_area_mapping.submit_selector",
        "program_area_mapping.confirm_selector", "program_area_mapping.ok_selector",
        "program_area_mapping.back_selector",
        "program_area_mapping.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_program_area(
        data["program_area_mapping"]
    )


@pytest.mark.rnd
def test_rnd_setup_maps_faculty(page, uucms_settings, login_as):
    """TC-RNDSETUP-002: university admin maps an Area of Research to faculty for the Ph.D program."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "faculty_mapping.login", "faculty_mapping.menu_path",
        "faculty_mapping.list_item_selector", "faculty_mapping.filters",
        "faculty_mapping.view_selector", "faculty_mapping.map_action",
        "faculty_mapping.fields", "faculty_mapping.add_selector",
        "faculty_mapping.submit_selector", "faculty_mapping.ok_selector",
        "faculty_mapping.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_faculty(
        data["faculty_mapping"]
    )


@pytest.mark.rnd
def test_rnd_setup_views_mapped_faculty(page, uucms_settings, login_as):
    """TC-RNDSETUP-003: university admin views the mapped Areas of Research to faculty."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "faculty_mapping_view.login", "faculty_mapping_view.menu_path",
        "faculty_mapping_view.list_item_selector", "faculty_mapping_view.filters",
        "faculty_mapping_view.view_selector", "faculty_mapping_view.view_action",
        "faculty_mapping_view.actions", "faculty_mapping_view.view_button",
        "faculty_mapping_view.back_selector", "faculty_mapping_view.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_views_mapped_faculty(
        data["faculty_mapping_view"]
    )


@pytest.mark.rnd
def test_rnd_setup_deletes_mapped_faculty(page, uucms_settings, login_as):
    """TC-RNDSETUP-004: university admin modifies the mapping and deletes the Area of Research from the faculty mapping."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "faculty_mapping_modify_delete.login",
        "faculty_mapping_modify_delete.menu_path",
        "faculty_mapping_modify_delete.list_item_selector",
        "faculty_mapping_modify_delete.filters",
        "faculty_mapping_modify_delete.view_selector",
        "faculty_mapping_modify_delete.modify_action",
        "faculty_mapping_modify_delete.actions",
        "faculty_mapping_modify_delete.view_button",
        "faculty_mapping_modify_delete.delete_selector",
        "faculty_mapping_modify_delete.confirm_selector",
        "faculty_mapping_modify_delete.ok_selector",
        "faculty_mapping_modify_delete.back_selector",
        "faculty_mapping_modify_delete.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_deletes_mapped_faculty(
        data["faculty_mapping_modify_delete"]
    )


@pytest.mark.rnd
def test_rnd_setup_remaps_faculty(page, uucms_settings, login_as):
    """TC-RNDSETUP-005: university admin re-maps the Area of Research to faculty as the final mapping."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "faculty_mapping_remap.login", "faculty_mapping_remap.menu_path",
        "faculty_mapping_remap.list_item_selector", "faculty_mapping_remap.filters",
        "faculty_mapping_remap.view_selector", "faculty_mapping_remap.map_action",
        "faculty_mapping_remap.fields", "faculty_mapping_remap.add_selector",
        "faculty_mapping_remap.submit_selector", "faculty_mapping_remap.ok_selector",
        "faculty_mapping_remap.back_selector", "faculty_mapping_remap.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_remaps_faculty(
        data["faculty_mapping_remap"]
    )


@pytest.mark.rnd
def test_rnd_setup_maps_student_to_committee(page, uucms_settings, login_as):
    """TC-RNDSETUP-006: university admin maps the student to the doctoral committee for the Area of Research."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "student_committee_mapping.login", "student_committee_mapping.menu_path",
        "student_committee_mapping.filters", "student_committee_mapping.view_selector",
        "student_committee_mapping.map_student_action",
        "student_committee_mapping.fields",
        "student_committee_mapping.student_select_selector",
        "student_committee_mapping.student_option",
        "student_committee_mapping.committee_fields",
        "student_committee_mapping.submit_selector",
        "student_committee_mapping.ok_selector",
        "student_committee_mapping.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_maps_student_to_committee(
        data["student_committee_mapping"]
    )


@pytest.mark.rnd
def test_rnd_setup_creates_committee(page, uucms_settings, login_as):
    """TC-RNDSETUP-007: university admin creates the committee under Research And Development > Set-up."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        "create_committee.login", "create_committee.menu_path",
        "create_committee.create_committees_button",
        "create_committee.committee_type_selector",
        "create_committee.committee_type_value",
        "create_committee.create_committee_button",
        "create_committee.committee_name_field", "create_committee.committee_name",
        "create_committee.committee_purpose_field",
        "create_committee.committee_purpose",
        "create_committee.add_selector", "create_committee.ok_selector",
        "create_committee.success_selector",
    )
    _workflow(page, uucms_settings, login_as).university_admin_creates_committee(
        data["create_committee"]
    )


@pytest.mark.rnd
def test_rnd_setup_full_flow(page, uucms_settings, login_as):
    """TC-RNDSETUP-008: full University Admin Ph.D setup flow from program area mapping to committee creation."""
    data = _require_setup_data(
        load_test_data(DATA_FILE),
        *[f"{stage}.login" for stage in FULL_FLOW_STAGES],
    )
    _workflow(page, uucms_settings, login_as).run_full_flow(data)
