"""Ph.D admission module test cases: candidate application to final payment."""

import pytest

from config.settings import load_test_data
from utils.json_reader import require_fields
from uucms.workflows.admission_workflow import AdmissionWorkflow
from uucms.workflows.phd_workflow import PhDAdmissionWorkflow

DATA_FILE = "admission/phd_admission.json"
DATA_PATH = f"test_data/{DATA_FILE}"
MULTI_DATA_FILE = "admission/phd_admission_multi.json"
MULTI_DATA_PATH = f"test_data/{MULTI_DATA_FILE}"

FULL_FLOW_STAGES = (
    "create_application", "education_declaration", "application_details",
    "offline_payment", "entrance_view", "cut_off_marks", "review_approve",
    "entrance_marks", "registrar_action", "interview_invite", "interview_marks",
    "interview_marks_approval", "student_invite", "document_verification",
    "final_payment",
)


def _require_admission_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _workflow(page, uucms_settings, login_as) -> PhDAdmissionWorkflow:
    return PhDAdmissionWorkflow(page, uucms_settings, login_as)


def _candidate_workflow(page, uucms_settings, login_as) -> AdmissionWorkflow:
    return AdmissionWorkflow(page, uucms_settings, login_as)


@pytest.mark.admission
def test_phd_admission_candidate_creates_application(page, uucms_settings, login_as):
    """TC-PHADMISSION-001: candidate creates a Ph.D application (program level, university, program)."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "create_application.login", "create_application.menu_entry_selector",
        "create_application.menu_entry_text", "create_application.create_button",
        "create_application.actions", "create_application.ok_selector",
        "create_application.success_selector",
    )
    _candidate_workflow(page, uucms_settings, login_as).candidate_creates_application(
        data["create_application"]
    )


@pytest.mark.admission
def test_phd_admission_candidate_previous_education_declaration(page, uucms_settings, login_as):
    """TC-PHADMISSION-002: candidate submits the previous-education declaration required by the program level."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "education_declaration.login", "education_declaration.program_level",
        "education_declaration.user_menu_selector",
        "education_declaration.registration_details_text",
        "education_declaration.education_declarations.PG.submitted_check_selector",
        "education_declaration.education_declarations.PG.tab",
        "education_declaration.education_declarations.PG.declaration_selector",
        "education_declaration.education_declarations.PG.success_selector",
        "education_declaration.captcha_selector",
        "education_declaration.submit_selector", "education_declaration.ok_selector",
    )
    _candidate_workflow(
        page, uucms_settings, login_as
    ).candidate_submits_previous_education_declaration_if_pending(
        data["education_declaration"]
    )


@pytest.mark.admission
def test_phd_admission_candidate_completes_application(page, uucms_settings, login_as):
    """TC-PHADMISSION-003: candidate completes the application (cycle, department, discipline) and confirms the declaration."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "application_details.login", "application_details.menu_entry_selector",
        "application_details.menu_entry_text", "application_details.create_button",
        "application_details.actions", "application_details.submit_selector",
        "application_details.discipline_selector", "application_details.discipline_value",
        "application_details.preview_submit_selector",
        "application_details.declaration_checkbox",
        "application_details.confirm_selector", "application_details.ok_selector",
        "application_details.success_selector",
    )
    _candidate_workflow(page, uucms_settings, login_as).candidate_completes_application(
        data["application_details"]
    )


@pytest.mark.admission
def test_phd_admission_candidate_offline_payment(page, uucms_settings, login_as):
    """TC-PHADMISSION-004: candidate submits the offline admission payment with challan details and receipt."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "offline_payment.login", "offline_payment.menu_entry_selector",
        "offline_payment.menu_entry_text", "offline_payment.view_application_button",
        "offline_payment.offline_payment_link", "offline_payment.challan_field",
        "offline_payment.challan_value", "offline_payment.amount_field",
        "offline_payment.amount_value", "offline_payment.payment_date_day",
        "offline_payment.receipt_upload_selector", "offline_payment.receipt_file",
        "offline_payment.submit_selector", "offline_payment.ok_selector",
        "offline_payment.success_selector",
    )
    _candidate_workflow(page, uucms_settings, login_as).candidate_submits_offline_payment(
        data["offline_payment"]
    )


