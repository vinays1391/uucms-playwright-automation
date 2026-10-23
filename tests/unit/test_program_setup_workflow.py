"""Unit tests for the state-to-college Ph.D program setup workflow."""

from unittest.mock import Mock

from uucms.workflows.program_setup_workflow import ProgramSetupWorkflow

STAGE_KEYS = (
    "state_program_creation", "map_new_program", "map_disciplines",
    "map_areas_of_research", "map_evaluation_system", "scheme_creation",
    "map_program_course_types", "course_creation", "term_credit_details",
    "course_type_credit_details", "curriculum_creation",
    "college_elective_selection",
)

METHOD_NAMES = (
    "state_admin_creates_program", "university_admin_maps_new_program",
    "university_admin_maps_disciplines", "university_admin_maps_areas_of_research",
    "university_admin_maps_evaluation_system", "university_admin_creates_scheme",
    "university_admin_maps_program_course_types", "university_admin_creates_courses",
    "university_admin_configures_term_credits",
    "university_admin_configures_course_type_credits",
    "university_admin_creates_curriculum", "college_admin_selects_electives",
)


def test_program_setup_workflow_runs_all_stages_in_order() -> None:
    workflow = ProgramSetupWorkflow.__new__(ProgramSetupWorkflow)
    calls: list[str] = []
    mocks: dict[str, Mock] = {}
    for method_name, stage_key in zip(METHOD_NAMES, STAGE_KEYS):
        mock = Mock(side_effect=lambda _stage, _name=method_name: calls.append(_name))
        mocks[method_name] = mock
        setattr(workflow, method_name, mock)
    data = {stage_key: {"stage": stage_key} for stage_key in STAGE_KEYS}

    workflow.run_full_flow(data)

    assert calls == list(METHOD_NAMES)
    for method_name, stage_key in zip(METHOD_NAMES, STAGE_KEYS):
        mocks[method_name].assert_called_once_with(data[stage_key])


def test_program_setup_scheme_stage_logs_in_and_creates_scheme() -> None:
    workflow = ProgramSetupWorkflow.__new__(ProgramSetupWorkflow)
    workflow.login_as = Mock()
    workflow.scheme = Mock()
    stage = {
        "login": "university_admin",
        "menu_path": ["Academics", "Schemes & Course Types", "Schemes"],
        "menu_index": 0,
        "add_scheme_button": "role=button[name='Add New Scheme Details']",
        "scheme_name_field": "#Scheme_Name",
        "scheme_name": "SCHEME-PHD",
        "scheme_code_field": "#Scheme_Code",
        "scheme_code": "SCh-PHD",
        "fields": [],
        "add_new_scheme_selector": "role=button[name='Add New Scheme']",
        "confirm_selector": "role=button[name='Yes']",
        "ok_selector": "role=button[name='OK']",
        "success_selector": "role=button[name='success']",
    }

    workflow.university_admin_creates_scheme(stage)

    workflow.login_as.assert_called_once_with("university_admin")
    workflow.scheme.open_from_menu.assert_called_once_with(
        stage["menu_path"], 0
    )
    workflow.scheme.add_scheme.assert_called_once_with(stage)


def test_program_setup_college_stage_skips_menu_when_not_configured() -> None:
    workflow = ProgramSetupWorkflow.__new__(ProgramSetupWorkflow)
    workflow.login_as = Mock()
    workflow.college_elective = Mock()
    stage = {
        "login": "college_admin",
        "search_selector": "role=searchbox[name='Search:']",
        "search_term": "ph.d",
        "select_electives_action": "Select Electives",
        "fields": [],
        "elective_checkbox": "#item_isSelectedElective_Value",
        "final_fields": [],
        "save_selector": "role=button[name='Save']",
        "confirm_selector": "role=button[name='Yes']",
        "ok_selector": "role=button[name='OK']",
        "success_selector": "role=button[name='success']",
    }

    workflow.college_admin_selects_electives(stage)

    workflow.login_as.assert_called_once_with("college_admin")
    workflow.college_elective.open_from_menu.assert_not_called()
    workflow.college_elective.select_electives.assert_called_once_with(stage)
