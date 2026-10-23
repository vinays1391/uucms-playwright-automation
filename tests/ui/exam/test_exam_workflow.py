"""Exam screen tests for Registrar (Evaluation) and Principal roles."""

import pytest

from config.settings import load_test_data
from utils.json_reader import require_fields
from uucms.workflows.examination_workflow import ExamWorkflow

DATA_FILE = "academics/coursework_examination.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_exam_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _workflow(page, uucms_settings, login_as) -> ExamWorkflow:
    return ExamWorkflow(page, uucms_settings, login_as)


@pytest.mark.exam
def test_exam_registrar_permits_students(page, uucms_settings, login_as):
    """TC-EXAM-001: Registrar (Evaluation) permits eligible students to take the exam."""
    data = _require_exam_data(
        load_test_data(DATA_FILE),
        "permit_exam.menu_path", "permit_exam.filters",
        "permit_exam.declaration_checkbox", "permit_exam.submit_selector",
        "permit_exam.confirm_selector", "permit_exam.success_selector",
    )
    _workflow(page, uucms_settings, login_as).permit_students_to_exam(
        data["permit_exam"]
    )


@pytest.mark.exam
def test_exam_registrar_approves_exam_center_students(page, uucms_settings, login_as):
    """TC-EXAM-002: Registrar (Evaluation) approves exam-center student allocations."""
    data = _require_exam_data(
        load_test_data(DATA_FILE),
        "exam_center_students.menu_path", "exam_center_students.filters",
        "exam_center_students.confirm_selector",
        "exam_center_students.success_selector",
    )
    _workflow(page, uucms_settings, login_as).approve_exam_center_students(
        data["exam_center_students"]
    )


@pytest.mark.exam
def test_exam_registrar_updates_qp_codes(page, uucms_settings, login_as):
    """TC-EXAM-003: Registrar (Evaluation) updates the exam question-paper codes."""
    data = _require_exam_data(
        load_test_data(DATA_FILE),
        "exam_qp_codes.menu_path", "exam_qp_codes.filters",
        "exam_qp_codes.view_selector", "exam_qp_codes.update_selector",
        "exam_qp_codes.success_selector",
    )
    _workflow(page, uucms_settings, login_as).update_qp_codes(
        data["exam_qp_codes"]
    )


@pytest.mark.exam
def test_exam_principal_views_hall_tickets(page, uucms_settings, login_as):
    """TC-EXAM-004: Principal views hall tickets and checks student eligibility."""
    data = _require_exam_data(
        load_test_data(DATA_FILE),
        "hall_tickets.menu_path", "hall_tickets.filters",
        "hall_tickets.view_details_selector",
        "hall_tickets.check_eligibility_selector",
        "hall_tickets.success_selector",
    )
    _workflow(page, uucms_settings, login_as).view_hall_tickets(
        data["hall_tickets"]
    )


@pytest.mark.exam
def test_exam_registrar_enters_evaluation_marks(page, uucms_settings, login_as):
    """TC-EXAM-005: Registrar (Evaluation) enters and saves evaluation marks."""
    data = _require_exam_data(
        load_test_data(DATA_FILE),
        "evaluation_marks.menu_path", "evaluation_marks.filters",
        "evaluation_marks.view_selector", "evaluation_marks.enter_marks_selector",
        "evaluation_marks.college_filters", "evaluation_marks.marks_fields",
        "evaluation_marks.save_selector", "evaluation_marks.confirm_selector",
        "evaluation_marks.ok_selector", "evaluation_marks.success_selector",
    )
    _workflow(page, uucms_settings, login_as).enter_evaluation_marks(
        data["evaluation_marks"]
    )