@pytest.mark.admission
def test_phd_admission_chairperson_views_entrance_candidates(page, uucms_settings, login_as):
    """TC-PHADMISSION-005: department chairperson views the Ph.D candidates for the cycle and department."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "entrance_view.login", "entrance_view.menu_path",
        "entrance_view.filters", "entrance_view.view_student_details_selector",
        "entrance_view.student_row",
    )
    _workflow(page, uucms_settings, login_as).chairperson_views_entrance_candidates(data["entrance_view"])


@pytest.mark.admission
def test_phd_admission_chairperson_sets_cut_off_marks(page, uucms_settings, login_as):
    """TC-PHADMISSION-006: department chairperson sets the Ph.D cut-off marks for the cycle, level, program and department."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "cut_off_marks.login", "cut_off_marks.menu_path",
        "cut_off_marks.filters", "cut_off_marks.edit_action_selector",
        "cut_off_marks.back_selector", "cut_off_marks.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_sets_cut_off_marks(data["cut_off_marks"])


@pytest.mark.admission
def test_phd_admission_chairperson_reviews_and_approves(page, uucms_settings, login_as):
    """TC-PHADMISSION-007: department chairperson reviews and approves the application and offline payment."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "review_approve.login", "review_approve.menu_path",
        "review_approve.filters", "review_approve.view_student_details_selector",
        "review_approve.review_action_selector", "review_approve.confirm_selector",
        "review_approve.approve_selector", "review_approve.ok_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_reviews_and_approves(data["review_approve"])


@pytest.mark.admission
def test_phd_admission_chairperson_enters_entrance_marks(page, uucms_settings, login_as):
    """TC-PHADMISSION-008: department chairperson enters the entrance exam marks and sends them for registrar approval."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "entrance_marks.login", "entrance_marks.menu_path",
        "entrance_marks.filters", "entrance_marks.view_student_details_selector",
        "entrance_marks.edit_marks_selector", "entrance_marks.marks_fields",
        "entrance_marks.save_marks_selector", "entrance_marks.confirm_selector",
        "entrance_marks.ok_selector", "entrance_marks.send_registrar_selector",
        "entrance_marks.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_enters_entrance_marks(data["entrance_marks"])


@pytest.mark.admission
def test_phd_admission_registrar_approves(page, uucms_settings, login_as):
    """TC-PHADMISSION-009: registrar (admin) approves or rejects the Ph.D entrance marks."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "registrar_action.login", "registrar_action.menu_path",
        "registrar_action.approve_selector", "registrar_action.remarks_field",
        "registrar_action.remarks_value", "registrar_action.submit_selector",
        "registrar_action.success_selector",
    )
    _workflow(page, uucms_settings, login_as).registrar_approves_or_rejects(data["registrar_action"])


@pytest.mark.admission
def test_phd_admission_chairperson_invites_interview(page, uucms_settings, login_as):
    """TC-PHADMISSION-010: department chairperson invites the selected Ph.D candidates for the interview."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "interview_invite.login", "interview_invite.menu_path",
        "interview_invite.filters", "interview_invite.view_student_details_selector",
        "interview_invite.students", "interview_invite.send_selector",
        "interview_invite.confirm_selector", "interview_invite.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_invites_interview(
        data["interview_invite"]
    )


@pytest.mark.admission
def test_phd_admission_chairperson_enters_interview_marks(page, uucms_settings, login_as):
    """TC-PHADMISSION-011: department chairperson enters the interview marks and sends them for registrar approval."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "interview_marks.login", "interview_marks.menu_path",
        "interview_marks.filters", "interview_marks.view_student_details_selector",
        "interview_marks.edit_marks_selector", "interview_marks.marks_fields",
        "interview_marks.save_marks_selector", "interview_marks.confirm_selector",
        "interview_marks.ok_selector", "interview_marks.send_registrar_selector",
        "interview_marks.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_enters_interview_marks(
        data["interview_marks"]
    )


@pytest.mark.admission
def test_phd_admission_registrar_approves_interview_marks(page, uucms_settings, login_as):
    """TC-PHADMISSION-012: registrar (admin) approves or rejects the Ph.D interview marks."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "interview_marks_approval.login", "interview_marks_approval.menu_path",
        "interview_marks_approval.approve_selector",
        "interview_marks_approval.remarks_field",
        "interview_marks_approval.remarks_value",
        "interview_marks_approval.submit_selector",
        "interview_marks_approval.success_selector",
    )
    _workflow(page, uucms_settings, login_as).registrar_approves_interview_marks(
        data["interview_marks_approval"]
    )


