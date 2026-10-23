"""R&D Phase-1 PERMUSN test cases: permanent USN approval chain.

University Admin -> Superintendent -> Registrar (Admin) -> permanent USN
assigned and student notified. Role logins come from the "roles" mapping
in test_data/login/LoginData.json via the login_as fixture.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.constants.menu_paths.research_development import PROGRESS_REPORT
from uucms.modules.common.menu_page import MenuPage
from uucms.modules.research_development.pages.permusn.permanent_usn_page import PermanentUsnPage
from utils.json_reader import require_fields
from uucms.workflows.research_development.phd_admission_workflow import PermanentUsnWorkflow

DATA_FILE = "rnd/permanent_usn.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_permusn_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _open_usn_screen(page, uucms_settings, section) -> PermanentUsnPage:
    page_obj = PermanentUsnPage(page, uucms_settings.timeout_ms)
    if section.get("menu_path"):
        page_obj.open_from_menu(section["menu_path"])
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


@pytest.mark.rnd
def test_rnd_permusn_university_admin_sends(page, uucms_settings, login_as):
    """TC-PERMUSN-001: University Admin sends the provisional USN for Superintendent approval."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "university_admin.login", "university_admin.menu_path",
        "university_admin.student_row", "university_admin.send_selector",
        "university_admin.success_selector", "university_admin.pending_status",
    )
    login_as(data["university_admin"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["university_admin"])
    section = data["university_admin"]
    page_obj.send_for_approval(
        section["student_row"], section["send_selector"], section["success_selector"]
    )
    page_obj.expect_row_text(section["student_row"], section["pending_status"])


@pytest.mark.rnd
def test_rnd_permusn_only_approved_synopsis_eligible(page, uucms_settings, login_as):
    """TC-PERMUSN-002: only synopsis-approved students are eligible for permanent USN."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "university_admin.login", "eligibility.menu_path",
        "eligibility.present", "eligibility.absent",
    )
    login_as(data["university_admin"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["eligibility"])
    page_obj.expect_students_listed(data["eligibility"]["present"], data["eligibility"]["absent"])


@pytest.mark.rnd
def test_rnd_permusn_superintendent_approves(page, uucms_settings, login_as):
    """TC-PERMUSN-003: Superintendent approves and forwards to Registrar (Admin)."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "superintendent.login", "superintendent.menu_path",
        "superintendent.request_row", "superintendent.review_action",
        "superintendent.approve_selector", "superintendent.success_selector",
        "superintendent.forwarded_status",
    )
    login_as(data["superintendent"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["superintendent"])
    section = data["superintendent"]
    page_obj.approve_request(
        section["request_row"], section["review_action"],
        section["approve_selector"], section["success_selector"],
    )
    page_obj.expect_row_text(section["request_row"], section["forwarded_status"])


@pytest.mark.rnd
def test_rnd_permusn_registrar_assigns_usn(page, uucms_settings, login_as):
    """TC-PERMUSN-004: Registrar (Admin) approval assigns the permanent USN."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "registrar_admin.login", "registrar_admin.menu_path",
        "registrar_admin.request_row", "registrar_admin.review_action",
        "registrar_admin.approve_selector", "registrar_admin.success_selector",
        "registrar_admin.completed_status",
        "usn_verification.login", "usn_verification.menu_path",
        "usn_verification.permanent_usn_selector",
    )
    login_as(data["registrar_admin"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["registrar_admin"])
    section = data["registrar_admin"]
    page_obj.approve_request(
        section["request_row"], section["review_action"],
        section["approve_selector"], section["success_selector"],
    )
    page_obj.expect_row_text(section["request_row"], section["completed_status"])
    verification = _open_usn_screen(page, uucms_settings, data["usn_verification"])
    usn = verification.read_permanent_usn(data["usn_verification"]["permanent_usn_selector"])
    assert usn, "No permanent USN was recorded after Registrar (Admin) approval"


@pytest.mark.rnd
def test_rnd_permusn_usn_format_uniqueness(page, uucms_settings, login_as):
    """TC-PERMUSN-005: permanent USN follows the configured format, is unique and differs from the provisional USN."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "usn_verification.login", "usn_verification.menu_path",
        "usn_verification.permanent_usn_selector", "usn_verification.usn_format",
        "usn_verification.provisional_usn", "usn_verification.all_usn_cells_selector",
    )
    login_as(data["usn_verification"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["usn_verification"])
    section = data["usn_verification"]
    usn = page_obj.read_permanent_usn(section["permanent_usn_selector"])
    page_obj.expect_usn_format(usn, section["usn_format"])
    page_obj.expect_usn_different_from(usn, section["provisional_usn"])
    usns = page_obj.collect_usns(section["all_usn_cells_selector"])
    assert len(set(usns)) == len(usns), f"Permanent USN is not unique: {usns}"


@pytest.mark.rnd
def test_rnd_permusn_student_notified(page, uucms_settings, login_as):
    """TC-PERMUSN-006: the student is notified of the assigned permanent USN."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "student.login", "student.notification_selector", "student.permanent_usn",
    )
    login_as(data["student"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["student"])
    page_obj.expect_notification(
        data["student"]["notification_selector"], data["student"]["permanent_usn"]
    )


@pytest.mark.rnd
def test_rnd_permusn_scholar_status_after_usn(page, uucms_settings, login_as):
    """TC-PERMUSN-007: the student is treated as a Ph.D scholar after the permanent USN."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "student.login", "student.profile_selector", "student.scholar_status_text",
        "student.progress_report_row",
    )
    login_as(data["student"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["student"])
    page_obj.expect_scholar_status(
        data["student"]["profile_selector"], data["student"]["scholar_status_text"]
    )
    MenuPage(page, uucms_settings.timeout_ms).open_menu(PROGRESS_REPORT)
    expect(page.locator(data["student"]["progress_report_row"])).to_be_visible()


@pytest.mark.rnd
def test_rnd_permusn_superintendent_rejects(page, uucms_settings, login_as):
    """TC-PERMUSN-008: Superintendent rejects the permanent USN request."""
    data = _require_permusn_data(
        load_test_data(DATA_FILE),
        "superintendent.login", "superintendent.menu_path",
        "superintendent.request_row", "superintendent.review_action",
        "superintendent.remarks_field", "superintendent.reject_remarks",
        "superintendent.reject_selector", "superintendent.success_selector",
        "superintendent.rejected_status",
    )
    login_as(data["superintendent"]["login"])
    page_obj = _open_usn_screen(page, uucms_settings, data["superintendent"])
    section = data["superintendent"]
    page_obj.reject_request(
        section["request_row"], section["review_action"],
        section["remarks_field"], section["reject_remarks"],
        section["reject_selector"], section["success_selector"],
    )
    page_obj.expect_row_text(section["request_row"], section["rejected_status"])


@pytest.mark.rnd
def test_rnd_permusn_full_flow(page, uucms_settings, login_as):
    """TC-PERMUSN-001/003/004/005/006/007: full University Admin -> Superintendent ->
    Registrar (Admin) chain, USN verified, student notified as Ph.D scholar."""
    _require_permusn_data(
        load_test_data(DATA_FILE),
        "university_admin.login", "university_admin.menu_path",
        "university_admin.student_row", "university_admin.send_selector",
        "university_admin.success_selector",
        "superintendent.login", "superintendent.menu_path",
        "superintendent.request_row", "superintendent.review_action",
        "superintendent.approve_selector",
        "registrar_admin.login", "registrar_admin.menu_path",
        "registrar_admin.request_row", "registrar_admin.review_action",
        "registrar_admin.approve_selector",
        "usn_verification.login", "usn_verification.menu_path",
        "usn_verification.permanent_usn_selector", "usn_verification.usn_format",
        "usn_verification.provisional_usn", "usn_verification.all_usn_cells_selector",
        "student.login", "student.notification_selector",
        "student.profile_selector", "student.scholar_status_text",
    )
    data = load_test_data(DATA_FILE)
    workflow = PermanentUsnWorkflow(page, uucms_settings, login_as)
    workflow.run_full_flow(data)
