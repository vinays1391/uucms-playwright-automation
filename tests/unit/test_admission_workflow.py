"""Unit tests for program-level-specific previous-education declarations."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from uucms.workflows.admission_workflow import AdmissionWorkflow
from uucms.workflows.phd_workflow import PhDAdmissionWorkflow


@pytest.mark.parametrize(
    ("program_level", "education_level"),
    [("UG", "PUC"), ("PG", "UG"), ("Ph.D.", "PG")],
)
def test_candidate_uses_declaration_for_previous_program_level(
    program_level: str, education_level: str
) -> None:
    workflow = AdmissionWorkflow.__new__(AdmissionWorkflow)
    workflow.settings = SimpleNamespace(captcha="12345")
    workflow.login_as = Mock()
    workflow.registration_details_page = Mock()
    workflow.registration_details_page.education_declaration_submitted.return_value = False
    declaration = {
        "submitted_check_selector": f"#{education_level}Submitted",
        "tab": f"Previous Education Details - {education_level}",
        "declaration_selector": f"#{education_level}declaration",
        "success_selector": f"#{education_level}Success",
    }
    stage = {
        "login": "candidate",
        "program_level": program_level,
        "user_menu_selector": "#userDropdown",
        "registration_details_text": "Registration Details",
        "education_declarations": {education_level: declaration},
        "captcha_selector": "#captcha",
        "submit_selector": "#submit",
        "ok_selector": "#ok",
    }

    result = workflow.candidate_submits_previous_education_declaration_if_pending(stage)

    assert result is False
    workflow.login_as.assert_called_once_with("candidate")
    workflow.registration_details_page.education_declaration_submitted.assert_called_once_with(
        declaration["submitted_check_selector"]
    )
    workflow.registration_details_page.submit_education_declaration.assert_called_once_with(
        declaration["tab"],
        declaration["declaration_selector"],
        "12345",
        "#captcha",
        "#submit",
        "#ok",
        declaration["success_selector"],
    )


def test_candidate_skips_previous_education_declaration_when_already_submitted() -> None:
    workflow = AdmissionWorkflow.__new__(AdmissionWorkflow)
    workflow.settings = SimpleNamespace(captcha=None)
    workflow.login_as = Mock()
    workflow.registration_details_page = Mock()
    workflow.registration_details_page.education_declaration_submitted.return_value = True
    stage = {
        "login": "candidate",
        "program_level": "PG",
        "user_menu_selector": "#userDropdown",
        "registration_details_text": "Registration Details",
        "education_declarations": {
            "UG": {"submitted_check_selector": "#UGSubmitted"},
        },
    }

    result = workflow.candidate_submits_previous_education_declaration_if_pending(stage)

    assert result is True
    workflow.registration_details_page.submit_education_declaration.assert_not_called()


def test_candidate_rejects_unknown_program_level() -> None:
    workflow = AdmissionWorkflow.__new__(AdmissionWorkflow)
    workflow.login_as = Mock()
    workflow.registration_details_page = Mock()
    stage = {
        "login": "candidate",
        "program_level": "Diploma",
        "user_menu_selector": "#userDropdown",
        "registration_details_text": "Registration Details",
    }

    with pytest.raises(ValueError, match="Unsupported admission program level"):
        workflow.candidate_submits_previous_education_declaration_if_pending(stage)


def test_phd_workflow_composes_candidate_workflow() -> None:
    workflow = PhDAdmissionWorkflow.__new__(PhDAdmissionWorkflow)
    workflow.candidate = Mock()
    workflow.chairperson_views_entrance_candidates = Mock()
    workflow.chairperson_sets_cut_off_marks = Mock()
    workflow.chairperson_reviews_and_approves = Mock()
    workflow.chairperson_enters_entrance_marks = Mock()
    workflow.registrar_approves_or_rejects = Mock()
    workflow.chairperson_invites_interview = Mock()
    workflow.chairperson_enters_interview_marks = Mock()
    workflow.registrar_approves_interview_marks = Mock()
    workflow.chairperson_confirms_student_invite = Mock()
    workflow.chairperson_verifies_documents = Mock()
    workflow.candidate_submits_final_payment = Mock()
    data = {
        "create_application": {},
        "education_declaration": {},
        "application_details": {},
        "offline_payment": {},
        "entrance_view": {},
        "cut_off_marks": {},
        "review_approve": {},
        "entrance_marks": {},
        "registrar_action": {},
        "interview_invite": {},
        "interview_marks": {},
        "interview_marks_approval": {},
        "student_invite": {},
        "document_verification": {},
        "final_payment": {},
    }

    workflow.run_full_flow(data)

    workflow.candidate.candidate_creates_application.assert_called_once_with(
        data["create_application"]
    )
    workflow.candidate.candidate_submits_previous_education_declaration_if_pending.assert_called_once_with(
        data["education_declaration"]
    )
    workflow.candidate.candidate_completes_application.assert_called_once_with(
        data["application_details"]
    )
    workflow.candidate.candidate_submits_offline_payment.assert_called_once_with(
        data["offline_payment"]
    )
    workflow.chairperson_views_entrance_candidates.assert_called_once_with(
        data["entrance_view"]
    )
    workflow.chairperson_sets_cut_off_marks.assert_called_once_with(
        data["cut_off_marks"]
    )
    workflow.chairperson_reviews_and_approves.assert_called_once_with(
        data["review_approve"]
    )
    workflow.chairperson_enters_entrance_marks.assert_called_once_with(
        data["entrance_marks"]
    )
    workflow.registrar_approves_or_rejects.assert_called_once_with(
        data["registrar_action"]
    )
    workflow.chairperson_invites_interview.assert_called_once_with(
        data["interview_invite"]
    )
    workflow.chairperson_enters_interview_marks.assert_called_once_with(
        data["interview_marks"]
    )
    workflow.registrar_approves_interview_marks.assert_called_once_with(
        data["interview_marks_approval"]
    )
    workflow.chairperson_confirms_student_invite.assert_called_once_with(
        data["student_invite"]
    )
    workflow.chairperson_verifies_documents.assert_called_once_with(
        data["document_verification"]
    )
    workflow.candidate_submits_final_payment.assert_called_once_with(
        data["final_payment"]
    )