@pytest.mark.admission
def test_phd_admission_chairperson_confirms_student_invite(page, uucms_settings, login_as):
    """TC-PHADMISSION-013: selected students are sent the interview invite with the configured date."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "student_invite.login", "student_invite.menu_path",
        "student_invite.filters", "student_invite.view_student_details_selector",
        "student_invite.students", "student_invite.send_selector",
        "student_invite.ok_selector", "student_invite.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_confirms_student_invite(
        data["student_invite"]
    )


@pytest.mark.admission
def test_phd_admission_chairperson_verifies_documents(page, uucms_settings, login_as):
    """TC-PHADMISSION-014: admission documents are verified and the Ph.D details (discipline, AOR, guide, category, quota, type) are mapped."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "document_verification.login", "document_verification.menu_path",
        "document_verification.filters", "document_verification.preview_row_selector",
        "document_verification.preview_button", "document_verification.documents",
        "document_verification.document_ok_selector",
        "document_verification.verification_date_day",
        "document_verification.phd_mapping",
        "document_verification.submit_selector",
        "document_verification.success_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_verifies_documents(
        data["document_verification"]
    )


@pytest.mark.admission
def test_phd_admission_candidate_submits_final_payment(page, uucms_settings, login_as):
    """TC-PHADMISSION-015: candidate submits the final offline payment for the admitted application."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        "final_payment.login", "final_payment.menu_entry_selector",
        "final_payment.menu_entry_text", "final_payment.view_application_button",
        "final_payment.application_row_action",
        "final_payment.offline_payment_control", "final_payment.challan_field",
        "final_payment.challan_value", "final_payment.amount_field",
        "final_payment.amount_value", "final_payment.payment_date_day",
        "final_payment.receipt_upload_selector", "final_payment.receipt_file",
        "final_payment.submit_selector", "final_payment.ok_selector",
        "final_payment.success_selector",
    )
    _workflow(page, uucms_settings, login_as).candidate_submits_final_payment(
        data["final_payment"]
    )


@pytest.mark.admission
def test_phd_admission_full_flow(page, uucms_settings, login_as):
    """TC-PHADMISSION-016: full Ph.D admission flow from application to final offline payment."""
    data = _require_admission_data(
        load_test_data(DATA_FILE),
        *[f"{stage}.login" for stage in FULL_FLOW_STAGES],
    )
    _workflow(page, uucms_settings, login_as).run_full_flow(data)


def _has_placeholders(node) -> bool:
    if isinstance(node, str):
        return "REPLACE_WITH" in node
    if isinstance(node, dict):
        return any(_has_placeholders(value) for value in node.values())
    if isinstance(node, list):
        return any(_has_placeholders(value) for value in node)
    return False


@pytest.mark.admission
def test_phd_admission_multi_candidate_full_flow(
    page, uucms_settings, login_as, role_manager
):
    """TC-PHADMISSION-017: full Ph.D admission flow for every roster candidate (groups share program/cycle/department)."""
    data = load_test_data(MULTI_DATA_FILE)
    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError(
            f"{MULTI_DATA_PATH} has no candidates. Fill in "
            "test_data/admission/candidates_roster.csv and the group values "
            "in phd_admission_multi.template.json, then run "
            "python scripts/generate_phd_multi_data.py"
        )
    if _has_placeholders(data):
        raise ValueError(
            f"{MULTI_DATA_PATH} still contains REPLACE_WITH placeholders; "
            "complete phd_admission_multi.template.json and regenerate"
        )
    missing_roles = []
    for candidate in candidates:
        role = str(candidate.get("login", ""))
        try:
            role_manager.credentials_for(role)
        except ValueError:
            missing_roles.append(role)
    if missing_roles:
        raise ValueError(
            "Login roles not registered in test_data/login/LoginData.json: "
            + ", ".join(sorted(set(missing_roles)))
            + ". Run python scripts/register_candidate_roles.py"
        )
    _workflow(page, uucms_settings, login_as).run_multi_candidate_flow(data)
