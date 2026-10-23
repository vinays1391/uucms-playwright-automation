"""R&D Phase-1 ADMISSION test cases: university wise Program Details."""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.research_development.pages.admission.map_new_program_page import MapNewProgramPage
from uucms.modules.research_development.pages.admission.program_details_page import ProgramDetailsPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/admission_program_details.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_admission_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _open_program_list(page, uucms_settings, filters) -> ProgramDetailsPage:
    program_page = ProgramDetailsPage(page, uucms_settings.timeout_ms)
    program_page.open_from_menu()
    if filters:
        program_page.apply_filters(filters)
    return program_page


@pytest.mark.rnd
def test_rnd_admission_view_program_list_university_admin(authenticated_page, uucms_settings):
    """TC-ADMISSION-001: university admin views the university wise program details list."""
    data = _require_admission_data(
        load_test_data(DATA_FILE), "list.filters", "list.list_columns", "list.row_actions"
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    program_page.expect_list_columns(data["list"]["list_columns"])
    program_page.expect_texts_visible(data["list"]["row_actions"])


@pytest.mark.rnd
def test_rnd_admission_college_admin_view_program_list(page, uucms_settings, login_as):
    """TC-ADMISSION-002: college admin can view the same university wise program details list."""
    data = _require_admission_data(
        load_test_data(DATA_FILE), "list.filters", "list.list_columns", "list.row_actions"
    )
    login_as("college_admin")
    program_page = _open_program_list(page, uucms_settings, data["list"]["filters"])
    program_page.expect_list_columns(data["list"]["list_columns"])
    program_page.expect_texts_visible(data["list"]["row_actions"])


@pytest.mark.rnd
def test_rnd_admission_edit_program_details(authenticated_page, uucms_settings):
    """TC-ADMISSION-003: university admin edits and saves program details."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "edit.program_row", "edit.edit_action", "edit.actions",
        "edit.save_selector", "edit.expected_values",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    edit = data["edit"]
    program_page.edit_program(
        edit["program_row"], edit["edit_action"], edit["actions"], edit["save_selector"]
    )
    program_page.open_from_menu()
    program_page.expect_row_updated(edit["program_row"], edit["expected_values"])


@pytest.mark.rnd
def test_rnd_admission_view_program_read_only(authenticated_page, uucms_settings):
    """TC-ADMISSION-004: program details open in read-only view without Save."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "view.program_row", "view.view_action", "view.columns", "view.save_selector",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    view = data["view"]
    program_page.view_program(view["program_row"], view["view_action"])
    program_page.expect_read_only_view(view["columns"], view["save_selector"])


@pytest.mark.rnd
def test_rnd_admission_map_discipline(authenticated_page, uucms_settings):
    """TC-ADMISSION-005: map a Discipline/Combination to a program."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_discipline.program_row", "map_discipline.action", "map_discipline.actions",
        "map_discipline.submit_selector", "map_discipline.success_selector",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    mapping = data["map_discipline"]
    program_page.map_discipline(
        mapping["program_row"], mapping["action"], mapping["actions"],
        mapping["submit_selector"], mapping["success_selector"],
    )


@pytest.mark.rnd
def test_rnd_admission_map_areas_of_research(authenticated_page, uucms_settings):
    """TC-ADMISSION-006: map Areas of Research to a program."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_areas.program_row", "map_areas.action", "map_areas.actions",
        "map_areas.submit_selector", "map_areas.success_selector",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    mapping = data["map_areas"]
    program_page.map_areas_of_research(
        mapping["program_row"], mapping["action"], mapping["actions"],
        mapping["submit_selector"], mapping["success_selector"],
    )


@pytest.mark.rnd
def test_rnd_admission_map_new_program_teaching_mode_medium(authenticated_page, uucms_settings):
    """TC-ADMISSION-007: map Teaching Mode and Medium of Instruction."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_new_program.program_row", "map_new_program.action",
        "map_new_program.submit_selector",
        "map_new_program.teaching_mode_medium.actions",
        "map_new_program.teaching_mode_medium.success_selector",
        "map_new_program.teaching_mode_medium.expected_values",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    map_new = data["map_new_program"]
    program_page.open_map_new_program(map_new["program_row"], map_new["action"])
    mapping_page = MapNewProgramPage(authenticated_page, uucms_settings.timeout_ms)
    case = map_new["teaching_mode_medium"]
    mapping_page.fill_mapping_fields(case["actions"])
    mapping_page.submit_mapping(map_new["submit_selector"], case["success_selector"])
    mapping_page.expect_mapping_displayed(case["success_selector"], case["expected_values"])


@pytest.mark.rnd
def test_rnd_admission_map_new_program_evaluation_system(authenticated_page, uucms_settings):
    """TC-ADMISSION-008: map the Evaluation System."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_new_program.program_row", "map_new_program.action",
        "map_new_program.submit_selector",
        "map_new_program.evaluation_system.actions",
        "map_new_program.evaluation_system.success_selector",
        "map_new_program.evaluation_system.expected_values",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    map_new = data["map_new_program"]
    program_page.open_map_new_program(map_new["program_row"], map_new["action"])
    mapping_page = MapNewProgramPage(authenticated_page, uucms_settings.timeout_ms)
    case = map_new["evaluation_system"]
    mapping_page.fill_mapping_fields(case["actions"])
    mapping_page.submit_mapping(map_new["submit_selector"], case["success_selector"])
    mapping_page.expect_mapping_displayed(case["success_selector"], case["expected_values"])


@pytest.mark.rnd
def test_rnd_admission_map_new_program_language(authenticated_page, uucms_settings):
    """TC-ADMISSION-009: map the Language."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_new_program.program_row", "map_new_program.action",
        "map_new_program.submit_selector",
        "map_new_program.language.actions",
        "map_new_program.language.success_selector",
        "map_new_program.language.expected_values",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    map_new = data["map_new_program"]
    program_page.open_map_new_program(map_new["program_row"], map_new["action"])
    mapping_page = MapNewProgramPage(authenticated_page, uucms_settings.timeout_ms)
    case = map_new["language"]
    mapping_page.fill_mapping_fields(case["actions"])
    mapping_page.submit_mapping(map_new["submit_selector"], case["success_selector"])
    mapping_page.expect_mapping_displayed(case["success_selector"], case["expected_values"])


@pytest.mark.rnd
def test_rnd_admission_map_new_program_open_elective(authenticated_page, uucms_settings):
    """TC-ADMISSION-010: map the Open Elective."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_new_program.program_row", "map_new_program.action",
        "map_new_program.submit_selector",
        "map_new_program.open_elective.actions",
        "map_new_program.open_elective.success_selector",
        "map_new_program.open_elective.expected_values",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    map_new = data["map_new_program"]
    program_page.open_map_new_program(map_new["program_row"], map_new["action"])
    mapping_page = MapNewProgramPage(authenticated_page, uucms_settings.timeout_ms)
    case = map_new["open_elective"]
    mapping_page.fill_mapping_fields(case["actions"])
    mapping_page.submit_mapping(map_new["submit_selector"], case["success_selector"])
    mapping_page.expect_mapping_displayed(case["success_selector"], case["expected_values"])


@pytest.mark.rnd
def test_rnd_admission_map_new_program_blank_validation(authenticated_page, uucms_settings):
    """TC-ADMISSION-011: Map New Program with blank fields shows validation and is not saved."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "map_new_program.program_row", "map_new_program.action",
        "map_new_program.submit_selector",
        "map_new_program.blank.expected_message",
        "map_new_program.blank.unmapped_check_selector",
    )
    program_page = _open_program_list(authenticated_page, uucms_settings, data["list"]["filters"])
    map_new = data["map_new_program"]
    program_page.open_map_new_program(map_new["program_row"], map_new["action"])
    mapping_page = MapNewProgramPage(authenticated_page, uucms_settings.timeout_ms)
    mapping_page.submit_blank_expect_validation(
        map_new["submit_selector"], map_new["blank"]["expected_message"]
    )
    expect(
        authenticated_page.locator(map_new["blank"]["unmapped_check_selector"])
    ).to_have_count(0)
