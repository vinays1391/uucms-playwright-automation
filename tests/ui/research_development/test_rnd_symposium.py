"""R&D Phase-2 SYMPOSIUM test cases.

The Doctoral Committee Chairperson invites final-report-approved
scholars for the Final Viva Voce / Colloquium / Symposium, schedules
the event, uploads the event details after the date & time has passed,
approves or rejects, and re-invites rejected scholars. The scholar's
invitation list mirrors the status transitions.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.constants import statuses
from uucms.modules.research_development.pages.symposium.symposium_event_details_page import SymposiumEventDetailsPage
from uucms.modules.research_development.pages.symposium.symposium_invitation_page import SymposiumInvitationPage
from uucms.modules.research_development.pages.symposium.symposium_scholar_invitation_page import SymposiumScholarInvitationPage
from utils.json_reader import require_fields
from uucms.workflows.research_development.symposium_workflow import SymposiumWorkflow

DATA_FILE = "rnd/symposium.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_sym_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _invitation_page(page, uucms_settings) -> SymposiumInvitationPage:
    return SymposiumInvitationPage(page, uucms_settings.timeout_ms)


def _details_page(page, uucms_settings) -> SymposiumEventDetailsPage:
    return SymposiumEventDetailsPage(page, uucms_settings.timeout_ms)


def _scholar_page(page, uucms_settings) -> SymposiumScholarInvitationPage:
    return SymposiumScholarInvitationPage(page, uucms_settings.timeout_ms)


def _open_dcc_list(page, uucms_settings, section) -> SymposiumInvitationPage:
    page_obj = _invitation_page(page, uucms_settings)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


@pytest.mark.rnd
def test_rnd_sym_dcc_list(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-001: the DCC lists only final-report-approved scholars with the invitation columns."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "dcc_list.login", "dcc_list.menu_path", "dcc_list.filters",
        "dcc_list.view_button", "dcc_list.list_columns",
        "dcc_list.view_report_action",
    )
    section = data["dcc_list"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.view_scholars(section["filters"], section["view_button"])
    page_obj.expect_list_columns(section["list_columns"])
    expect(page.locator(section["view_report_action"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sym_send_invitation(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-002: the invitation moves the scholar from Yet to Send to Scheduled; the scholar sees it."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "invite.login", "invite.menu_path", "invite.filters",
        "invite.scholar_row", "invite.initial_status", "invite.actions",
        "invite.send_selector", "invite.success_selector",
        "invite.scholar_check.login", "invite.scholar_check.menu_path",
        "invite.scholar_check.event_row",
    )
    section = data["invite"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.expect_status(section["scholar_row"], section["initial_status"])
    page_obj.send_invitation(
        section["scholar_row"], section["actions"],
        section["send_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_status(section["scholar_row"], statuses.SCHEDULED)

    check = section["scholar_check"]
    login_as(check["login"])
    scholar_page = _scholar_page(page, uucms_settings)
    scholar_page.open_from_menu(check["menu_path"])
    scholar_page.expect_status(check["event_row"], statuses.SCHEDULED)


@pytest.mark.rnd
def test_rnd_sym_edit_schedule(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-003: the schedule of a Scheduled event is edited and saved."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "edit_schedule.login", "edit_schedule.menu_path", "edit_schedule.filters",
        "edit_schedule.scholar_row", "edit_schedule.edit_action",
        "edit_schedule.date_time_field", "edit_schedule.new_date_time",
        "edit_schedule.duration_field", "edit_schedule.new_duration",
        "edit_schedule.save_selector", "edit_schedule.success_selector",
        "edit_schedule.expected_row_values",
    )
    section = data["edit_schedule"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.edit_schedule(
        section["scholar_row"], section["edit_action"],
        section["date_time_field"], section["new_date_time"],
        section["duration_field"], section["new_duration"],
        section["save_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_row_values(section["scholar_row"],
                               section["expected_row_values"])


@pytest.mark.rnd
def test_rnd_sym_upload_disabled_before_event(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-004: Upload Details is not enabled before the event date & time has passed."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "upload_disabled_before.login", "upload_disabled_before.menu_path",
        "upload_disabled_before.filters", "upload_disabled_before.scholar_row",
        "upload_disabled_before.status", "upload_disabled_before.upload_action",
    )
    section = data["upload_disabled_before"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.expect_status(section["scholar_row"], section["status"])
    page_obj.expect_action_not_available(section["scholar_row"],
                                         section["upload_action"])


@pytest.mark.rnd
def test_rnd_sym_event_details_screen(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-005: the event details screen shows the event information and mandatory fields."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "event_details_screen.login", "event_details_screen.menu_path",
        "event_details_screen.filters", "event_details_screen.scholar_row",
        "event_details_screen.upload_action", "event_details_screen.detail_fields",
        "event_details_screen.media_input", "event_details_screen.media_label",
        "event_details_screen.media_link_field", "event_details_screen.support_input",
        "event_details_screen.approve_selector",
        "event_details_screen.reject_selector",
    )
    section = data["event_details_screen"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.open_event_details(section["scholar_row"],
                                section["upload_action"])
    details = _details_page(page, uucms_settings)
    details.expect_event_details(section["detail_fields"])
    expect(page.get_by_text(section["media_label"], exact=True)).to_be_visible()
    expect(page.locator(section["media_input"])).to_be_attached()
    expect(page.locator(section["media_link_field"])).to_be_visible()
    expect(page.locator(section["support_input"])).to_be_attached()
    expect(page.locator(section["approve_selector"])).to_be_visible()
    expect(page.locator(section["reject_selector"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_sym_approve_event(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-006: the event details are uploaded and the event is Approved."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "event_details.login", "event_details.menu_path", "event_details.filters",
        "event_details.scholar_row", "event_details.upload_action",
        "event_details.event_type_select", "event_details.event_type",
        "event_details.media_input", "event_details.media",
        "event_details.media_link_field", "event_details.media_link",
        "event_details.support_input", "event_details.support",
        "event_details.approve_selector", "event_details.success_selector",
        "event_details.view_details_action",
    )
    section = data["event_details"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.open_event_details(section["scholar_row"],
                                section["upload_action"])
    details = _details_page(page, uucms_settings)
    details.choose_event_type(section["event_type_select"],
                              section["event_type"])
    details.upload_details(
        section["media_input"], section["media"],
        section["media_link_field"], section["media_link"],
        section["support_input"], section["support"],
    )
    details.approve(section["approve_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_status(section["scholar_row"], statuses.APPROVED)
    page_obj.expect_action_available(section["scholar_row"],
                                     section["view_details_action"])


@pytest.mark.rnd
def test_rnd_sym_reject_event(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-007: the event is Rejected; Send Re-Invitation and Edit Schedule are offered."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "event_details.login", "event_details.menu_path", "event_details.filters",
        "event_details.scholar_row", "event_details.upload_action",
        "event_details.media_input", "event_details.media",
        "event_details.media_link_field", "event_details.media_link",
        "event_details.support_input", "event_details.support",
        "event_details.reject_selector", "event_details.success_selector",
        "re_invite.re_invite_action", "edit_schedule.edit_action",
    )
    section = data["event_details"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.open_event_details(section["scholar_row"],
                                section["upload_action"])
    details = _details_page(page, uucms_settings)
    details.upload_details(
        section["media_input"], section["media"],
        section["media_link_field"], section["media_link"],
        section["support_input"], section["support"],
    )
    details.reject(section["reject_selector"], section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_status(section["scholar_row"], statuses.REJECTED)
    page_obj.expect_action_available(section["scholar_row"],
                                     data["re_invite"]["re_invite_action"])
    page_obj.expect_action_available(section["scholar_row"],
                                     data["edit_schedule"]["edit_action"])


@pytest.mark.rnd
def test_rnd_sym_approve_blocked_missing_details(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-008: approval is blocked while the mandatory event details are missing."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "approve_missing_details.login", "approve_missing_details.menu_path",
        "approve_missing_details.filters", "approve_missing_details.scholar_row",
        "approve_missing_details.upload_action",
        "approve_missing_details.approve_selector",
        "approve_missing_details.expected_message",
        "approve_missing_details.still_status",
    )
    section = data["approve_missing_details"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.open_event_details(section["scholar_row"],
                                section["upload_action"])
    details = _details_page(page, uucms_settings)
    details.attempt_approve(section["approve_selector"],
                            section["expected_message"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_status(section["scholar_row"], section["still_status"])


@pytest.mark.rnd
def test_rnd_sym_scholar_invitation_details(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-009: the scholar sees the invitation with read-only details and uploaded documents."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "scholar_list.login", "scholar_list.menu_path",
        "scholar_list.event_row", "scholar_list.view_details_action",
        "scholar_list.detail_fields", "scholar_list.media_view_selector",
        "scholar_list.media_download_selector",
        "scholar_list.support_view_selector", "scholar_list.support_download_selector",
    )
    section = data["scholar_list"]
    login_as(section["login"])
    page_obj = _scholar_page(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_details(section["event_row"], section["view_details_action"])
    page_obj.expect_read_only_details(section["detail_fields"])
    page_obj.expect_documents_available(section["media_view_selector"],
                                        section["media_download_selector"])
    page_obj.expect_documents_available(section["support_view_selector"],
                                        section["support_download_selector"])


@pytest.mark.rnd
def test_rnd_sym_scholar_status_updates(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-010: the scholar's list status follows Scheduled -> Yet to Upload Details -> Approved."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "scholar_status_updates.login", "scholar_status_updates.menu_path",
        "scholar_status_updates.event_row",
        "scholar_status_updates.scheduled_status",
        "scholar_status_updates.yet_to_upload_status",
        "scholar_status_updates.approved_status",
        "invite.login", "invite.menu_path", "invite.filters",
        "event_details.scholar_row", "event_details.upload_action",
        "event_details.media_input", "event_details.media",
        "event_details.media_link_field", "event_details.media_link",
        "event_details.support_input", "event_details.support",
        "event_details.approve_selector", "event_details.success_selector",
    )
    scholar = data["scholar_status_updates"]
    details = data["event_details"]
    dcc = data["invite"]

    login_as(scholar["login"])
    scholar_page = _scholar_page(page, uucms_settings)
    scholar_page.open_from_menu(scholar["menu_path"])
    scholar_page.expect_status(scholar["event_row"],
                               scholar["scheduled_status"])

    # precondition: the event date & time has crossed, the row moves to
    # Yet to Upload Details on its own
    scholar_page.open_from_menu(scholar["menu_path"])
    scholar_page.expect_status(scholar["event_row"],
                               scholar["yet_to_upload_status"])

    login_as(dcc["login"])
    dcc_page = _invitation_page(page, uucms_settings)
    dcc_page.open_from_menu(dcc["menu_path"])
    dcc_page.apply_filters(dcc["filters"])
    dcc_page.open_event_details(details["scholar_row"],
                                details["upload_action"])
    details_page = _details_page(page, uucms_settings)
    details_page.upload_details(
        details["media_input"], details["media"],
        details["media_link_field"], details["media_link"],
        details["support_input"], details["support"],
    )
    details_page.approve(details["approve_selector"],
                         details["success_selector"])

    login_as(scholar["login"])
    scholar_page.open_from_menu(scholar["menu_path"])
    scholar_page.expect_status(scholar["event_row"],
                               scholar["approved_status"])


@pytest.mark.rnd
def test_rnd_sym_re_invite_rejected(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-011: a Rejected scholar is re-invited for the next symposium."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "re_invite.login", "re_invite.menu_path", "re_invite.filters",
        "re_invite.scholar_row", "re_invite.re_invite_action",
        "re_invite.actions", "re_invite.send_selector",
        "re_invite.success_selector",
    )
    section = data["re_invite"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.expect_status(section["scholar_row"], statuses.REJECTED)
    page_obj.send_re_invitation(
        section["scholar_row"], section["re_invite_action"],
        section["actions"], section["send_selector"],
        section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.apply_filters(section["filters"])
    page_obj.expect_status(section["scholar_row"], statuses.SCHEDULED)


@pytest.mark.rnd
def test_rnd_sym_only_approved_visible(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-012: only final-report-approved scholars are visible to the DCC."""
    data = _require_sym_data(
        load_test_data(DATA_FILE),
        "only_approved_visible.login", "only_approved_visible.menu_path",
        "only_approved_visible.filters", "only_approved_visible.present",
        "only_approved_visible.absent",
    )
    section = data["only_approved_visible"]
    login_as(section["login"])
    page_obj = _open_dcc_list(page, uucms_settings, section)
    page_obj.expect_scholars_listed(section["present"], section["absent"])


