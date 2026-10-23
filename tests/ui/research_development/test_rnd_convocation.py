"""R&D Phase-2 CONVOCATION test cases.

Registrar (Evaluation) marks approved scholars as convocation
eligible; eligible scholars apply with the Indian/Foreign fee
structure; PDC and degree/convocation certificate printing; role
restriction.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.convocation.convocation_eligibility_page import ConvocationEligibilityPage
from uucms.modules.research_development.pages.requests.guide_change_page import GuideChangePage
from utils.json_reader import require_fields

DATA_FILE = "rnd/convocation.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_conv_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _convocation_page(page, uucms_settings) -> ConvocationEligibilityPage:
    return ConvocationEligibilityPage(page, uucms_settings.timeout_ms)


def _open_eligibility_list(page, uucms_settings, section) -> ConvocationEligibilityPage:
    page_obj = _convocation_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


def _apply_and_pay(page, uucms_settings, section) -> None:
    """Scholar: apply for the convocation and pay the applicable fee."""
    page_obj = ConvocationEligibilityPage(page, uucms_settings.timeout_ms)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.click_control(section["apply_action"])
    if section.get("apply_actions"):
        page_obj.execute_actions(section["apply_actions"])
    fee = page_obj.page.locator(section["fee_amount_field"])
    fee.first.wait_for(state="visible")
    expect(fee.first).to_contain_text(section["expected_fee"])
    wizard = GuideChangePage(page, uucms_settings.timeout_ms)
    wizard.pay_fees(section["pay_selector"], section.get("payment_actions"),
                    section.get("payment_success_selector"))


@pytest.mark.rnd
def test_rnd_conv_eligibility_list(page, uucms_settings, login_as):
    """TC-CONVOCATION-001: the eligibility list shows only approved scholars with the mark-as-eligible column."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "eligibility_list.login", "eligibility_list.menu_path",
        "eligibility_list.filters", "eligibility_list.view_button",
        "eligibility_list.list_columns", "eligibility_list.submit_action",
    )
    section = data["eligibility_list"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])
    expect(page.locator(section["submit_action"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_conv_rejected_scholar_absent(page, uucms_settings, login_as):
    """TC-CONVOCATION-002: a rejected symposium scholar is not in the eligibility list."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "rejected_absent.login", "rejected_absent.menu_path",
        "rejected_absent.filters", "rejected_absent.view_button",
        "rejected_absent.present", "rejected_absent.absent",
    )
    section = data["rejected_absent"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.expect_scholars_listed(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_conv_mark_multiple_eligible(page, uucms_settings, login_as):
    """TC-CONVOCATION-003: multiple scholars are marked eligible at once (multi-select)."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "mark_eligible.login", "mark_eligible.menu_path",
        "mark_eligible.filters", "mark_eligible.view_button",
        "mark_eligible.checks", "mark_eligible.submit_action",
        "mark_eligible.success_selector",
    )
    section = data["mark_eligible"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.mark_eligible(section["checks"], section["submit_action"],
                           section["success_selector"])


@pytest.mark.rnd
def test_rnd_conv_view_details(page, uucms_settings, login_as):
    """TC-CONVOCATION-004: the convocation eligibility details of a scholar can be viewed."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "view_details.login", "view_details.menu_path", "view_details.filters",
        "view_details.view_button", "view_details.scholar_row",
        "view_details.view_action", "view_details.detail_fields",
        "view_details.media_view_selector",
    )
    section = data["view_details"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.open_scholar_details(section["scholar_row"],
                                  section["view_action"])
    page_obj.expect_eligibility_details(section["detail_fields"])
    expect(page.locator(section["media_view_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_conv_apply_indian_fee(page, uucms_settings, login_as):
    """TC-CONVOCATION-005: an Indian scholar applies with the Indian fee structure and appears in the list."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "apply_indian_fee.scholar.login", "apply_indian_fee.scholar.menu_path",
        "apply_indian_fee.scholar.apply_action",
        "apply_indian_fee.scholar.apply_actions",
        "apply_indian_fee.scholar.fee_amount_field",
        "apply_indian_fee.scholar.expected_fee",
        "apply_indian_fee.scholar.pay_selector",
        "apply_indian_fee.scholar.payment_actions",
        "apply_indian_fee.scholar.payment_success_selector",
        "apply_indian_fee.registrar_check.login",
        "apply_indian_fee.registrar_check.menu_path",
        "apply_indian_fee.registrar_check.filters",
        "apply_indian_fee.registrar_check.view_button",
        "apply_indian_fee.registrar_check.scholar_row",
        "apply_indian_fee.registrar_check.paid_check",
    )
    scholar = data["apply_indian_fee"]["scholar"]
    login_as(scholar["login"])
    _apply_and_pay(page, uucms_settings, scholar)

    check = data["apply_indian_fee"]["registrar_check"]
    login_as(check["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, check)
    page_obj.view_scholars(check["filters"], check["view_button"])
    page_obj.expect_row_present(check["scholar_row"])
    expect(page.locator(check["paid_check"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_conv_apply_foreign_fee(page, uucms_settings, login_as):
    """TC-CONVOCATION-006: a foreign scholar applies with the Foreign fee structure."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "apply_foreign_fee.scholar.login", "apply_foreign_fee.scholar.menu_path",
        "apply_foreign_fee.scholar.apply_action",
        "apply_foreign_fee.scholar.apply_actions",
        "apply_foreign_fee.scholar.fee_amount_field",
        "apply_foreign_fee.scholar.expected_fee",
        "apply_foreign_fee.scholar.pay_selector",
        "apply_foreign_fee.scholar.payment_actions",
        "apply_foreign_fee.scholar.payment_success_selector",
        "apply_foreign_fee.registrar_check.login",
        "apply_foreign_fee.registrar_check.menu_path",
        "apply_foreign_fee.registrar_check.filters",
        "apply_foreign_fee.registrar_check.view_button",
        "apply_foreign_fee.registrar_check.scholar_row",
        "apply_foreign_fee.registrar_check.paid_check",
    )
    scholar = data["apply_foreign_fee"]["scholar"]
    login_as(scholar["login"])
    _apply_and_pay(page, uucms_settings, scholar)

    check = data["apply_foreign_fee"]["registrar_check"]
    login_as(check["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, check)
    page_obj.view_scholars(check["filters"], check["view_button"])
    page_obj.expect_row_present(check["scholar_row"])
    expect(page.locator(check["paid_check"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_conv_pdc_print(page, uucms_settings, login_as):
    """TC-CONVOCATION-007: the PDC is generated and printed for the eligible scholar."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "pdc_print.login", "pdc_print.menu_path", "pdc_print.filters",
        "pdc_print.view_button", "pdc_print.scholar_row",
        "pdc_print.pdc_action", "pdc_print.success_selector",
    )
    section = data["pdc_print"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.print_pdc(section["scholar_row"], section["pdc_action"],
                       section["success_selector"])


@pytest.mark.rnd
def test_rnd_conv_degree_certificate(page, uucms_settings, login_as):
    """TC-CONVOCATION-008: the degree/convocation certificate is issued and printed."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "degree_certificate.login", "degree_certificate.menu_path",
        "degree_certificate.filters", "degree_certificate.view_button",
        "degree_certificate.scholar_row", "degree_certificate.issue_action",
        "degree_certificate.print_action", "degree_certificate.success_selector",
    )
    section = data["degree_certificate"]
    login_as(section["login"])
    page_obj = _open_eligibility_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.issue_degree_certificate(
        section["scholar_row"], section["issue_action"],
        section["print_action"], section["success_selector"],
    )


@pytest.mark.rnd
def test_rnd_conv_access_registrar_evaluation_only(page, uucms_settings, login_as):
    """TC-CONVOCATION-009: Convocation Eligibility is only available to Registrar (Evaluation)."""
    data = _require_conv_data(
        load_test_data(DATA_FILE),
        "access_denied.roles", "access_denied.menu_path",
    )
    section = data["access_denied"]
    for role in section["roles"]:
        login_as(role)
        menu = MenuPage(page, uucms_settings.timeout_ms)
        if menu.is_menu_visible(section["menu_path"]):
            _require_conv_data(data, "access_denied.denied_message")
            menu.open_menu(section["menu_path"])
            expect(page.get_by_text(section["denied_message"])).to_be_visible()
