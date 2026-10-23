"""R&D Phase-1 FACULTYMAPPING test cases: Mapping of Area of Research to Faculty."""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.research_development.pages.admission.faculty_mapping_page import FacultyMappingPage
from uucms.modules.research_development.pages.admission.fee_payment_page import FeePaymentPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/faculty_mapping.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_faculty_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _open_faculty_list(page, uucms_settings, data,
                       filters=None, view_button=None) -> FacultyMappingPage:
    faculty_page = FacultyMappingPage(page, uucms_settings.timeout_ms)
    faculty_page.open_from_menu()
    faculty_page.apply_filters(filters if filters is not None else data["list"]["filters"])
    faculty_page.click_view(view_button or data["list"]["view_button"])
    return faculty_page


@pytest.mark.rnd
def test_rnd_faculty_mapping_list_and_discipline_rule(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-001: list with filters; discipline dropdown only shows disciplines with Areas of Research."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button", "list.list_columns", "list.row_actions",
        "discipline_rule.discipline_select", "discipline_rule.present", "discipline_rule.absent",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    faculty_page.expect_list_columns(data["list"]["list_columns"])
    faculty_page.expect_texts_visible(data["list"]["row_actions"])
    rule = data["discipline_rule"]
    faculty_page.expect_select_options(
        rule["discipline_select"], rule["present"], rule["absent"]
    )


@pytest.mark.rnd
def test_rnd_faculty_mapping_academic_year_required(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-002: Academic Year is required before the list loads."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "academic_year_required.partial_filters", "academic_year_required.view_button",
        "academic_year_required.list_selector", "academic_year_required.required_mark",
    )
    required = data["academic_year_required"]
    faculty_page = _open_faculty_list(
        authenticated_page, uucms_settings, data,
        filters=required["partial_filters"], view_button=required["view_button"],
    )
    faculty_page.expect_list_not_loaded(required["list_selector"])
    expect(authenticated_page.locator(required["required_mark"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_faculty_mapping_guide_happy_path(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-003: map an Area of Research to a faculty member as Guide."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "map_guide.map_action", "map_guide.actions", "map_guide.add_row_button",
        "map_guide.submit_button", "map_guide.success_selector",
        "map_guide.expected_row_values",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    mapping = data["map_guide"]
    faculty_page.open_list_action(mapping["map_action"])
    faculty_page.fill_mapping_form(mapping["actions"])
    faculty_page.click_control(mapping["add_row_button"])
    faculty_page.submit_mapping(mapping["submit_button"], mapping["success_selector"])
    faculty_page.expect_mapped_rows(mapping["expected_row_values"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_teaching_staff_only(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-004: employee dropdown lists only Teaching Staff of the department."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "teaching_staff_only.map_action", "teaching_staff_only.faculty_type_select",
        "teaching_staff_only.faculty_type", "teaching_staff_only.department_select",
        "teaching_staff_only.department", "teaching_staff_only.employee_select",
        "teaching_staff_only.present", "teaching_staff_only.absent",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    case = data["teaching_staff_only"]
    faculty_page.open_list_action(case["map_action"])
    faculty_page.execute_actions([
        {"type": "select_label", "selector": case["faculty_type_select"], "value": case["faculty_type"]},
        {"type": "select_label", "selector": case["department_select"], "value": case["department"]},
    ])
    faculty_page.expect_select_options(
        case["employee_select"], case["present"], case["absent"]
    )


@pytest.mark.rnd
def test_rnd_faculty_mapping_department_limited_to_discipline(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-005: department dropdown is limited to departments mapped to the discipline."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "department_limit.map_action", "department_limit.aor_select", "department_limit.aor",
        "department_limit.department_select",
        "department_limit.present", "department_limit.absent",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    case = data["department_limit"]
    faculty_page.open_list_action(case["map_action"])
    faculty_page.execute_actions([
        {"type": "select_label", "selector": case["aor_select"], "value": case["aor"]},
    ])
    faculty_page.expect_select_options(
        case["department_select"], case["present"], case["absent"]
    )


@pytest.mark.rnd
def test_rnd_faculty_mapping_multi_select_employees(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-006: multi-select Research Faculty Type and multiple employee rows."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "map_multi.map_action", "map_multi.aor_select", "map_multi.aor",
        "map_multi.department_select", "map_multi.department",
        "map_multi.employee_select", "map_multi.research_type_select",
        "map_multi.add_row_button", "map_multi.submit_button",
        "map_multi.success_selector", "map_multi.employees",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    case = data["map_multi"]
    faculty_page.open_list_action(case["map_action"])
    actions = [
        {"type": "select_label", "selector": case["aor_select"], "value": case["aor"]},
        {"type": "select_label", "selector": case["department_select"], "value": case["department"]},
    ]
    for employee in case["employees"]:
        actions.append(
            {"type": "select_label", "selector": case["employee_select"], "value": employee["employee"]}
        )
        actions.append(
            {"type": "multiselect_labels", "selector": case["research_type_select"], "value": employee["types"]}
        )
        actions.append({"type": "click", "selector": case["add_row_button"]})
    faculty_page.fill_mapping_form(actions)
    faculty_page.submit_mapping(case["submit_button"], case["success_selector"])
    for employee in case["employees"]:
        expect(authenticated_page.get_by_text(employee["employee"])).to_be_visible()
        for type_label in [item.strip() for item in str(employee["types"]).split(",")]:
            expect(authenticated_page.get_by_text(type_label, exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_faculty_mapping_view_mapped_by_code(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-007: view mapped Areas of Research to Faculties by multi-selected codes."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "view_mapped.view_mapped_action", "view_mapped.code_actions",
        "view_mapped.view_button", "view_mapped.list_columns",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    view = data["view_mapped"]
    faculty_page.open_list_action(view["view_mapped_action"])
    faculty_page.select_area_codes(view["code_actions"])
    faculty_page.click_view(view["view_button"])
    faculty_page.expect_list_columns(view["list_columns"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_print_mapped(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-008: print provision for the mapped Areas of Research to Faculties list."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "print.view_mapped_action", "print.code_actions", "print.view_button",
        "print.print_button", "print.print_view_selector",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    print_case = data["print"]
    faculty_page.open_list_action(print_case["view_mapped_action"])
    faculty_page.select_area_codes(print_case["code_actions"])
    faculty_page.click_view(print_case["view_button"])
    faculty_page.click_print(print_case["print_button"], print_case["print_view_selector"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_modify_delete(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-009: modify mapped faculty - deletion of an eligible mapping succeeds."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "modify_delete.modify_action", "modify_delete.mapping_row",
        "modify_delete.delete_action", "modify_delete.confirm_selector",
        "modify_delete.submit_button",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    modify = data["modify_delete"]
    faculty_page.open_list_action(modify["modify_action"])
    faculty_page.delete_mapping(
        modify["mapping_row"], modify["delete_action"],
        modify["confirm_selector"], modify["submit_button"],
    )
    faculty_page.expect_mapping_removed(modify["mapping_row"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_delete_blocked_student(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-010: deletion blocked when the employee is guide/co-guide to a student."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "delete_blocked_student.modify_action", "delete_blocked_student.mapping_row",
        "delete_blocked_student.delete_action", "delete_blocked_student.expected_message",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    blocked = data["delete_blocked_student"]
    faculty_page.open_list_action(blocked["modify_action"])
    faculty_page.attempt_delete_blocked(
        blocked["mapping_row"], blocked["delete_action"], blocked["expected_message"]
    )
    faculty_page.expect_mapping_still_present(blocked["mapping_row"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_delete_blocked_project(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-011: deletion blocked when the employee is PI/mentor to a project."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "delete_blocked_project.modify_action", "delete_blocked_project.mapping_row",
        "delete_blocked_project.delete_action", "delete_blocked_project.expected_message",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    blocked = data["delete_blocked_project"]
    faculty_page.open_list_action(blocked["modify_action"])
    faculty_page.attempt_delete_blocked(
        blocked["mapping_row"], blocked["delete_action"], blocked["expected_message"]
    )
    faculty_page.expect_mapping_still_present(blocked["mapping_row"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_back_discards_draft(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-012: Back discards a faculty mapping draft."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.view_button",
        "back_discards.map_action", "back_discards.aor_select", "back_discards.aor",
        "back_discards.employee_select", "back_discards.employee",
        "back_discards.back_button", "back_discards.list_selector",
    )
    faculty_page = _open_faculty_list(authenticated_page, uucms_settings, data)
    back = data["back_discards"]
    faculty_page.open_list_action(back["map_action"])
    faculty_page.execute_actions([
        {"type": "select_label", "selector": back["aor_select"], "value": back["aor"]},
        {"type": "select_label", "selector": back["employee_select"], "value": back["employee"]},
    ])
    faculty_page.back_discards_draft(back["back_button"], back["list_selector"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_fee_invitation_allowed(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-013: online fee payment invitation sent when AoR and guide mapping is complete."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "fee_invitation_allowed.student_row", "fee_invitation_allowed.invitation_action",
        "fee_invitation_allowed.send_button", "fee_invitation_allowed.success_selector",
    )
    fee_page = FeePaymentPage(authenticated_page, uucms_settings.timeout_ms)
    fee_page.open_online_fee_invitation()
    case = data["fee_invitation_allowed"]
    fee_page.open_student_screen(case["student_row"], case["invitation_action"])
    fee_page.send_invitation(case["send_button"], case["success_selector"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_fee_invitation_blocked(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-014: online fee payment invitation not allowed before AoR mapping is complete."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "fee_invitation_blocked.student_row", "fee_invitation_blocked.invitation_action",
        "fee_invitation_blocked.send_button", "fee_invitation_blocked.expected_message",
    )
    fee_page = FeePaymentPage(authenticated_page, uucms_settings.timeout_ms)
    fee_page.open_online_fee_invitation()
    case = data["fee_invitation_blocked"]
    fee_page.open_student_screen(case["student_row"], case["invitation_action"])
    fee_page.expect_invitation_blocked(case["send_button"], case["expected_message"])


@pytest.mark.rnd
def test_rnd_faculty_mapping_offline_payment_blocked(authenticated_page, uucms_settings):
    """TC-FACULTYMAPPING-015: offline payment approval blocked before AoR mapping is complete."""
    data = _require_faculty_data(
        load_test_data(DATA_FILE),
        "offline_payment_blocked.student_row", "offline_payment_blocked.approval_action",
        "offline_payment_blocked.approve_button", "offline_payment_blocked.expected_message",
        "offline_payment_blocked.unapproved_status",
    )
    fee_page = FeePaymentPage(authenticated_page, uucms_settings.timeout_ms)
    fee_page.open_offline_payment_approval()
    case = data["offline_payment_blocked"]
    fee_page.open_student_screen(case["student_row"], case["approval_action"])
    fee_page.expect_payment_approval_blocked(case["approve_button"], case["expected_message"])
    fee_page.expect_row_text(case["student_row"], case["unapproved_status"])
