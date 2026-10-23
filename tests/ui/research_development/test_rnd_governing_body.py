"""R&D Phase-2 GOVERNINGBODY test cases.

Committee creation (Board of Studies / Doctoral Committee / Panel of
Examiners / Research Review Committee), the Committee ID sequence
rules, member mapping to committees and role restrictions. Role logins
come from the "roles" mapping in test_data/login/LoginData.json.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.governing_body.committee_members_page import CommitteeMembersPage
from uucms.modules.research_development.pages.governing_body.committees_page import CommitteesPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/governing_bodies.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_gb_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _committees(page, uucms_settings) -> CommitteesPage:
    return CommitteesPage(page, uucms_settings.timeout_ms)


def _members(page, uucms_settings) -> CommitteeMembersPage:
    return CommitteeMembersPage(page, uucms_settings.timeout_ms)


def _create_actions(data: dict, entry: dict, purpose: str | None = None) -> list[dict]:
    """Build the Create Committees form actions for one committee entry."""
    screen = data["create_screen"]
    return [
        {"type": "select_label", "selector": screen["committee_type_select"],
         "value": entry["committee_type"]},
        {"type": "fill", "selector": screen["committee_id_field"],
         "value": entry["committee_id"]},
        {"type": "fill", "selector": screen["committee_name_field"],
         "value": entry["committee_name"]},
        {"type": "fill", "selector": screen["committee_name_kannada_field"],
         "value": entry["committee_name_kannada"]},
        {"type": "fill", "selector": screen["committee_purpose_field"],
         "value": purpose or entry.get("committee_purpose") or screen["purpose"]},
    ]


@pytest.mark.rnd
def test_rnd_gb_create_committee(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-001: University Admin creates a Board of Studies committee."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "create_screen.committee_type_select", "create_screen.committee_id_field",
        "create_screen.committee_name_field", "create_screen.committee_name_kannada_field",
        "create_screen.committee_purpose_field", "create_screen.purpose",
        "create_screen.add_selector", "create_screen.success_selector",
        "create_screen.list_columns",
        "create_committee.committee_type", "create_committee.committee_id",
        "create_committee.committee_name", "create_committee.committee_name_kannada",
        "create_committee.committee_row", "create_committee.expected_row_values",
    )
    screen = data["create_screen"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.expect_list_columns(screen["list_columns"])
    entry = data["create_committee"]
    page_obj.create_committee(
        _create_actions(data, entry), screen["add_selector"], screen["success_selector"]
    )
    page_obj.expect_row_values(entry["committee_row"], entry["expected_row_values"])


@pytest.mark.rnd
def test_rnd_gb_committee_id_sequence(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-002: Committee IDs follow prefix + University ID + 3-digit code."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "create_screen.committee_type_select", "create_screen.committee_id_field",
        "create_screen.committee_name_field", "create_screen.committee_name_kannada_field",
        "create_screen.committee_purpose_field", "create_screen.purpose",
        "create_screen.add_selector",
        "id_sequence.university_id", "id_sequence.communities_to_create",
        "id_sequence.committee_id_cells",
    )
    screen = data["create_screen"]
    seq = data["id_sequence"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    for entry in seq["communities_to_create"]:
        page_obj.create_committee(
            _create_actions(data, entry), screen["add_selector"]
        )
    page_obj.open_from_menu(screen["menu_path"])
    ids = page_obj.collect_cell_texts(seq["committee_id_cells"])
    for entry in seq["communities_to_create"]:
        assert entry["expected_id"] in ids, (
            f"Expected Committee ID {entry['expected_id']} (prefix + university id "
            f"{seq['university_id']} + 3-digit code) not found in {ids}"
        )


@pytest.mark.rnd
def test_rnd_gb_invalid_committee_id(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-003: invalid Committee ID patterns are rejected and no committee is created."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "create_screen.committee_type_select", "create_screen.committee_id_field",
        "create_screen.committee_name_field", "create_screen.committee_name_kannada_field",
        "create_screen.committee_purpose_field", "create_screen.purpose",
        "create_screen.add_selector",
        "invalid_id.committees", "invalid_id.expected_message",
        "invalid_id.dialog_ok_selector",
    )
    screen = data["create_screen"]
    invalid = data["invalid_id"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    for entry in invalid["committees"]:
        page_obj.open_from_menu(screen["menu_path"])
        page_obj.attempt_create_invalid(
            _create_actions(data, entry), screen["add_selector"],
            invalid["expected_message"],
        )
        page_obj.dismiss_validation_dialog(invalid["dialog_ok_selector"])
        page_obj.open_from_menu(screen["menu_path"])
        page_obj.expect_committee_not_created(entry["committee_id"])


@pytest.mark.rnd
def test_rnd_gb_blank_committee_type(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-004: Committee Type left blank is rejected as mandatory."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "create_screen.add_selector",
        "blank_type.actions", "blank_type.expected_message",
        "blank_type.dialog_ok_selector", "blank_type.committee_id",
    )
    screen = data["create_screen"]
    blank = data["blank_type"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.attempt_create_invalid(
        blank["actions"], screen["add_selector"], blank["expected_message"]
    )
    page_obj.dismiss_validation_dialog(blank["dialog_ok_selector"])
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.expect_committee_not_created(blank["committee_id"])


@pytest.mark.rnd
def test_rnd_gb_create_committee_college_admin(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-005: College Admin can create a committee on the same screen."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.menu_path",
        "create_screen.committee_type_select", "create_screen.committee_id_field",
        "create_screen.committee_name_field", "create_screen.committee_name_kannada_field",
        "create_screen.committee_purpose_field", "create_screen.purpose",
        "create_screen.add_selector",
        "college_admin_create.login", "college_admin_create.committee_type",
        "college_admin_create.committee_id", "college_admin_create.committee_name",
        "college_admin_create.committee_name_kannada", "college_admin_create.committee_row",
        "college_admin_create.expected_row_values",
    )
    screen = data["create_screen"]
    entry = data["college_admin_create"]
    login_as(entry["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.create_committee(
        _create_actions(data, entry), screen["add_selector"]
    )
    page_obj.expect_row_values(entry["committee_row"], entry["expected_row_values"])


@pytest.mark.rnd
def test_rnd_gb_delete_committee(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-006: a committee without mapped members can be deleted."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "delete_committee.committee_row", "delete_committee.delete_action",
        "delete_committee.confirm_selector", "delete_committee.success_selector",
    )
    screen = data["create_screen"]
    delete = data["delete_committee"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.delete_committee(
        delete["committee_row"], delete["delete_action"],
        delete["confirm_selector"], delete["success_selector"],
    )
    page_obj.expect_row_absent(delete["committee_row"])


@pytest.mark.rnd
def test_rnd_gb_submit_committees(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-007: created committees are submitted and remain visible."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "submit_committees.submit_selector", "submit_committees.back_selector",
        "submit_committees.success_selector", "submit_committees.expected_rows",
    )
    screen = data["create_screen"]
    submit = data["submit_committees"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.submit_committees(
        submit["submit_selector"], submit["back_selector"], submit["success_selector"]
    )
    page_obj.open_from_menu(screen["menu_path"])
    for committee in submit["expected_rows"]:
        expect(page.get_by_text(committee, exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_gb_row_member_actions(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-008: each committee row offers Map/View/Edit Members to Committee."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "create_screen.login", "create_screen.menu_path",
        "row_member_actions.committee_row", "row_member_actions.action_texts",
    )
    screen = data["create_screen"]
    actions = data["row_member_actions"]
    login_as(screen["login"])
    page_obj = _committees(page, uucms_settings)
    page_obj.open_from_menu(screen["menu_path"])
    page_obj.expect_member_actions(actions["committee_row"], actions["action_texts"])


@pytest.mark.rnd
def test_rnd_gb_map_member_happy_path(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-009: a faculty member is mapped to a committee as Chairperson."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "map_members.login", "map_members.menu_path", "map_members.filters",
        "map_members.actions", "map_members.add_selector", "map_members.map_selector",
        "map_members.success_selector", "map_members.member_row",
        "map_members.expected_row_values",
    )
    section = data["map_members"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.map_member(
        section["actions"], section["add_selector"],
        section["map_selector"], section["success_selector"],
    )
    page_obj.expect_row_values(section["member_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_gb_faculty_type_teaching_staff(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-010: Faculty Type offers Permanent/Temporary/Outside University;
    the Employee list shows teaching staff only."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "faculty_type_options.login", "faculty_type_options.menu_path",
        "faculty_type_options.filters", "faculty_type_options.faculty_type_select",
        "faculty_type_options.expected_options", "faculty_type_options.employee_select",
        "faculty_type_options.employee_list_container",
        "faculty_type_options.present", "faculty_type_options.absent",
    )
    section = data["faculty_type_options"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_select_options(
        section["faculty_type_select"], section["expected_options"]
    )
    page_obj.click_control(section["employee_select"])
    page_obj.expect_options_in_container(
        section["employee_list_container"], section["present"], section["absent"]
    )


@pytest.mark.rnd
def test_rnd_gb_department_restricted_to_discipline(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-011: the Department list is limited to departments mapped to the discipline."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "department_restriction.login", "department_restriction.menu_path",
        "department_restriction.filters", "department_restriction.department_select",
        "department_restriction.expected_options", "department_restriction.absent_options",
    )
    section = data["department_restriction"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    options = page_obj.collect_select_options(section["department_select"])
    for option in section["expected_options"]:
        assert option in options, f"{option!r} missing from {options}"
    for option in section["absent_options"]:
        assert option not in options, f"{option!r} should not be in {options}"


@pytest.mark.rnd
def test_rnd_gb_single_chairperson(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-012: only one Chairperson is allowed per committee."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "single_chairperson.login", "single_chairperson.menu_path",
        "single_chairperson.filters", "single_chairperson.actions",
        "single_chairperson.add_selector", "single_chairperson.expected_message",
        "single_chairperson.member_not_saved_text",
    )
    section = data["single_chairperson"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.attempt_add_member(
        section["actions"], section["add_selector"], section["expected_message"]
    )
    page_obj.expect_absent(section["member_not_saved_text"])


@pytest.mark.rnd
def test_rnd_gb_map_member_and_secretary(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-013: Member and Member Secretary are mapped to the committee."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "map_member_and_secretary.login", "map_member_and_secretary.menu_path",
        "map_member_and_secretary.filters", "map_member_and_secretary.employee_select",
        "map_member_and_secretary.member_type_select", "map_member_and_secretary.phone_field",
        "map_member_and_secretary.email_field", "map_member_and_secretary.members",
        "map_member_and_secretary.add_selector", "map_member_and_secretary.map_selector",
        "map_member_and_secretary.success_selector", "map_member_and_secretary.expected_row_values",
    )
    section = data["map_member_and_secretary"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    for member in section["members"]:
        page_obj.fill_mapping_form([
            {"type": "select_labels", "selector": section["employee_select"],
             "value": member["employee"]},
            {"type": "select_label", "selector": section["member_type_select"],
             "value": member["member_type"]},
            {"type": "fill", "selector": section["phone_field"], "value": member["phone"]},
            {"type": "fill", "selector": section["email_field"], "value": member["email"]},
        ])
        page_obj.submit(section["add_selector"])
    page_obj.click_guarded(section["map_selector"])
    expect(page.locator(section["success_selector"])).to_be_visible()
    page_obj.expect_texts_visible(section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_gb_map_outside_university(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-014: an Outside University expert is mapped as Member."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "outside_university.login", "outside_university.menu_path",
        "outside_university.filters", "outside_university.actions",
        "outside_university.add_selector", "outside_university.map_selector",
        "outside_university.success_selector", "outside_university.member_row",
        "outside_university.expected_row_values",
    )
    section = data["outside_university"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.map_member(
        section["actions"], section["add_selector"],
        section["map_selector"], section["success_selector"],
    )
    page_obj.expect_row_values(section["member_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_gb_delete_mapped_member(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-015: a mapped member can be deleted from the committee."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "delete_member.login", "delete_member.menu_path", "delete_member.filters",
        "delete_member.member_row", "delete_member.delete_action",
        "delete_member.confirm_selector", "delete_member.member_text",
    )
    section = data["delete_member"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.delete_mapped_member(
        section["member_row"], section["delete_action"], section["confirm_selector"]
    )
    page_obj.expect_row_absent(section["member_row"])
    page_obj.expect_absent(section["member_text"])


@pytest.mark.rnd
def test_rnd_gb_view_mapped_members(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-016: View Members to Committee displays every mapped member column."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "view_members.login", "view_members.menu_path", "view_members.committee_row",
        "view_members.view_action", "view_members.list_columns",
        "view_members.back_selector",
    )
    section = data["view_members"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_view_members(section["committee_row"], section["view_action"])
    page_obj.expect_list_columns(section["list_columns"])
    page_obj.click_control(section["back_selector"])
    expect(page.locator(section["committee_row"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_gb_edit_contact_details(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-017: a mapped member's phone number and email id are updated."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "edit_contact.login", "edit_contact.menu_path", "edit_contact.committee_row",
        "edit_contact.edit_action", "edit_contact.member_row", "edit_contact.actions",
        "edit_contact.save_selector", "edit_contact.success_selector",
        "view_members.view_action",
    )
    section = data["edit_contact"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_edit_members(section["committee_row"], section["edit_action"])
    page_obj.edit_contact_details(
        section["actions"], section["save_selector"], section["success_selector"]
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_view_members(
        section["committee_row"], data["view_members"]["view_action"]
    )
    updated = [str(action["value"]) for action in section["actions"]]
    page_obj.expect_row_values(section["member_row"], updated)


@pytest.mark.rnd
def test_rnd_gb_blank_employee_validation(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-018: Employee ID & Name left blank is rejected."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "blank_employee.login", "blank_employee.menu_path", "blank_employee.filters",
        "blank_employee.actions", "blank_employee.add_selector",
        "blank_employee.expected_message", "blank_employee.dialog_ok_selector",
        "blank_employee.no_row_check",
    )
    section = data["blank_employee"]
    login_as(section["login"])
    page_obj = _members(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.attempt_add_member(
        section["actions"], section["add_selector"], section["expected_message"]
    )
    page_obj.dismiss_validation_dialog(section["dialog_ok_selector"])
    page_obj.expect_row_absent(section["no_row_check"])


@pytest.mark.rnd
def test_rnd_gb_scholar_no_access(page, uucms_settings, login_as):
    """TC-GOVERNINGBODY-019: the Governing Bodies setup is not available to a Scholar."""
    data = _require_gb_data(
        load_test_data(DATA_FILE),
        "scholar_access.login", "scholar_access.menu_path",
    )
    section = data["scholar_access"]
    login_as(section["login"])
    menu = MenuPage(page, uucms_settings.timeout_ms)
    if menu.is_menu_visible(section["menu_path"]):
        _require_gb_data(data, "scholar_access.denied_message")
        menu.open_menu(section["menu_path"])
        expect(page.get_by_text(section["denied_message"])).to_be_visible()
