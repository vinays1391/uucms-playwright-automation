"""R&D Phase-2 COMMITTEEMAPPING test cases.

Areas of Research are mapped to (Doctoral) Committees and students;
the mapped committee chairperson sees the reports of the mapped
students; modification is restricted once the student has submitted the
synopsis.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.research_development.pages.committee_mapping.aor_committee_mapping_page import AorCommitteeMappingPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/committee_mapping.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_cm_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _mapping_page(page, uucms_settings) -> AorCommitteeMappingPage:
    return AorCommitteeMappingPage(page, uucms_settings.timeout_ms)


def _open_list(page, uucms_settings, section) -> AorCommitteeMappingPage:
    page_obj = _mapping_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


@pytest.mark.rnd
def test_rnd_cm_mapped_aor_list(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-001: Mapped Areas of Research list with all mapping actions."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "mapped_list.login", "mapped_list.menu_path", "mapped_list.filters",
        "mapped_list.list_columns", "mapped_list.row_actions",
        "mapped_list.discipline_select", "mapped_list.discipline_present",
        "mapped_list.discipline_absent",
    )
    section = data["mapped_list"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.expect_list_columns(section["list_columns"])
    for action in section["row_actions"]:
        expect(page.get_by_text(action, exact=True)).to_be_visible()
    options = page_obj.collect_select_options(section["discipline_select"])
    for option in section["discipline_present"]:
        assert option in options, f"{option!r} missing from {options}"
    for option in section["discipline_absent"]:
        assert option not in options, f"{option!r} should not be in {options}"


@pytest.mark.rnd
def test_rnd_cm_map_aor_to_committee(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-002: an Area of Research is mapped to a Committee and a student."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "map_aor.login", "map_aor.menu_path", "map_aor.filters",
        "map_aor.aor_row", "map_aor.map_action", "map_aor.actions",
        "map_aor.add_selector", "map_aor.submit_selector", "map_aor.success_selector",
        "map_aor.mapped_row", "map_aor.expected_row_values",
    )
    section = data["map_aor"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_mapping_screen(section["aor_row"], section["map_action"])
    page_obj.add_mapping(
        section["actions"], section["add_selector"],
        section["submit_selector"], section["success_selector"],
    )
    page_obj.expect_row_values(section["mapped_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_cm_chairperson_sees_mapped_reports(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-003: the mapped committee chairperson sees the student's reports."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "mapped_reports.login", "mapped_reports.menu_path",
        "mapped_reports.present", "mapped_reports.absent",
    )
    section = data["mapped_reports"]
    login_as(section["login"])
    page_obj = _mapping_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    page_obj.expect_rows_listed(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_cm_view_mapped_multi_select(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-004: view mapped AORs with the Area of Research multi-select filter."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "view_mapped.login", "view_mapped.menu_path", "view_mapped.filters",
        "view_mapped.aor_row", "view_mapped.view_action", "view_mapped.actions",
        "view_mapped.view_button", "view_mapped.list_columns",
        "view_mapped.delete_action_check", "view_mapped.submit_action_check",
        "view_mapped.back_selector", "view_mapped.list_check",
    )
    section = data["view_mapped"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_mapping_screen(section["aor_row"], section["view_action"])
    page_obj.view_mappings(section["actions"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])
    page_obj.expect_read_only_view(
        section["delete_action_check"], section["submit_action_check"]
    )
    page_obj.click_control(section["back_selector"])
    expect(page.locator(section["list_check"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_cm_modify_allowed_before_synopsis(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-005: the committee mapping is modifiable before the student submits the synopsis."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "modify_allowed.login", "modify_allowed.menu_path", "modify_allowed.filters",
        "modify_allowed.aor_row", "modify_allowed.modify_action",
        "modify_allowed.mapping_row", "modify_allowed.committee_select",
        "modify_allowed.new_committee", "modify_allowed.submit_selector",
        "modify_allowed.success_selector", "modify_allowed.expected_row_values",
    )
    section = data["modify_allowed"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_mapping_screen(section["aor_row"], section["modify_action"])
    page_obj.modify_mapping(
        section["committee_select"], section["new_committee"],
        section["submit_selector"], section["success_selector"],
    )
    page_obj.expect_row_values(section["mapping_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_cm_modify_restricted_after_synopsis(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-006: the mapping is restricted after the student has submitted the synopsis."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "modify_restricted.login", "modify_restricted.menu_path",
        "modify_restricted.filters", "modify_restricted.aor_row",
        "modify_restricted.modify_action", "modify_restricted.mapping_row",
        "modify_restricted.committee_select", "modify_restricted.new_committee",
        "modify_restricted.submit_selector", "modify_restricted.expected_message",
        "modify_restricted.unchanged_row_values",
    )
    section = data["modify_restricted"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_mapping_screen(section["aor_row"], section["modify_action"])
    page_obj.attempt_modify_mapping(
        section["committee_select"], section["new_committee"],
        section["submit_selector"], section["expected_message"],
    )
    page_obj.expect_row_values(section["mapping_row"], section["unchanged_row_values"])


@pytest.mark.rnd
def test_rnd_cm_blank_committee_type(page, uucms_settings, login_as):
    """TC-COMMITTEEMAPPING-007: Committee Type left blank is rejected as mandatory."""
    data = _require_cm_data(
        load_test_data(DATA_FILE),
        "blank_committee_type.login", "blank_committee_type.menu_path",
        "blank_committee_type.filters", "blank_committee_type.aor_row",
        "blank_committee_type.map_action", "blank_committee_type.actions",
        "blank_committee_type.add_selector", "blank_committee_type.expected_message",
    )
    section = data["blank_committee_type"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_mapping_screen(section["aor_row"], section["map_action"])
    page_obj.attempt_add_mapping(
        section["actions"], section["add_selector"], section["expected_message"]
    )
