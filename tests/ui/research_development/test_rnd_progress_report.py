"""R&D Phase-2 PROGRESSREPORT test cases.

Scholar-wise progress-report configuration, submission windows, report
ID formats and the multi-stage approval chain:

    Scholar -> Guide -> Co-Guide (if assigned) -> Department
    Chairperson -> Doctoral Committee Chairperson

Role logins come from the "roles" mapping in test_data/login/LoginData.json
via the login_as fixture.
"""

import re

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.constants import statuses
from uucms.constants.menu_paths.research_development import SYMPOSIUM_INVITATION
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.progress_report.progress_configuration_page import ProgressConfigurationPage
from uucms.modules.research_development.pages.progress_report.progress_review_page import ProgressReviewPage
from uucms.modules.research_development.pages.progress_report.progress_submissions_page import ProgressSubmissionsPage
from utils.json_reader import require_fields
from uucms.workflows.research_development.progress_report_workflow import ProgressReportWorkflow

DATA_FILE = "rnd/progress_report.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_pr_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _config_page(page, uucms_settings) -> ProgressConfigurationPage:
    return ProgressConfigurationPage(page, uucms_settings.timeout_ms)


def _submissions_page(page, uucms_settings) -> ProgressSubmissionsPage:
    return ProgressSubmissionsPage(page, uucms_settings.timeout_ms)


def _review_page(page, uucms_settings) -> ProgressReviewPage:
    return ProgressReviewPage(page, uucms_settings.timeout_ms)


def _open_config(page, uucms_settings, section) -> ProgressConfigurationPage:
    page_obj = _config_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


def _open_submissions(page, uucms_settings, section) -> ProgressSubmissionsPage:
    page_obj = _submissions_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


@pytest.mark.rnd
def test_rnd_pr_configuration_scholars_list(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-001: the Department Chairperson views the progress configuration list."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "configuration_list.login", "configuration_list.menu_path",
        "configuration_list.filters", "configuration_list.view_button",
        "configuration_list.list_columns",
    )
    section = data["configuration_list"]
    login_as(section["login"])
    page_obj = _open_config(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])


