"""R&D Phase-2 SPECIALREQUEST test cases.

Allocation/change requests (guide change, co-guide allocation/change,
special circumstances, mode of study, maternity leave, extensions)
raised by the student and reviewed by the Department Chairperson /
Doctoral Committee Chairperson, including the online fee step and the
vacancy-matrix seat lock.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.requests.guide_change_page import GuideChangePage
from uucms.modules.research_development.pages.special_request.special_request_review_page import SpecialRequestReviewPage
from uucms.modules.research_development.pages.special_request.special_requests_page import SpecialRequestsPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/special_requests.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_sr_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _requests_page(page, uucms_settings) -> SpecialRequestsPage:
    return SpecialRequestsPage(page, uucms_settings.timeout_ms)


def _wizard(page, uucms_settings) -> GuideChangePage:
    return GuideChangePage(page, uucms_settings.timeout_ms)


def _review_page(page, uucms_settings) -> SpecialRequestReviewPage:
    return SpecialRequestReviewPage(page, uucms_settings.timeout_ms)


def _open_list(page, uucms_settings, section) -> SpecialRequestsPage:
    page_obj = _requests_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


def _open_wizard(page, uucms_settings, section):
    """Log-in-independent helper: open the Add New Request wizard."""
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_add_request(section["add_action"])
    return page_obj, _wizard(page, uucms_settings)


def _detail_actions(section) -> list[dict]:
    """Reason + supporting document actions for the wizard first step."""
    actions = []
    if section.get("reason_field") and section.get("reason") is not None:
        actions.append({"type": "fill", "selector": section["reason_field"],
                        "value": section["reason"]})
    for key, action_type in (("from_date_field", "fill"),
                             ("to_date_field", "fill"),
                             ("new_end_date_field", "fill"),
                             ("updated_projected_year_field", "fill")):
        if section.get(key):
            value_key = key.replace("_field", "")
            actions.append({"type": action_type, "selector": section[key],
                            "value": section[value_key]})
    if section.get("document_input") and section.get("document"):
        actions.append({"type": "upload", "selector": section["document_input"],
                        "value": section["document"]})
    return actions


def _pay_fee(page, uucms_settings, section, pay_fee) -> None:
    """Advance to the Online Fee Details step and complete the payment."""
    wizard = _wizard(page, uucms_settings)
    if pay_fee.get("next_selector"):
        wizard.proceed_next(pay_fee["next_selector"])
    if pay_fee.get("expected_amount") and pay_fee.get("fee_amount_field"):
        wizard.expect_fee_amount(pay_fee["fee_amount_field"],
                                 pay_fee["expected_amount"])
    wizard.pay_fees(pay_fee["pay_selector"], pay_fee.get("payment_actions"),
                    pay_fee.get("payment_success_selector"))


def _wizard_wizard_actions(section) -> list[dict]:
    actions = []
    if section.get("mode_select") and section.get("mode"):
        actions.append({"type": "select_label", "selector": section["mode_select"],
                        "value": section["mode"]})
    actions.extend(_detail_actions(section))
    return actions


@pytest.mark.rnd
def test_rnd_sr_my_submitted_requests_list(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-001: the student views their submitted special requests."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "student_list.login", "student_list.menu_path", "student_list.filters",
        "student_list.view_button", "student_list.list_columns",
        "student_list.add_new_request_action",
    )
    section = data["student_list"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.view_my_requests(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])
    expect(page.locator(section["add_new_request_action"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_raise_guide_change(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-002: a Request for Guide Change is raised up to the faculty step."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "raise_guide_change.login", "raise_guide_change.menu_path",
        "raise_guide_change.filters", "raise_guide_change.add_action",
        "raise_guide_change.student_details",
        "raise_guide_change.request_type_select", "raise_guide_change.request_type",
        "raise_guide_change.reason_field", "raise_guide_change.reason",
        "raise_guide_change.document_input", "raise_guide_change.document",
        "raise_guide_change.next_selector", "raise_guide_change.success_selector",
        "raise_guide_change.preferred_faculty_heading",
    )
    section = data["raise_guide_change"]
    login_as(section["login"])
    page_obj, wizard = _open_wizard(page, uucms_settings, section)
    wizard.expect_student_details(section["student_details"])
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    expect(page.locator(section["success_selector"])).to_be_visible()
    expect(page.get_by_text(section["preferred_faculty_heading"],
                            exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_special_circumstance_list(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-003: the Special Circumstance list loads only for the two special-circumstance types."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "special_circumstance_types.login", "special_circumstance_types.menu_path",
        "special_circumstance_types.filters", "special_circumstance_types.add_action",
        "special_circumstance_types.request_type_select",
        "special_circumstance_types.special_circumstance_select",
        "special_circumstance_types.request_types",
        "special_circumstance_types.expected_options",
    )
    section = data["special_circumstance_types"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    for request_type in section["request_types"]:
        wizard.choose_request_type(section["request_type_select"], request_type)
        wizard.expect_special_circumstance_options(
            section["special_circumstance_select"], section["expected_options"]
        )


@pytest.mark.rnd
def test_rnd_sr_no_special_circumstance_normal_types(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-004: no Special Circumstance field for normal request types."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "no_special_circumstance.login", "no_special_circumstance.menu_path",
        "no_special_circumstance.filters", "no_special_circumstance.add_action",
        "no_special_circumstance.request_type_select",
        "no_special_circumstance.request_type",
        "no_special_circumstance.special_circumstance_select",
    )
    section = data["no_special_circumstance"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.expect_special_circumstance_absent(
        section["special_circumstance_select"]
    )


@pytest.mark.rnd
def test_rnd_sr_preferred_faculty_vacancy_matrix(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-005: preferred faculty are filtered by the vacancy matrix of the student category."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "preferred_faculty_vacancy.login", "preferred_faculty_vacancy.menu_path",
        "preferred_faculty_vacancy.filters", "preferred_faculty_vacancy.add_action",
        "preferred_faculty_vacancy.request_type_select",
        "preferred_faculty_vacancy.request_type",
        "preferred_faculty_vacancy.reason_field", "preferred_faculty_vacancy.reason",
        "preferred_faculty_vacancy.next_selector",
        "preferred_faculty_vacancy.list_columns",
        "preferred_faculty_vacancy.present", "preferred_faculty_vacancy.absent",
    )
    section = data["preferred_faculty_vacancy"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.expect_preferred_faculty_columns(section["list_columns"])
    wizard.expect_preferred_faculty(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_sr_coguide_vacancy_matrix(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-006: co-guide candidates use the guide's vacancy matrix."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "coguide_vacancy_matrix.login", "coguide_vacancy_matrix.menu_path",
        "coguide_vacancy_matrix.filters", "coguide_vacancy_matrix.add_action",
        "coguide_vacancy_matrix.request_type_select",
        "coguide_vacancy_matrix.request_type",
        "coguide_vacancy_matrix.reason_field", "coguide_vacancy_matrix.reason",
        "coguide_vacancy_matrix.next_selector",
        "coguide_vacancy_matrix.present", "coguide_vacancy_matrix.absent",
    )
    section = data["coguide_vacancy_matrix"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.expect_preferred_faculty(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_sr_existing_guide_excluded(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-007: the existing guide is not offered in a Guide Change request."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "existing_guide_excluded.login", "existing_guide_excluded.menu_path",
        "existing_guide_excluded.filters", "existing_guide_excluded.add_action",
        "existing_guide_excluded.request_type_select",
        "existing_guide_excluded.request_type",
        "existing_guide_excluded.reason_field", "existing_guide_excluded.reason",
        "existing_guide_excluded.next_selector",
        "existing_guide_excluded.present", "existing_guide_excluded.absent",
    )
    section = data["existing_guide_excluded"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.expect_preferred_faculty(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_sr_preferred_faculty_aor_limited(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-008: preferred faculty are limited to the student's area of research."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "aor_limited_faculty.login", "aor_limited_faculty.menu_path",
        "aor_limited_faculty.filters", "aor_limited_faculty.add_action",
        "aor_limited_faculty.request_type_select",
        "aor_limited_faculty.request_type",
        "aor_limited_faculty.reason_field", "aor_limited_faculty.reason",
        "aor_limited_faculty.next_selector",
        "aor_limited_faculty.present", "aor_limited_faculty.absent",
    )
    section = data["aor_limited_faculty"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.expect_preferred_faculty(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_sr_research_faculty_type_loaded(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-009: preferred faculty load per research faculty type of the request."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "research_faculty_type.login", "research_faculty_type.menu_path",
        "research_faculty_type.filters", "research_faculty_type.add_action",
        "research_faculty_type.request_type_select",
        "research_faculty_type.reason_field", "research_faculty_type.reason",
        "research_faculty_type.next_selector",
        "research_faculty_type.research_faculty_type_cells",
        "research_faculty_type.guide_change",
        "research_faculty_type.coguide_allocation",
    )
    section = data["research_faculty_type"]
    login_as(section["login"])
    for key in ("guide_change", "coguide_allocation"):
        entry = section[key]
        _, wizard = _open_wizard(page, uucms_settings, section)
        wizard.choose_request_type(section["request_type_select"],
                                   entry["request_type"])
        wizard.enter_request_details(_detail_actions(section))
        wizard.proceed_next(section["next_selector"])
        types = wizard.collect_research_faculty_types(
            section["research_faculty_type_cells"]
        )
        assert set(types) == set(entry["expected_types"]), (
            f"Research Faculty Type values for {entry['request_type']} are "
            f"{types}, expected exactly {entry['expected_types']}"
        )


@pytest.mark.rnd
def test_rnd_sr_online_fee_payment(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-010: the configured fee is paid online and the request is submitted."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "online_fee_payment.login", "online_fee_payment.menu_path",
        "online_fee_payment.filters", "online_fee_payment.add_action",
        "online_fee_payment.request_type_select",
        "online_fee_payment.request_type",
        "online_fee_payment.reason_field", "online_fee_payment.reason",
        "online_fee_payment.document_input", "online_fee_payment.document",
        "online_fee_payment.next_selector",
        "online_fee_payment.faculty_select", "online_fee_payment.faculty",
        "online_fee_payment.fee_amount_field", "online_fee_payment.expected_amount",
        "online_fee_payment.pay_selector", "online_fee_payment.payment_actions",
        "online_fee_payment.payment_success_selector",
        "online_fee_payment.request_row", "online_fee_payment.amount_paid",
    )
    section = data["online_fee_payment"]
    login_as(section["login"])
    page_obj, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.execute_actions([
        {"type": "select_label", "selector": section["faculty_select"],
         "value": section["faculty"]},
    ])
    wizard.expect_fee_amount(section["fee_amount_field"],
                             section["expected_amount"])
    wizard.pay_fees(section["pay_selector"], section["payment_actions"],
                    section["payment_success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_text(section["request_row"], section["amount_paid"])


@pytest.mark.rnd
def test_rnd_sr_no_offline_payment(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-011: only online fee payment is offered for these requests."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "no_offline_payment.login", "no_offline_payment.menu_path",
        "no_offline_payment.filters", "no_offline_payment.add_action",
        "no_offline_payment.request_type_select",
        "no_offline_payment.request_type",
        "no_offline_payment.reason_field", "no_offline_payment.reason",
        "no_offline_payment.next_selector",
        "no_offline_payment.faculty_select", "no_offline_payment.faculty",
        "no_offline_payment.offline_option_selector",
    )
    section = data["no_offline_payment"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.execute_actions([
        {"type": "select_label", "selector": section["faculty_select"],
         "value": section["faculty"]},
    ])
    wizard.expect_no_offline_payment(section["offline_option_selector"])


@pytest.mark.rnd
def test_rnd_sr_vacancy_seat_lock(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-012: the vacancy matrix seat locks on request and releases on cancellation."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "vacancy_seat_lock.matrix.login", "vacancy_seat_lock.matrix.menu_path",
        "vacancy_seat_lock.matrix.filters", "vacancy_seat_lock.matrix.faculty_row",
        "vacancy_seat_lock.matrix.seat_cell", "vacancy_seat_lock.matrix.original_seats",
        "vacancy_seat_lock.login", "vacancy_seat_lock.menu_path",
        "vacancy_seat_lock.filters", "vacancy_seat_lock.add_action",
        "vacancy_seat_lock.request_type_select", "vacancy_seat_lock.request_type",
        "vacancy_seat_lock.reason_field", "vacancy_seat_lock.reason",
        "vacancy_seat_lock.document_input", "vacancy_seat_lock.document",
        "vacancy_seat_lock.next_selector",
        "vacancy_seat_lock.faculty_select", "vacancy_seat_lock.faculty",
        "vacancy_seat_lock.pay_selector", "vacancy_seat_lock.payment_actions",
        "vacancy_seat_lock.payment_success_selector",
        "vacancy_seat_lock.request_row", "vacancy_seat_lock.release_action",
        "vacancy_seat_lock.release_confirm_selector",
    )
    matrix = data["vacancy_seat_lock"]["matrix"]
    section = data["vacancy_seat_lock"]
    original = int(str(matrix["original_seats"]).strip())

    def read_seats() -> int:
        login_as(matrix["login"])
        page_obj = _requests_page(page, uucms_settings)
        page_obj.open_from_menu(matrix["menu_path"])
        page_obj.apply_filters(matrix["filters"])
        page_obj.find_row(matrix["faculty_row"])
        return int(page_obj.read_cell_text(matrix["seat_cell"]))

    assert read_seats() == original, "Starting seat count differs from the test data"

    login_as(section["login"])
    page_obj, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    wizard.proceed_next(section["next_selector"])
    wizard.execute_actions([
        {"type": "select_label", "selector": section["faculty_select"],
         "value": section["faculty"]},
    ])
    wizard.pay_fees(section["pay_selector"], section["payment_actions"],
                    section["payment_success_selector"])

    assert read_seats() == original - 1, "Seat was not locked after the request"

    login_as(section["login"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.release_request(
        section["request_row"], section["release_action"],
        section["release_confirm_selector"],
    )
    assert read_seats() == original, "Seat was not released after cancellation"


@pytest.mark.rnd
def test_rnd_sr_existing_coguide_display(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-013: the existing co-guide is shown only when previously allocated."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "existing_coguide_display.student_a.login",
        "existing_coguide_display.student_a.menu_path",
        "existing_coguide_display.student_a.filters",
        "existing_coguide_display.student_a.add_action",
        "existing_coguide_display.student_a.request_type_select",
        "existing_coguide_display.student_a.request_type",
        "existing_coguide_display.student_a.coguide_field",
        "existing_coguide_display.student_a.coguide_name",
        "existing_coguide_display.student_b.login",
        "existing_coguide_display.student_b.menu_path",
        "existing_coguide_display.student_b.filters",
        "existing_coguide_display.student_b.add_action",
        "existing_coguide_display.student_b.request_type_select",
        "existing_coguide_display.student_b.request_type",
        "existing_coguide_display.student_b.coguide_field",
    )
    student_a = data["existing_coguide_display"]["student_a"]
    login_as(student_a["login"])
    _, wizard = _open_wizard(page, uucms_settings, student_a)
    wizard.choose_request_type(student_a["request_type_select"],
                               student_a["request_type"])
    _requests_page(page, uucms_settings).expect_field_visible(
        student_a["coguide_field"], student_a["coguide_name"]
    )

    student_b = data["existing_coguide_display"]["student_b"]
    login_as(student_b["login"])
    page_obj_b = _open_list(page, uucms_settings, student_b)
    page_obj_b.open_add_request(student_b["add_action"])
    _wizard(page, uucms_settings).choose_request_type(
        student_b["request_type_select"], student_b["request_type"]
    )
    requests_page.expect_field_absent(student_b["coguide_field"])


@pytest.mark.rnd
def test_rnd_sr_reason_required(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-014: Reason for your request is mandatory."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "reason_required.login", "reason_required.menu_path",
        "reason_required.filters", "reason_required.add_action",
        "reason_required.request_type_select", "reason_required.request_type",
        "reason_required.next_selector", "reason_required.expected_message",
    )
    section = data["reason_required"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.attempt_proceed_next(section["next_selector"],
                                section["expected_message"])


@pytest.mark.rnd
def test_rnd_sr_request_type_required(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-015: Choose Request Type is mandatory."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "request_type_required.login", "request_type_required.menu_path",
        "request_type_required.filters", "request_type_required.add_action",
        "request_type_required.next_selector",
        "request_type_required.expected_message",
    )
    section = data["request_type_required"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.attempt_proceed_next(section["next_selector"],
                                section["expected_message"])


@pytest.mark.rnd
def test_rnd_sr_duplicate_pending_prevented(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-016: a second pending request of the same type is prevented."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "duplicate_pending.login", "duplicate_pending.menu_path",
        "duplicate_pending.filters", "duplicate_pending.add_action",
        "duplicate_pending.request_type_select", "duplicate_pending.request_type",
        "duplicate_pending.next_selector", "duplicate_pending.expected_message",
    )
    section = data["duplicate_pending"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.attempt_proceed_next(section["next_selector"],
                                section["expected_message"])


@pytest.mark.rnd
def test_rnd_sr_chairperson_list(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-017: the Department Chairperson views all student requests."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "chairperson_list.login", "chairperson_list.menu_path",
        "chairperson_list.filters", "chairperson_list.view_button",
        "chairperson_list.list_columns",
    )
    section = data["chairperson_list"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.view_students_list(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])


@pytest.mark.rnd
def test_rnd_sr_dcc_list(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-018: the Doctoral Committee Chairperson views the same request list."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "dcc_list.login", "dcc_list.menu_path", "dcc_list.filters",
        "dcc_list.view_button", "dcc_list.list_columns",
    )
    section = data["dcc_list"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.view_students_list(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])


@pytest.mark.rnd
def test_rnd_sr_chairperson_review_screen(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-019: the chairperson review screen shows details, faculty list and fees."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "chairperson_review.login", "chairperson_review.menu_path",
        "chairperson_review.filters", "chairperson_review.request_row",
        "chairperson_review.view_action", "chairperson_review.student_details",
        "chairperson_review.sections",
        "chairperson_review.document_view_selector",
        "chairperson_review.document_download_selector",
        "chairperson_review.preferred_faculty_columns",
        "chairperson_review.preference_approve_action",
        "chairperson_review.fee_paid_status", "chairperson_review.remarks_field",
        "chairperson_review.approve_selector", "chairperson_review.reject_selector",
    )
    section = data["chairperson_review"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_student_details(section["student_details"])
    review.expect_review_sections(section["sections"])
    review.expect_document_available(
        section["document_view_selector"], section["document_download_selector"]
    )
    review.expect_preferred_faculty_columns(section["preferred_faculty_columns"])
    expect(page.locator(section["preference_approve_action"])).to_be_visible()
    review.expect_fee_paid_status(section["fee_paid_status"])
    expect(page.locator(section["remarks_field"])).to_be_visible()
    expect(page.locator(section["approve_selector"])).to_be_visible()
    expect(page.locator(section["reject_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_chairperson_approves_guide_change(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-020: the chairperson approves the Guide Change; the faculty is allocated."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "chairperson_approves.login", "chairperson_approves.menu_path",
        "chairperson_approves.filters", "chairperson_approves.request_row",
        "chairperson_approves.view_action", "chairperson_approves.approve_selector",
        "chairperson_approves.success_selector",
        "chairperson_approves.approved_status",
        "chairperson_approves.allocation_check_selector",
        "chairperson_approves.allocated_guide",
    )
    section = data["chairperson_approves"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.approve(section["approve_selector"], section["success_selector"])
    review.expect_request_status(section["approved_status"])
    review.expect_allocated_guide(section["allocation_check_selector"],
                                  section["allocated_guide"])


@pytest.mark.rnd
def test_rnd_sr_chairperson_rejects(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-021: the chairperson rejects the request with remarks."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "chairperson_rejects.login", "chairperson_rejects.menu_path",
        "chairperson_rejects.filters", "chairperson_rejects.request_row",
        "chairperson_rejects.view_action", "chairperson_rejects.remarks_field",
        "chairperson_rejects.reject_remarks", "chairperson_rejects.reject_selector",
        "chairperson_rejects.success_selector",
        "chairperson_rejects.rejected_status",
    )
    section = data["chairperson_rejects"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.reject(section["remarks_field"], section["reject_remarks"],
                  section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_request_status(section["request_row"],
                                   section["rejected_status"])


@pytest.mark.rnd
def test_rnd_sr_approve_specific_faculty(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-022: only the chosen preferred faculty is allocated."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "approve_specific_faculty.login", "approve_specific_faculty.menu_path",
        "approve_specific_faculty.filters", "approve_specific_faculty.request_row",
        "approve_specific_faculty.view_action", "approve_specific_faculty.faculties",
        "approve_specific_faculty.faculty_rows", "approve_specific_faculty.approves_index",
        "approve_specific_faculty.preference_approve_action",
        "approve_specific_faculty.success_selector",
        "approve_specific_faculty.allocation_check_selector",
        "approve_specific_faculty.allocated_faculty",
        "approve_specific_faculty.not_allocated_faculties",
    )
    section = data["approve_specific_faculty"]
    index = int(section["approves_index"])
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.approve_faculty(section["faculty_rows"][index],
                           section["preference_approve_action"],
                           section["success_selector"])
    review.expect_allocated_guide(section["allocation_check_selector"],
                                  section["allocated_faculty"])
    review.expect_not_allocated(section["allocation_check_selector"],
                                section["not_allocated_faculties"])


@pytest.mark.rnd
def test_rnd_sr_mode_of_study_request(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-023: a mode of study change request is submitted with the fee paid."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "mode_of_study.login", "mode_of_study.menu_path", "mode_of_study.filters",
        "mode_of_study.add_action", "mode_of_study.request_type_select",
        "mode_of_study.request_type", "mode_of_study.mode_select",
        "mode_of_study.mode", "mode_of_study.expected_modes",
        "mode_of_study.reason_field", "mode_of_study.reason",
        "mode_of_study.pay_fee.next_selector",
        "mode_of_study.pay_fee.fee_amount_field",
        "mode_of_study.pay_fee.expected_amount",
        "mode_of_study.pay_fee.pay_selector",
        "mode_of_study.pay_fee.payment_actions",
        "mode_of_study.pay_fee.payment_success_selector",
    )
    section = data["mode_of_study"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    requests_page = _requests_page(page, uucms_settings)
    modes = requests_page.collect_select_options(section["mode_select"])
    assert set(modes) == set(section["expected_modes"]), (
        f"Mode of study options differ from the documented set: {modes}"
    )
    wizard.execute_actions([
        {"type": "select_label", "selector": section["mode_select"],
         "value": section["mode"]},
    ])
    wizard.enter_request_details(_detail_actions(section))
    _pay_fee(page, uucms_settings, section, section["pay_fee"])


@pytest.mark.rnd
def test_rnd_sr_mode_of_study_review(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-024: the chairperson reviews and approves the mode of study request."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "mode_of_study_review.login", "mode_of_study_review.menu_path",
        "mode_of_study_review.filters", "mode_of_study_review.request_row",
        "mode_of_study_review.view_action", "mode_of_study_review.mode_requested_field",
        "mode_of_study_review.mode_requested",
        "mode_of_study_review.document_view_selector",
        "mode_of_study_review.document_download_selector",
        "mode_of_study_review.fee_paid_status", "mode_of_study_review.remarks_field",
        "mode_of_study_review.approve_remarks", "mode_of_study_review.approve_selector",
        "mode_of_study_review.success_selector", "mode_of_study_review.approved_status",
    )
    section = data["mode_of_study_review"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_field_value(section["mode_requested_field"],
                              section["mode_requested"])
    review.expect_document_available(
        section["document_view_selector"], section["document_download_selector"]
    )
    review.expect_fee_paid_status(section["fee_paid_status"])
    review.fill_field(section["remarks_field"], section["approve_remarks"])
    review.approve(section["approve_selector"], section["success_selector"])
    review.expect_request_status(section["approved_status"])


@pytest.mark.rnd
def test_rnd_sr_maternity_leave_female_visible(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-025: Maternity Leave is offered to the female scholar."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "maternity_leave_visibility.female_scholar.login",
        "maternity_leave_visibility.female_scholar.menu_path",
        "maternity_leave_visibility.female_scholar.filters",
        "maternity_leave_visibility.female_scholar.add_action",
        "maternity_leave_visibility.female_scholar.request_type_select",
        "maternity_leave_visibility.female_scholar.present",
    )
    section = data["maternity_leave_visibility"]["female_scholar"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_add_request(section["add_action"])
    page_obj.expect_request_types(section["request_type_select"],
                                  section["present"], [])


@pytest.mark.rnd
def test_rnd_sr_maternity_leave_male_absent(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-026: Maternity Leave is not offered to the male scholar."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "maternity_leave_visibility.male_scholar.login",
        "maternity_leave_visibility.male_scholar.menu_path",
        "maternity_leave_visibility.male_scholar.filters",
        "maternity_leave_visibility.male_scholar.add_action",
        "maternity_leave_visibility.male_scholar.request_type_select",
        "maternity_leave_visibility.male_scholar.absent",
    )
    section = data["maternity_leave_visibility"]["male_scholar"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_add_request(section["add_action"])
    page_obj.expect_request_types(section["request_type_select"], [],
                                  section["absent"])


@pytest.mark.rnd
def test_rnd_sr_maternity_leave_request(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-027: a Maternity Leave request with From/To dates is submitted and reviewed."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "maternity_leave_request.login", "maternity_leave_request.menu_path",
        "maternity_leave_request.filters", "maternity_leave_request.add_action",
        "maternity_leave_request.request_type_select",
        "maternity_leave_request.request_type",
        "maternity_leave_request.from_date_field", "maternity_leave_request.from_date",
        "maternity_leave_request.to_date_field", "maternity_leave_request.to_date",
        "maternity_leave_request.reason_field", "maternity_leave_request.reason",
        "maternity_leave_request.document_input", "maternity_leave_request.document",
        "maternity_leave_request.pay_fee.next_selector",
        "maternity_leave_request.pay_fee.fee_amount_field",
        "maternity_leave_request.pay_fee.expected_amount",
        "maternity_leave_request.pay_fee.pay_selector",
        "maternity_leave_request.pay_fee.payment_actions",
        "maternity_leave_request.pay_fee.payment_success_selector",
        "maternity_leave_request.chairperson.login",
        "maternity_leave_request.chairperson.menu_path",
        "maternity_leave_request.chairperson.filters",
        "maternity_leave_request.chairperson.request_row",
        "maternity_leave_request.chairperson.view_action",
        "maternity_leave_request.chairperson.from_date_label",
        "maternity_leave_request.chairperson.to_date_label",
        "maternity_leave_request.chairperson.approve_selector",
        "maternity_leave_request.chairperson.reject_selector",
        "maternity_leave_request.chairperson.remarks_field",
    )
    section = data["maternity_leave_request"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    _pay_fee(page, uucms_settings, section, section["pay_fee"])

    chair = section["chairperson"]
    login_as(chair["login"])
    page_obj = _open_list(page, uucms_settings, chair)
    page_obj.open_request_details(chair["request_row"], chair["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections([chair["from_date_label"], chair["to_date_label"]])
    expect(page.get_by_text(section["from_date"])).to_be_visible()
    expect(page.get_by_text(section["to_date"])).to_be_visible()
    expect(page.locator(chair["approve_selector"])).to_be_visible()
    expect(page.locator(chair["reject_selector"])).to_be_visible()
    expect(page.locator(chair["remarks_field"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_no_submission_during_leave(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-028: synopsis/progress report submission is blocked during approved leave."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "no_submission_during_leave.login",
        "no_submission_during_leave.synopsis_menu_path",
        "no_submission_during_leave.synopsis_row",
        "no_submission_during_leave.synopsis_submit_action",
        "no_submission_during_leave.progress_menu_path",
        "no_submission_during_leave.progress_row",
        "no_submission_during_leave.progress_submit_action",
    )
    section = data["no_submission_during_leave"]
    login_as(section["login"])
    page_obj = _requests_page(page, uucms_settings)
    page_obj.open_from_menu(section["synopsis_menu_path"])
    page_obj.expect_action_not_available(section["synopsis_row"],
                                         section["synopsis_submit_action"])
    page_obj.open_from_menu(section["progress_menu_path"])
    page_obj.expect_action_not_available(section["progress_row"],
                                         section["progress_submit_action"])


@pytest.mark.rnd
def test_rnd_sr_maternity_leave_6plus_approved(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-029: a 6+ months leave is approved within the Double Duration."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "maternity_leave_6plus.student.login",
        "maternity_leave_6plus.student.menu_path",
        "maternity_leave_6plus.student.filters",
        "maternity_leave_6plus.student.add_action",
        "maternity_leave_6plus.student.request_type_select",
        "maternity_leave_6plus.student.request_type",
        "maternity_leave_6plus.student.from_date_field",
        "maternity_leave_6plus.student.from_date",
        "maternity_leave_6plus.student.to_date_field",
        "maternity_leave_6plus.student.to_date",
        "maternity_leave_6plus.student.reason_field",
        "maternity_leave_6plus.student.reason",
        "maternity_leave_6plus.student.document_input",
        "maternity_leave_6plus.student.document",
        "maternity_leave_6plus.student.pay_fee.next_selector",
        "maternity_leave_6plus.student.pay_fee.pay_selector",
        "maternity_leave_6plus.student.pay_fee.payment_actions",
        "maternity_leave_6plus.student.pay_fee.payment_success_selector",
        "maternity_leave_6plus.chairperson.login",
        "maternity_leave_6plus.chairperson.menu_path",
        "maternity_leave_6plus.chairperson.filters",
        "maternity_leave_6plus.chairperson.request_row",
        "maternity_leave_6plus.chairperson.view_action",
        "maternity_leave_6plus.chairperson.approve_selector",
        "maternity_leave_6plus.chairperson.success_selector",
        "maternity_leave_6plus.chairperson.approved_status",
        "maternity_leave_6plus.chairperson.double_duration_check",
    )
    section = data["maternity_leave_6plus"]
    student = section["student"]
    login_as(student["login"])
    _, wizard = _open_wizard(page, uucms_settings, student)
    wizard.choose_request_type(student["request_type_select"],
                               student["request_type"])
    wizard.enter_request_details(_detail_actions(student))
    _pay_fee(page, uucms_settings, student, student["pay_fee"])

    chair = section["chairperson"]
    login_as(chair["login"])
    page_obj = _open_list(page, uucms_settings, chair)
    page_obj.open_request_details(chair["request_row"], chair["view_action"])
    review = _review_page(page, uucms_settings)
    review.approve(chair["approve_selector"], chair["success_selector"])
    review.expect_request_status(chair["approved_status"])
    expect(page.locator(chair["double_duration_check"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_extension_request(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-030: an extension of expected end date request is submitted."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "extension_request.login", "extension_request.menu_path",
        "extension_request.filters", "extension_request.add_action",
        "extension_request.request_type_select", "extension_request.request_type",
        "extension_request.new_end_date_field", "extension_request.new_end_date",
        "extension_request.reason_field", "extension_request.reason",
        "extension_request.document_input", "extension_request.document",
        "extension_request.pay_fee.next_selector",
        "extension_request.pay_fee.fee_amount_field",
        "extension_request.pay_fee.expected_amount",
        "extension_request.pay_fee.pay_selector",
        "extension_request.pay_fee.payment_actions",
        "extension_request.pay_fee.payment_success_selector",
    )
    section = data["extension_request"]
    login_as(section["login"])
    _, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    wizard.enter_request_details(_detail_actions(section))
    _pay_fee(page, uucms_settings, section, section["pay_fee"])


@pytest.mark.rnd
def test_rnd_sr_extension_approve(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-031: the chairperson approves the extension; the end date is updated."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "extension_approve.login", "extension_approve.menu_path",
        "extension_approve.filters", "extension_approve.request_row",
        "extension_approve.view_action", "extension_approve.remarks_field",
        "extension_approve.approve_remarks", "extension_approve.approve_selector",
        "extension_approve.success_selector", "extension_approve.approved_status",
        "extension_approve.end_date_updated_check", "extension_approve.new_end_date",
    )
    section = data["extension_approve"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.fill_field(section["remarks_field"], section["approve_remarks"])
    review.approve(section["approve_selector"], section["success_selector"])
    review.expect_request_status(section["approved_status"])
    review.expect_field_value(section["end_date_updated_check"],
                              section["new_end_date"])


@pytest.mark.rnd
def test_rnd_sr_extension_reject(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-032: the chairperson rejects the extension with remarks."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "extension_reject.login", "extension_reject.menu_path",
        "extension_reject.filters", "extension_reject.request_row",
        "extension_reject.view_action", "extension_reject.remarks_field",
        "extension_reject.reject_remarks", "extension_reject.reject_selector",
        "extension_reject.success_selector", "extension_reject.rejected_status",
    )
    section = data["extension_reject"]
    login_as(section["login"])
    page_obj = _open_list(page, uucms_settings, section)
    page_obj.open_request_details(section["request_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.reject(section["remarks_field"], section["reject_remarks"],
                  section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_request_status(section["request_row"],
                                   section["rejected_status"])


@pytest.mark.rnd
def test_rnd_sr_additional_year_visibility(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-033: the additional year of extension is available only after double duration."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "additional_year_visibility.student_a.login",
        "additional_year_visibility.student_a.menu_path",
        "additional_year_visibility.student_a.filters",
        "additional_year_visibility.student_a.add_action",
        "additional_year_visibility.student_a.request_type_select",
        "additional_year_visibility.student_a.present",
        "additional_year_visibility.student_b.login",
        "additional_year_visibility.student_b.menu_path",
        "additional_year_visibility.student_b.filters",
        "additional_year_visibility.student_b.add_action",
        "additional_year_visibility.student_b.request_type_select",
        "additional_year_visibility.student_b.absent",
    )
    visibility = data["additional_year_visibility"]
    student_a = visibility["student_a"]
    login_as(student_a["login"])
    page_obj = _open_list(page, uucms_settings, student_a)
    page_obj.open_add_request(student_a["add_action"])
    page_obj.expect_request_types(student_a["request_type_select"],
                                  student_a["present"], [])

    student_b = visibility["student_b"]
    login_as(student_b["login"])
    page_obj = _open_list(page, uucms_settings, student_b)
    page_obj.open_add_request(student_b["add_action"])
    page_obj.expect_request_types(student_b["request_type_select"], [],
                                  student_b["absent"])


@pytest.mark.rnd
def test_rnd_sr_additional_year_request(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-034: the additional year request carries both projected year fields."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "additional_year_request.login", "additional_year_request.menu_path",
        "additional_year_request.filters", "additional_year_request.add_action",
        "additional_year_request.request_type_select",
        "additional_year_request.request_type",
        "additional_year_request.existing_projected_year_field",
        "additional_year_request.existing_projected_year",
        "additional_year_request.updated_projected_year_field",
        "additional_year_request.updated_projected_year",
        "additional_year_request.reason_field", "additional_year_request.reason",
        "additional_year_request.document_input", "additional_year_request.document",
        "additional_year_request.pay_fee.next_selector",
        "additional_year_request.pay_fee.pay_selector",
        "additional_year_request.pay_fee.payment_actions",
        "additional_year_request.pay_fee.payment_success_selector",
    )
    section = data["additional_year_request"]
    login_as(section["login"])
    page_obj, wizard = _open_wizard(page, uucms_settings, section)
    wizard.choose_request_type(section["request_type_select"],
                               section["request_type"])
    page_obj.expect_field_visible(
        section["existing_projected_year_field"],
        section["existing_projected_year"],
    )
    wizard.enter_request_details(_detail_actions(section))
    _pay_fee(page, uucms_settings, section, section["pay_fee"])


@pytest.mark.rnd
def test_rnd_sr_activities_after_extension(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-035: after an approved extension, submissions and convocation are allowed."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "activities_after_extension.login",
        "activities_after_extension.synopsis_menu_path",
        "activities_after_extension.synopsis_row",
        "activities_after_extension.synopsis_submit_action",
        "activities_after_extension.progress_menu_path",
        "activities_after_extension.progress_row",
        "activities_after_extension.progress_submit_action",
        "activities_after_extension.convocation_menu_path",
        "activities_after_extension.convocation_apply_action",
    )
    section = data["activities_after_extension"]
    login_as(section["login"])
    page_obj = _requests_page(page, uucms_settings)
    page_obj.open_from_menu(section["synopsis_menu_path"])
    page_obj.expect_action_available(section["synopsis_row"],
                                     section["synopsis_submit_action"])
    page_obj.open_from_menu(section["progress_menu_path"])
    page_obj.expect_action_available(section["progress_row"],
                                     section["progress_submit_action"])
    MenuPage(page, uucms_settings.timeout_ms).open_menu(
        section["convocation_menu_path"]
    )
    expect(page.locator(section["convocation_apply_action"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sr_activities_blocked_no_extension(page, uucms_settings, login_as):
    """TC-SPECIALREQUEST-036: at the duration limit without an approved extension, all activities are blocked."""
    data = _require_sr_data(
        load_test_data(DATA_FILE),
        "activities_blocked_no_extension.login",
        "activities_blocked_no_extension.synopsis_menu_path",
        "activities_blocked_no_extension.synopsis_row",
        "activities_blocked_no_extension.synopsis_submit_action",
        "activities_blocked_no_extension.progress_menu_path",
        "activities_blocked_no_extension.progress_row",
        "activities_blocked_no_extension.progress_submit_action",
        "activities_blocked_no_extension.convocation_menu_path",
        "activities_blocked_no_extension.convocation_apply_action",
    )
    section = data["activities_blocked_no_extension"]
    login_as(section["login"])
    page_obj = _requests_page(page, uucms_settings)
    page_obj.open_from_menu(section["synopsis_menu_path"])
    page_obj.expect_action_not_available(section["synopsis_row"],
                                         section["synopsis_submit_action"])
    page_obj.open_from_menu(section["progress_menu_path"])
    page_obj.expect_action_not_available(section["progress_row"],
                                         section["progress_submit_action"])
    menu = MenuPage(page, uucms_settings.timeout_ms)
    if menu.is_menu_visible(section["convocation_menu_path"]):
        menu.open_menu(section["convocation_menu_path"])
        expect(page.locator(section["convocation_apply_action"])).to_have_count(0)
