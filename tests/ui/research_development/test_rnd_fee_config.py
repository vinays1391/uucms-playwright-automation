"""R&D Phase-2 FEECONFIG test cases.

University Admin maintains the R&D fee list per program, request type,
academic year, category, gender and income limit; revisions with a
Committee Order, read-only viewing, reset and the role restriction.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.fee_config.fee_config_page import FeeConfigPage
from uucms.modules.research_development.pages.requests.guide_change_page import GuideChangePage
from utils.json_reader import require_fields

DATA_FILE = "rnd/fee_config.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_fc_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _fee_page(page, uucms_settings) -> FeeConfigPage:
    return FeeConfigPage(page, uucms_settings.timeout_ms)


def _open_fee_list(page, uucms_settings, section) -> FeeConfigPage:
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


def _open_request_wizard(page, uucms_settings, section) -> GuideChangePage:
    """Advance the student to the preferred faculty / fee step."""
    list_page = FeeConfigPage(page, uucms_settings.timeout_ms)
    list_page.open_from_menu(section["menu_path"])
    if section.get("filters"):
        list_page.apply_filters(section["filters"])
    list_page.open_add_new_fee(section["add_action"])
    wizard = GuideChangePage(page, uucms_settings.timeout_ms)
    wizard.choose_request_type(section["request_type_select"], section["request_type"])
    wizard.enter_request_details([
        {"type": "fill", "selector": section["reason_field"],
         "value": section["reason"]},
        {"type": "upload", "selector": section["document_input"],
         "value": section["document"]},
    ])
    wizard.proceed_next(section["next_selector"])
    wizard.execute_actions([
        {"type": "select_label", "selector": section["faculty_select"],
         "value": section["faculty"]},
    ])
    return wizard


@pytest.mark.rnd
def test_rnd_fc_fee_list_filters(page, uucms_settings, login_as):
    """TC-FEECONFIG-001: the R&D fee list narrows with program/request/year filters."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "fee_list.login", "fee_list.menu_path", "fee_list.filters",
        "fee_list.list_columns", "fee_list.row_actions",
        "fee_list.add_new_fee_action", "fee_list.expected_row_values",
    )
    section = data["fee_list"]
    login_as(section["login"])
    page_obj = _open_fee_list(page, uucms_settings, section)
    page_obj.expect_list_columns(section["list_columns"])
    for action in section["row_actions"]:
        expect(page.get_by_text(action, exact=True)).to_be_visible()
    expect(page.locator(section["add_new_fee_action"])).to_be_visible()
    page_obj.expect_texts_visible(section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_fc_add_new_fee(page, uucms_settings, login_as):
    """TC-FEECONFIG-002: a new R&D fee is saved and appears in the fee list."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "add_fee.login", "add_fee.menu_path", "add_fee.add_action",
        "add_fee.actions", "add_fee.save_selector", "add_fee.success_selector",
        "add_fee.fee_row", "add_fee.expected_row_values",
    )
    section = data["add_fee"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_add_new_fee(section["add_action"])
    page_obj.save_fee(section["actions"], section["save_selector"],
                      section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_row_values(section["fee_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_fc_add_fee_multi_select(page, uucms_settings, login_as):
    """TC-FEECONFIG-003: a fee applies to all selected Disciplines and Areas of Research."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "add_fee_multi_select.login", "add_fee_multi_select.menu_path",
        "add_fee_multi_select.add_action", "add_fee_multi_select.actions",
        "add_fee_multi_select.save_selector", "add_fee_multi_select.success_selector",
        "add_fee_multi_select.fee_row", "add_fee_multi_select.view_action",
        "add_fee_multi_select.expected_selections",
    )
    section = data["add_fee_multi_select"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_add_new_fee(section["add_action"])
    page_obj.save_fee(section["actions"], section["save_selector"],
                      section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_fee(section["fee_row"], section["view_action"])
    page_obj.expect_texts_visible(section["expected_selections"])


@pytest.mark.rnd
def test_rnd_fc_revise_fee_with_order(page, uucms_settings, login_as):
    """TC-FEECONFIG-004: the fee is revised with a Committee Order number and document."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "revise_fee.login", "revise_fee.menu_path", "revise_fee.fee_row",
        "revise_fee.revise_action", "revise_fee.actions", "revise_fee.save_selector",
        "revise_fee.success_selector", "revise_fee.expected_row_values",
    )
    section = data["revise_fee"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.revise_fee(
        section["fee_row"], section["revise_action"], section["actions"],
        section["save_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_row_values(section["fee_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_fc_cancel_discards(page, uucms_settings, login_as):
    """TC-FEECONFIG-005: Cancel discards the fee entry; no new row appears."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "cancel_discards.login", "cancel_discards.menu_path",
        "cancel_discards.add_action", "cancel_discards.actions",
        "cancel_discards.cancel_selector", "cancel_discards.cancelled_amount",
    )
    section = data["cancel_discards"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_add_new_fee(section["add_action"])
    page_obj.fill_fee_form(section["actions"])
    page_obj.cancel_fee_entry(section["cancel_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_absent(section["cancelled_amount"])


@pytest.mark.rnd
def test_rnd_fc_reset_fee(page, uucms_settings, login_as):
    """TC-FEECONFIG-006: Reset restores the previous fee configuration."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "reset_fee.login", "reset_fee.menu_path", "reset_fee.fee_row",
        "reset_fee.reset_action", "reset_fee.confirm_selector",
        "reset_fee.success_selector", "reset_fee.expected_row_values",
    )
    section = data["reset_fee"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.reset_fee(
        section["fee_row"], section["reset_action"],
        section["confirm_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_row_values(section["fee_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_fc_view_fee_read_only(page, uucms_settings, login_as):
    """TC-FEECONFIG-007: the fee opens in read-only mode without Save/Cancel."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "view_fee.login", "view_fee.menu_path", "view_fee.fee_row",
        "view_fee.view_action", "view_fee.sections", "view_fee.save_selector",
        "view_fee.cancel_selector",
    )
    section = data["view_fee"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_fee(section["fee_row"], section["view_action"])
    page_obj.expect_fee_sections(section["sections"])
    page_obj.expect_view_read_only(section["save_selector"], section["cancel_selector"])


@pytest.mark.rnd
def test_rnd_fc_request_types_complete(page, uucms_settings, login_as):
    """TC-FEECONFIG-008: all ten Request Types are available in fee configuration."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "request_types.login", "request_types.menu_path", "request_types.add_action",
        "request_types.request_type_select", "request_types.expected_options",
    )
    section = data["request_types"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_add_new_fee(section["add_action"])
    options = page_obj.collect_select_options(section["request_type_select"])
    assert set(options) == set(section["expected_options"]), (
        f"Request Type options differ from the documented set: {options}"
    )


@pytest.mark.rnd
def test_rnd_fc_fee_by_category(page, uucms_settings, login_as):
    """TC-FEECONFIG-009: the Amount to be Paid on the request screen loads per student category."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "fee_by_category.general_student.login",
        "fee_by_category.general_student.menu_path",
        "fee_by_category.general_student.filters",
        "fee_by_category.general_student.add_action",
        "fee_by_category.general_student.request_type_select",
        "fee_by_category.general_student.request_type",
        "fee_by_category.general_student.reason_field",
        "fee_by_category.general_student.reason",
        "fee_by_category.general_student.document_input",
        "fee_by_category.general_student.document",
        "fee_by_category.general_student.next_selector",
        "fee_by_category.general_student.faculty_select",
        "fee_by_category.general_student.faculty",
        "fee_by_category.general_student.fee_amount_field",
        "fee_by_category.general_student.expected_amount",
        "fee_by_category.obc_student.login",
        "fee_by_category.obc_student.menu_path",
        "fee_by_category.obc_student.filters",
        "fee_by_category.obc_student.add_action",
        "fee_by_category.obc_student.request_type_select",
        "fee_by_category.obc_student.request_type",
        "fee_by_category.obc_student.reason_field",
        "fee_by_category.obc_student.reason",
        "fee_by_category.obc_student.document_input",
        "fee_by_category.obc_student.document",
        "fee_by_category.obc_student.next_selector",
        "fee_by_category.obc_student.faculty_select",
        "fee_by_category.obc_student.faculty",
        "fee_by_category.obc_student.fee_amount_field",
        "fee_by_category.obc_student.expected_amount",
    )
    for key in ("general_student", "obc_student"):
        section = data["fee_by_category"][key]
        login_as(section["login"])
        wizard = _open_request_wizard(page, uucms_settings, section)
        wizard.expect_fee_amount(section["fee_amount_field"],
                                 section["expected_amount"])


@pytest.mark.rnd
def test_rnd_fc_blank_amount_validation(page, uucms_settings, login_as):
    """TC-FEECONFIG-010: a fee with Amount (Rs) blank is not saved."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "blank_amount.login", "blank_amount.menu_path", "blank_amount.add_action",
        "blank_amount.actions", "blank_amount.save_selector",
        "blank_amount.expected_message",
    )
    section = data["blank_amount"]
    login_as(section["login"])
    page_obj = _fee_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_add_new_fee(section["add_action"])
    page_obj.attempt_save_fee(
        section["actions"], section["save_selector"], section["expected_message"]
    )


@pytest.mark.rnd
def test_rnd_fc_access_university_admin_only(page, uucms_settings, login_as):
    """TC-FEECONFIG-011: R&D Fee Configuration is not accessible to other roles."""
    data = _require_fc_data(
        load_test_data(DATA_FILE),
        "access_denied.roles", "access_denied.menu_path",
    )
    section = data["access_denied"]
    for role in section["roles"]:
        login_as(role)
        menu = MenuPage(page, uucms_settings.timeout_ms)
        if menu.is_menu_visible(section["menu_path"]):
            _require_fc_data(data, "access_denied.denied_message")
            menu.open_menu(section["menu_path"])
            expect(page.get_by_text(section["denied_message"])).to_be_visible()