@pytest.mark.rnd
def test_rnd_sym_full_lifecycle(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-002/006: full DCC lifecycle invite -> upload details -> approve."""
    _require_sym_data(
        load_test_data(DATA_FILE),
        "invite.login", "invite.menu_path", "invite.filters",
        "invite.scholar_row", "invite.actions", "invite.send_selector",
        "event_details.login", "event_details.menu_path",
        "event_details.filters", "event_details.scholar_row",
        "event_details.upload_action", "event_details.media_input",
        "event_details.media", "event_details.media_link_field",
        "event_details.media_link", "event_details.support_input",
        "event_details.support", "event_details.approve_selector",
    )
    data = load_test_data(DATA_FILE)
    workflow = SymposiumWorkflow(page, uucms_settings, login_as)
    workflow.run_full_lifecycle(
        {"invite": data["invite"], "event_details": data["event_details"]}
    )


@pytest.mark.rnd
def test_rnd_sym_reject_reinvite_lifecycle(page, uucms_settings, login_as):
    """TC-SYMPOSIUM-007/011: invite -> reject -> send re-invitation."""
    _require_sym_data(
        load_test_data(DATA_FILE),
        "invite.login", "invite.menu_path", "invite.filters",
        "invite.scholar_row", "invite.actions", "invite.send_selector",
        "event_details.login", "event_details.menu_path",
        "event_details.filters", "event_details.scholar_row",
        "event_details.upload_action", "event_details.media_input",
        "event_details.media", "event_details.media_link_field",
        "event_details.media_link", "event_details.support_input",
        "event_details.support", "event_details.reject_selector",
        "re_invite.login", "re_invite.menu_path", "re_invite.filters",
        "re_invite.scholar_row", "re_invite.re_invite_action",
        "re_invite.actions", "re_invite.send_selector",
    )
    data = load_test_data(DATA_FILE)
    workflow = SymposiumWorkflow(page, uucms_settings, login_as)
    workflow.run_reject_reinvite(
        {"invite": data["invite"], "event_details": data["event_details"],
         "re_invite": data["re_invite"]}
    )
