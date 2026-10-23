"""Unit tests for exam-screen orchestration and role routing."""

from unittest.mock import Mock

import pytest

from uucms.workflows.examination_workflow import ExamWorkflow


@pytest.mark.parametrize(
    ("method_name", "page_attribute", "page_method", "role"),
    [
        (
            "permit_students_to_exam",
            "permit_students_page",
            "permit_students",
            "registrar_evaluation",
        ),
        (
            "approve_exam_center_students",
            "exam_center_page",
            "approve_students",
            "registrar_evaluation",
        ),
        ("update_qp_codes", "qp_code_page", "update_codes", "registrar_evaluation"),
        (
            "enter_evaluation_marks",
            "evaluation_marks_page",
            "enter_marks",
            "registrar_evaluation",
        ),
        (
            "view_hall_tickets",
            "hall_ticket_page",
            "view_hall_tickets",
            "principal",
        ),
    ],
)
def test_exam_action_uses_screen_page_and_designated_role(
    method_name: str, page_attribute: str, page_method: str, role: str
) -> None:
    workflow = ExamWorkflow.__new__(ExamWorkflow)
    workflow.login_as = Mock()
    page_object = Mock()
    setattr(workflow, page_attribute, page_object)
    stage = {"login": "incorrect_configured_role"}

    getattr(workflow, method_name)(stage)

    workflow.login_as.assert_called_once_with(role)
    getattr(page_object, page_method).assert_called_once_with(stage)


def test_exam_workflow_full_flow_runs_each_exam_screen_in_order() -> None:
    workflow = ExamWorkflow.__new__(ExamWorkflow)
    workflow.permit_students_to_exam = Mock()
    workflow.approve_exam_center_students = Mock()
    workflow.update_qp_codes = Mock()
    workflow.view_hall_tickets = Mock()
    workflow.enter_evaluation_marks = Mock()
    data = {
        "permit_exam": {},
        "exam_center_students": {},
        "exam_qp_codes": {},
        "hall_tickets": {},
        "evaluation_marks": {},
    }

    workflow.run_full_flow(data)

    workflow.permit_students_to_exam.assert_called_once_with(data["permit_exam"])
    workflow.approve_exam_center_students.assert_called_once_with(
        data["exam_center_students"]
    )
    workflow.update_qp_codes.assert_called_once_with(data["exam_qp_codes"])
    workflow.view_hall_tickets.assert_called_once_with(data["hall_tickets"])
    workflow.enter_evaluation_marks.assert_called_once_with(data["evaluation_marks"])