@pytest.mark.rnd
def test_rnd_pr_configure_scholar(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-002: the progress submission schedule is configured for a scholar."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "configure_scholar.login", "configure_scholar.menu_path",
        "configure_scholar.filters", "configure_scholar.scholar_row",
        "configure_scholar.actions", "configure_scholar.save_selector",
        "configure_scholar.success_selector", "configure_scholar.expected_row_values",
    )
    section = data["configure_scholar"]
    login_as(section["login"])
    page_obj = _open_config(page, uucms_settings, section)
    page_obj.configure_scholar(
        section["scholar_row"], section["actions"],
        section["save_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_values(section["scholar_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_pr_frequency_options(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-003: all eight Frequency of Submission options are available."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "frequency_options.login", "frequency_options.menu_path",
        "frequency_options.filters", "frequency_options.scholar_row",
        "frequency_options.edit_action", "frequency_options.frequency_select",
        "frequency_options.expected_options",
    )
    section = data["frequency_options"]
    login_as(section["login"])
    page_obj = _open_config(page, uucms_settings, section)
    page_obj.open_row_action(section["scholar_row"], section["edit_action"])
    options = page_obj.collect_select_options(section["frequency_select"])
    assert set(options) == set(section["expected_options"]), (
        f"Frequency options differ from the documented set: {options}"
    )


@pytest.mark.rnd
def test_rnd_pr_edit_configuration(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-004: an existing progress configuration is edited."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "edit_configuration.login", "edit_configuration.menu_path",
        "edit_configuration.filters", "edit_configuration.scholar_row",
        "edit_configuration.edit_action", "edit_configuration.actions",
        "edit_configuration.save_selector", "edit_configuration.success_selector",
        "edit_configuration.expected_row_values",
    )
    section = data["edit_configuration"]
    login_as(section["login"])
    page_obj = _open_config(page, uucms_settings, section)
    page_obj.edit_configuration(
        section["scholar_row"], section["edit_action"], section["actions"],
        section["save_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_values(section["scholar_row"], section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_pr_master_status_table(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-005: status and Action Pending With values match the master set."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "master_table.login", "master_table.menu_path", "master_table.filters",
        "master_table.status_cells", "master_table.pending_cells",
    )
    section = data["master_table"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    allowed_statuses = {
        statuses.PROGRESS_YET_TO_UPLOAD, statuses.AWAITING_APPROVAL,
        statuses.APPROVED, statuses.SENT_BACK, statuses.REJECTED,
        statuses.DEADLINE_PASSED,
    }
    allowed_pending = {
        statuses.PENDING_WITH_STUDENT, statuses.PENDING_WITH_GUIDE,
        statuses.PENDING_WITH_CO_GUIDE, statuses.PENDING_WITH_GUIDE_AND_CO_GUIDE,
        statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON,
        statuses.PENDING_WITH_DOCTORAL_COMMITTEE_CHAIRPERSON,
        statuses.PENDING_WITH_NONE, "--",
    }
    statuses_seen = set(page_obj.collect_cell_texts(section["status_cells"]))
    unexpected = statuses_seen - allowed_statuses
    assert not unexpected, f"Unexpected progress statuses observed: {sorted(unexpected)}"
    pending_seen = set(page_obj.collect_cell_texts(section["pending_cells"]))
    unexpected_pending = pending_seen - allowed_pending
    assert not unexpected_pending, (
        f"Unexpected Action Pending With values observed: {sorted(unexpected_pending)}"
    )


@pytest.mark.rnd
def test_rnd_pr_scholar_list(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-006: the scholar's progress submissions list shows all approved reports."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "scholar_list.login", "scholar_list.menu_path", "scholar_list.filters",
        "scholar_list.list_columns",
    )
    section = data["scholar_list"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_list_columns(section["list_columns"])


@pytest.mark.rnd
def test_rnd_pr_submit_enabled_in_window(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-007: the Submit link is enabled inside the submission window."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "submit_window_enabled.login", "submit_window_enabled.menu_path",
        "submit_window_enabled.filters", "submit_window_enabled.report_row",
        "submit_window_enabled.submit_action",
    )
    section = data["submit_window_enabled"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_action_available(section["report_row"], section["submit_action"])


@pytest.mark.rnd
def test_rnd_pr_submit_before_start(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-008: the Submit link is not available before the submission start date."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "submit_before_start.login", "submit_before_start.menu_path",
        "submit_before_start.filters", "submit_before_start.report_row",
        "submit_before_start.submit_action",
    )
    section = data["submit_before_start"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_action_not_available(section["report_row"],
                                         section["submit_action"])


@pytest.mark.rnd
def test_rnd_pr_deadline_passed_message(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-009: the exact deadline message is displayed after the deadline."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "deadline_message.login", "deadline_message.menu_path",
        "deadline_message.filters", "deadline_message.report_row",
        "deadline_message.submit_action", "deadline_message.deadline_message",
    )
    section = data["deadline_message"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_deadline_message(section["deadline_message"])
    page_obj.expect_action_not_available(section["report_row"],
                                         section["submit_action"])


@pytest.mark.rnd
def test_rnd_pr_next_report_after_approval(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-010: the next upcoming report is shown with its submission timeline."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "next_report_displayed.login", "next_report_displayed.menu_path",
        "next_report_displayed.filters", "next_report_displayed.approved_row",
        "next_report_displayed.next_report_row",
        "next_report_displayed.next_report_marker",
        "next_report_displayed.next_report_date",
        "next_report_displayed.submit_action",
    )
    section = data["next_report_displayed"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_row_status(section["approved_row"], statuses.APPROVED)
    page_obj.expect_row_text(section["next_report_row"],
                             section["next_report_marker"])
    page_obj.expect_row_text(section["next_report_row"],
                             section["next_report_date"])
    page_obj.expect_action_available(section["next_report_row"],
                                     section["submit_action"])


@pytest.mark.rnd
def test_rnd_pr_report_id_format(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-011: Progress Report IDs follow PRGRS_AdmissionYear_UniversityID_AORShortForm_ReportNo."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "report_id_format.login", "report_id_format.menu_path",
        "report_id_format.filters", "report_id_format.first_report_row",
        "report_id_format.first_report_id_cell", "report_id_format.first_report_id",
        "report_id_format.id_pattern", "report_id_format.admission_year",
        "report_id_format.university_id", "report_id_format.aor_short_form",
        "report_id_format.all_report_id_cells", "report_id_format.second_report_id",
    )
    section = data["report_id_format"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    report_id = page_obj.read_report_id(section["first_report_row"],
                                        section["first_report_id_cell"])
    assert report_id == section["first_report_id"], (
        f"Progress Report ID {report_id!r} != {section['first_report_id']!r}"
    )
    match = re.fullmatch(section["id_pattern"], report_id)
    assert match, f"Progress Report ID {report_id!r} does not match {section['id_pattern']!r}"
    assert match.groups() == (
        section["admission_year"], section["university_id"],
        section["aor_short_form"], "001",
    )
    ids = page_obj.collect_cell_texts(section["all_report_id_cells"])
    assert section["second_report_id"] in ids, (
        f"Second report ID {section['second_report_id']} not found in {ids}"
    )


@pytest.mark.rnd
def test_rnd_pr_final_report_id_format(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-012: the Final Report ID follows FINAL_AdmissionYear_UniversityID_AORShortForm_ReportNo."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "final_report_id.login", "final_report_id.menu_path",
        "final_report_id.filters", "final_report_id.final_report_row",
        "final_report_id.final_report_id_cell", "final_report_id.expected_id",
        "final_report_id.id_pattern",
    )
    section = data["final_report_id"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    report_id = page_obj.read_report_id(section["final_report_row"],
                                        section["final_report_id_cell"])
    assert report_id == section["expected_id"], (
        f"Final Report ID {report_id!r} != {section['expected_id']!r}"
    )
    assert re.fullmatch(section["id_pattern"], report_id), (
        f"Final Report ID {report_id!r} does not match {section['id_pattern']!r}"
    )


@pytest.mark.rnd
def test_rnd_pr_scholar_submits_report(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-013: the scholar submits a progress report; the chain starts at the Guide."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "scholar.login", "scholar.menu_path", "scholar.filters",
        "scholar.report_row", "scholar.submit_action", "scholar.brief_field",
        "scholar.brief", "scholar.document_input", "scholar.document",
        "scholar.submit_selector", "scholar.success_selector",
        "scholar.report_id_cell",
        "pending_after_scholar",
    )
    section = data["scholar"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.submit_report(
        section["report_row"], section["submit_action"],
        section["brief_field"], section["brief"],
        section["document_input"], section["document"],
        section["submit_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     data["pending_after_scholar"])
    report_id = page_obj.read_report_id(section["report_row"],
                                        section["report_id_cell"])
    assert report_id.upper().startswith("PRGRS"), (
        f"Progress Report ID {report_id!r} is not in the PRGRS format"
    )


@pytest.mark.rnd
def test_rnd_pr_submission_validations(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-014: brief details and report document are both mandatory."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "submission_validation.login", "submission_validation.menu_path",
        "submission_validation.filters", "submission_validation.report_row",
        "submission_validation.submit_action", "submission_validation.brief_field",
        "submission_validation.brief", "submission_validation.document_input",
        "submission_validation.document", "submission_validation.submit_selector",
        "submission_validation.blank_brief_message",
        "submission_validation.missing_document_message",
        "submission_validation.dialog_ok_selector",
    )
    section = data["submission_validation"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.attempt_submit_blank_brief(
        section["report_row"], section["submit_action"],
        section["document_input"], section["document"],
        section["submit_selector"], section["blank_brief_message"],
    )
    page_obj.dismiss_validation_dialog(section["dialog_ok_selector"])
    page_obj.attempt_submit_without_document(
        section["report_row"], section["submit_action"],
        section["brief_field"], section["brief"],
        section["submit_selector"], section["missing_document_message"],
    )


@pytest.mark.rnd
def test_rnd_pr_invalid_document_rejected(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-015: an unsupported report document is rejected."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "invalid_document.login", "invalid_document.menu_path",
        "invalid_document.filters", "invalid_document.report_row",
        "invalid_document.submit_action", "invalid_document.document_input",
        "invalid_document.invalid_file", "invalid_document.expected_message",
    )
    section = data["invalid_document"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.attempt_upload_invalid_file(
        section["report_row"], section["submit_action"],
        section["document_input"], section["invalid_file"],
        section["expected_message"],
    )


@pytest.mark.rnd
def test_rnd_pr_guide_review_list(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-016: the Guide's list filters and row actions reflect the report states."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.list_columns",
        "guide.report_row", "guide.review_action", "guide.pending_rows",
    )
    section = data["guide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.expect_list_columns(section["list_columns"])
    page_obj.expect_action_available(section["report_row"], section["review_action"])
    for entry in section["pending_rows"]:
        page_obj.expect_row_pending_with(entry["row"], entry["pending_with"])


@pytest.mark.rnd
def test_rnd_pr_guide_review_screen(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-017: the Guide review screen shows the report and all review actions."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.report_row",
        "guide.review_action", "guide.document_view_selector",
        "guide.document_download_selector", "guide.detail_sections",
        "guide.remarks_field", "guide.approve_selector",
        "guide.send_back_selector", "guide.reject_selector",
    )
    section = data["guide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_document_available(
        section["document_view_selector"], section["document_download_selector"]
    )
    review.expect_review_sections(section["detail_sections"])
    expect(page.locator(section["remarks_field"])).to_be_visible()
    expect(page.locator(section["approve_selector"])).to_be_visible()
    expect(page.locator(section["send_back_selector"])).to_be_visible()
    expect(page.locator(section["reject_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_guide_approves(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-018: the Guide approves; the report awaits the Co-Guide."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.report_row",
        "guide.review_action", "guide.remarks_field", "guide.approve_remarks",
        "guide.approve_selector", "guide.success_selector",
        "guide.next_pending_with",
    )
    section = data["guide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(section["remarks_field"], section["approve_remarks"],
                   section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     section["next_pending_with"])


@pytest.mark.rnd
def test_rnd_pr_guide_sends_back(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-019: the Guide sends the report back to the Scholar."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.report_row",
        "guide.review_action", "guide.remarks_field", "guide.send_back_remarks",
        "guide.send_back_selector", "guide.success_selector",
    )
    section = data["guide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(section["remarks_field"], section["send_back_remarks"],
                     section["send_back_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(section["report_row"],
                                     statuses.PENDING_WITH_STUDENT)


@pytest.mark.rnd
def test_rnd_pr_guide_rejects(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-020: the Guide rejects the report with remarks."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.report_row",
        "guide.review_action", "guide.remarks_field", "guide.reject_remarks",
        "guide.reject_selector", "guide.success_selector",
    )
    section = data["guide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.reject(section["remarks_field"], section["reject_remarks"],
                  section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.REJECTED)


@pytest.mark.rnd
def test_rnd_pr_guide_coguide_cross_display(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-021: Guide and Co-Guide see each other's reviews (both directions)."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "cross_display.coguide_reviewed_first.login",
        "cross_display.coguide_reviewed_first.menu_path",
        "cross_display.coguide_reviewed_first.filters",
        "cross_display.coguide_reviewed_first.report_row",
        "cross_display.coguide_reviewed_first.view_action",
        "cross_display.coguide_reviewed_first.coguide_review_section",
        "cross_display.coguide_reviewed_first.coguide_review_remarks",
        "cross_display.coguide_reviewed_first.coguide_review_status",
        "cross_display.guide_reviewed_first.login",
        "cross_display.guide_reviewed_first.menu_path",
        "cross_display.guide_reviewed_first.filters",
        "cross_display.guide_reviewed_first.report_row",
        "cross_display.guide_reviewed_first.view_action",
        "cross_display.guide_reviewed_first.guide_review_section",
        "cross_display.guide_reviewed_first.guide_review_remarks",
        "cross_display.guide_reviewed_first.guide_review_status",
    )
    first = data["cross_display"]["coguide_reviewed_first"]
    login_as(first["login"])
    page_obj = _open_submissions(page, uucms_settings, first)
    page_obj.open_row_action(first["report_row"], first["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections([first["coguide_review_section"]])
    review.expect_remarks_visible([first["coguide_review_remarks"]])
    expect(page.get_by_text(first["coguide_review_status"],
                            exact=True)).to_be_visible()

    second = data["cross_display"]["guide_reviewed_first"]
    login_as(second["login"])
    page_obj = _open_submissions(page, uucms_settings, second)
    page_obj.open_row_action(second["report_row"], second["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections([second["guide_review_section"]])
    review.expect_remarks_visible([second["guide_review_remarks"]])
    expect(page.get_by_text(second["guide_review_status"],
                            exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_resubmit_after_send_back(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-022: a sent-back report is resubmitted and re-enters the chain at the Guide."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "resubmit_after_send_back.login", "resubmit_after_send_back.menu_path",
        "resubmit_after_send_back.filters", "resubmit_after_send_back.report_row",
        "resubmit_after_send_back.resubmit_action",
        "resubmit_after_send_back.brief_field", "resubmit_after_send_back.brief",
        "resubmit_after_send_back.document_input",
        "resubmit_after_send_back.document",
        "resubmit_after_send_back.submit_selector",
        "resubmit_after_send_back.success_selector",
        "resubmit_after_send_back.pending_with",
    )
    section = data["resubmit_after_send_back"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.submit_report(
        section["report_row"], section["resubmit_action"],
        section["brief_field"], section["brief"],
        section["document_input"], section["document"],
        section["submit_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     section["pending_with"])


@pytest.mark.rnd
def test_rnd_pr_coguide_approves(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-023: the Co-Guide approves; the report awaits the Department Chairperson."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters",
        "coguide.report_row", "coguide.review_action", "coguide.remarks_field",
        "coguide.approve_remarks", "coguide.approve_selector",
        "coguide.success_selector", "coguide.next_pending_with",
    )
    section = data["coguide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(section["remarks_field"], section["approve_remarks"],
                   section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     section["next_pending_with"])


@pytest.mark.rnd
def test_rnd_pr_coguide_sends_back(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-024: the Co-Guide sends the report back to the Scholar."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters",
        "coguide.report_row", "coguide.review_action", "coguide.remarks_field",
        "coguide.send_back_remarks", "coguide.send_back_selector",
        "coguide.success_selector",
    )
    section = data["coguide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(section["remarks_field"], section["send_back_remarks"],
                     section["send_back_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(section["report_row"],
                                     statuses.PENDING_WITH_STUDENT)


@pytest.mark.rnd
def test_rnd_pr_chain_skips_coguide(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-025: without a co-guide the report goes straight to the Department Chairperson."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "skip_coguide.login", "skip_coguide.menu_path", "skip_coguide.filters",
        "skip_coguide.report_row", "skip_coguide.review_action",
        "skip_coguide.remarks_field", "skip_coguide.approve_remarks",
        "skip_coguide.approve_selector", "skip_coguide.success_selector",
        "skip_coguide.next_pending_with",
    )
    section = data["skip_coguide"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(section["remarks_field"], section["approve_remarks"],
                   section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     section["next_pending_with"])


@pytest.mark.rnd
def test_rnd_pr_chairperson_review_screen(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-026: the Department Chairperson review screen shows the report and actions."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.report_row",
        "department_chairperson.review_action",
        "department_chairperson.document_view_selector",
        "department_chairperson.document_download_selector",
        "department_chairperson.detail_sections",
        "department_chairperson.remarks_field",
        "department_chairperson.approve_selector",
        "department_chairperson.send_back_selector",
        "department_chairperson.reject_selector",
    )
    section = data["department_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_document_available(
        section["document_view_selector"], section["document_download_selector"]
    )
    review.expect_review_sections(section["detail_sections"])
    expect(page.locator(section["remarks_field"])).to_be_visible()
    expect(page.locator(section["approve_selector"])).to_be_visible()
    expect(page.locator(section["send_back_selector"])).to_be_visible()
    expect(page.locator(section["reject_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_chairperson_sees_all_reviews(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-027: the Department Chairperson sees the Guide and Co-Guide reviews."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.report_row",
        "department_chairperson.review_action",
        "department_chairperson.expected_sections",
        "department_chairperson.expected_remarks",
    )
    section = data["department_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections(section["expected_sections"])
    review.expect_remarks_visible(section["expected_remarks"])


@pytest.mark.rnd
def test_rnd_pr_chairperson_approves(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-028: the Department Chairperson approves; the report awaits the DCC."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.report_row",
        "department_chairperson.review_action",
        "department_chairperson.remarks_field",
        "department_chairperson.approve_remarks",
        "department_chairperson.approve_selector",
        "department_chairperson.success_selector",
        "department_chairperson.next_pending_with",
    )
    section = data["department_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(section["remarks_field"], section["approve_remarks"],
                   section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(section["report_row"],
                                     section["next_pending_with"])


@pytest.mark.rnd
def test_rnd_pr_chairperson_rejects(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-029: the Department Chairperson rejects the report with remarks."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.report_row",
        "department_chairperson.review_action",
        "department_chairperson.remarks_field",
        "department_chairperson.reject_remarks",
        "department_chairperson.reject_selector",
        "department_chairperson.success_selector",
    )
    section = data["department_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.reject(section["remarks_field"], section["reject_remarks"],
                  section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.REJECTED)


@pytest.mark.rnd
def test_rnd_pr_dcc_review_screen(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-030: the DCC review screen shows all preceding reviews and the symposium upload."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.report_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.expected_sections",
        "doctoral_committee_chairperson.expected_remarks",
        "doctoral_committee_chairperson.symposium_upload_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.approve_selector",
        "doctoral_committee_chairperson.send_back_selector",
        "doctoral_committee_chairperson.reject_selector",
    )
    section = data["doctoral_committee_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections(section["expected_sections"])
    review.expect_remarks_visible(section["expected_remarks"])
    review.expect_symposium_upload_action(section["symposium_upload_action"])
    expect(page.locator(section["remarks_field"])).to_be_visible()
    expect(page.locator(section["approve_selector"])).to_be_visible()
    expect(page.locator(section["send_back_selector"])).to_be_visible()
    expect(page.locator(section["reject_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_dcc_approves(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-031: the DCC approves; the total approved count increments and the scholar reaches the symposium list."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.report_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.approve_remarks",
        "doctoral_committee_chairperson.approve_selector",
        "doctoral_committee_chairperson.success_selector",
        "doctoral_committee_chairperson.symposium_input",
        "doctoral_committee_chairperson.symposium_document",
        "doctoral_committee_chairperson.total_approved_cell",
        "doctoral_committee_chairperson.total_approved_value",
        "doctoral_committee_chairperson.symposium_list_check",
    )
    section = data["doctoral_committee_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.upload_symposium_details(section["symposium_input"],
                                    section["symposium_document"])
    review.approve(section["remarks_field"], section["approve_remarks"],
                   section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.APPROVED)
    total = page_obj.read_cell_text(section["total_approved_cell"])
    assert total == str(section["total_approved_value"]), (
        f"Total Approved Submission Till Date {total!r} != "
        f"{section['total_approved_value']!r}"
    )
    MenuPage(page, uucms_settings.timeout_ms).open_menu(list(SYMPOSIUM_INVITATION))
    expect(page.get_by_text(section["symposium_list_check"],
                            exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_dcc_rejects(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-032: the DCC rejects the report with remarks."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.report_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.reject_remarks",
        "doctoral_committee_chairperson.reject_selector",
        "doctoral_committee_chairperson.success_selector",
    )
    section = data["doctoral_committee_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.reject(section["remarks_field"], section["reject_remarks"],
                  section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.REJECTED)


@pytest.mark.rnd
def test_rnd_pr_dcc_sends_back(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-033: the DCC sends the report back to the Scholar."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.report_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.send_back_remarks",
        "doctoral_committee_chairperson.send_back_selector",
        "doctoral_committee_chairperson.success_selector",
    )
    section = data["doctoral_committee_chairperson"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(section["remarks_field"], section["send_back_remarks"],
                     section["send_back_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_status(section["report_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(section["report_row"],
                                     statuses.PENDING_WITH_STUDENT)


@pytest.mark.rnd
def test_rnd_pr_scholar_view_approved_report(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-034: the scholar views the approved report with all reviews and the symposium details."""
    data = _require_pr_data(
        load_test_data(DATA_FILE),
        "scholar_view_approved.login", "scholar_view_approved.menu_path",
        "scholar_view_approved.filters", "scholar_view_approved.report_row",
        "scholar_view_approved.view_action",
        "scholar_view_approved.document_view_selector",
        "scholar_view_approved.document_download_selector",
        "scholar_view_approved.expected_sections",
        "scholar_view_approved.expected_remarks",
        "scholar_view_approved.symposium_details_view_selector",
        "scholar_view_approved.symposium_details_download_selector",
    )
    section = data["scholar_view_approved"]
    login_as(section["login"])
    page_obj = _open_submissions(page, uucms_settings, section)
    page_obj.open_row_action(section["report_row"], section["view_action"])
    review = _review_page(page, uucms_settings)
    review.expect_document_available(
        section["document_view_selector"], section["document_download_selector"]
    )
    review.expect_review_sections(section["expected_sections"])
    review.expect_remarks_visible(section["expected_remarks"])
    expect(page.locator(section["symposium_details_view_selector"])).to_be_visible()
    expect(page.locator(
        section["symposium_details_download_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_pr_full_approval_chain(page, uucms_settings, login_as):
    """TC-PROGRESSREPORT-013/018/023/028/031: full Scholar -> Guide -> Co-Guide ->
    Department Chairperson -> Doctoral Committee Chairperson chain ends Approved."""
    _require_pr_data(
        load_test_data(DATA_FILE),
        "pending_after_scholar", "pending_after_guide",
        "scholar.login", "scholar.menu_path", "scholar.filters",
        "scholar.report_row", "scholar.submit_action", "scholar.brief_field",
        "scholar.brief", "scholar.document_input", "scholar.document",
        "scholar.submit_selector",
        "guide.login", "guide.menu_path", "guide.filters", "guide.report_row",
        "guide.review_action", "guide.remarks_field", "guide.approve_remarks",
        "guide.approve_selector",
        "coguide.login", "coguide.menu_path", "coguide.filters",
        "coguide.report_row", "coguide.review_action", "coguide.remarks_field",
        "coguide.approve_remarks", "coguide.approve_selector",
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.report_row",
        "department_chairperson.review_action",
        "department_chairperson.remarks_field",
        "department_chairperson.approve_remarks",
        "department_chairperson.approve_selector",
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.report_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.approve_remarks",
        "doctoral_committee_chairperson.approve_selector",
    )
    data = load_test_data(DATA_FILE)
    workflow = ProgressReportWorkflow(page, uucms_settings, login_as)
    workflow.run_approval_chain(data)
