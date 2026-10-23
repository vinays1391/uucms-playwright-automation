"""R&D Phase-1 AREAOFRESEARCH test cases: Discipline Wise - Area of Research Mapping."""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.research_development.pages.phd.area_of_research_page import AreaOfResearchPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/area_of_research.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_aor_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _open_aor_list(page, uucms_settings, data) -> AreaOfResearchPage:
    aor_page = AreaOfResearchPage(page, uucms_settings.timeout_ms)
    aor_page.open_from_menu()
    aor_page.select_filters(data["list"]["filters"])
    return aor_page


@pytest.mark.rnd
def test_rnd_area_of_research_view_list(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-001: view the existing Areas of Research list."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters", "list.list_selector", "list.list_columns",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    expect(authenticated_page.locator(data["list"]["list_selector"])).to_be_visible()
    aor_page.expect_list_columns(data["list"]["list_columns"])


@pytest.mark.rnd
def test_rnd_area_of_research_add_new(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-002: add a new Area of Research."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "add.add_button", "add.code_field", "add.name_field", "add.short_form_field",
        "add.aor_code", "add.aor_name", "add.aor_short_form",
        "add.submit_button", "add.success_selector",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    add = data["add"]
    aor_page.click_add(add["add_button"])
    aor_page.fill_add_form([
        {"type": "fill", "selector": add["code_field"], "value": add["aor_code"]},
        {"type": "fill", "selector": add["name_field"], "value": add["aor_name"]},
        {"type": "fill", "selector": add["short_form_field"], "value": add["aor_short_form"]},
    ])
    aor_page.submit_add(add["submit_button"], add["success_selector"])
    saved = authenticated_page.locator(add["success_selector"])
    saved.first.wait_for(state="visible")
    for value in (add["aor_code"], add["aor_name"], add["aor_short_form"]):
        expect(saved.first).to_contain_text(value)


@pytest.mark.rnd
def test_rnd_area_of_research_duplicate_code_validation(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-003: duplicate Area of Research code is rejected."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "add.code_field", "add.name_field",
        "duplicate_code.add_button", "duplicate_code.existing_code",
        "duplicate_code.new_name", "duplicate_code.submit_button",
        "duplicate_code.expected_message", "duplicate_code.existing_row",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    duplicate = data["duplicate_code"]
    aor_page.click_add(duplicate["add_button"])
    aor_page.fill_add_form([
        {"type": "fill", "selector": data["add"]["code_field"], "value": duplicate["existing_code"]},
        {"type": "fill", "selector": data["add"]["name_field"], "value": duplicate["new_name"]},
    ])
    aor_page.submit_expect_validation(duplicate["submit_button"], duplicate["expected_message"])
    if duplicate.get("confirm_selector"):
        aor_page.dismiss_validation_dialog(duplicate["confirm_selector"])
    aor_page.expect_row_present(duplicate["existing_row"])
    aor_page.expect_absent(duplicate["new_name"])


@pytest.mark.rnd
def test_rnd_area_of_research_required_fields_validation(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-004: required-field validation when adding with blank fields."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "required_validation.add_button", "required_validation.submit_button",
        "required_validation.expected_messages",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    required = data["required_validation"]
    aor_page.click_add(required["add_button"])
    aor_page.submit_expect_validation(
        required["submit_button"], required["expected_messages"][0]
    )
    for message in required["expected_messages"][1:]:
        aor_page.expect_validation_dialog(message)
    if required.get("no_row_created_check"):
        expect(authenticated_page.locator(required["no_row_created_check"])).to_have_count(0)


@pytest.mark.rnd
def test_rnd_area_of_research_delete(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-005: delete an unmapped Area of Research."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "delete.aor_row", "delete.delete_action", "delete.confirm_selector",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    delete = data["delete"]
    aor_page.delete_area(delete["aor_row"], delete["delete_action"], delete["confirm_selector"])
    aor_page.expect_row_removed(delete["aor_row"])


@pytest.mark.rnd
def test_rnd_area_of_research_back_discards_draft(authenticated_page, uucms_settings):
    """TC-AREAOFRESEARCH-006: Back discards a partially entered Area of Research."""
    data = _require_aor_data(
        load_test_data(DATA_FILE),
        "list.filters",
        "back_discards.add_button", "back_discards.code_field", "back_discards.partial_code",
        "back_discards.back_button", "back_discards.list_selector",
        "back_discards.unchanged_row",
    )
    aor_page = _open_aor_list(authenticated_page, uucms_settings, data)
    back = data["back_discards"]
    aor_page.click_add(back["add_button"])
    aor_page.fill_add_form([
        {"type": "fill", "selector": back["code_field"], "value": back["partial_code"]},
    ])
    aor_page.click_back(back["back_button"], back["list_selector"])
    aor_page.expect_row_present(back["unchanged_row"])
