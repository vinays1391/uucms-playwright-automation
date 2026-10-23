"""Exam-module orchestration using one role login and screen-specific POMs."""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.exam.pages.exam_center_page import ExamCenterPage
from uucms.modules.exam.pages.evaluation_marks_page import EvaluationMarksPage
from uucms.modules.exam.pages.hall_ticket_page import HallTicketPage
from uucms.modules.exam.pages.permit_students_page import PermitStudentsPage
from uucms.modules.exam.pages.qp_code_page import QpCodePage


class ExamWorkflow:
    """Orchestrates Exam screens under Registrar (Evaluation) and Principal roles."""

    REGISTRAR_EVALUATION_ROLE = "registrar_evaluation"
    PRINCIPAL_ROLE = "principal"

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.login_as = login_as
        self.permit_students_page = PermitStudentsPage(page, settings.timeout_ms)
        self.exam_center_page = ExamCenterPage(page, settings.timeout_ms)
        self.qp_code_page = QpCodePage(page, settings.timeout_ms)
        self.evaluation_marks_page = EvaluationMarksPage(page, settings.timeout_ms)
        self.hall_ticket_page = HallTicketPage(page, settings.timeout_ms)

    def permit_students_to_exam(self, stage: Mapping[str, Any]) -> None:
        self.login_as(self.REGISTRAR_EVALUATION_ROLE)
        self.permit_students_page.permit_students(stage)

    def approve_exam_center_students(self, stage: Mapping[str, Any]) -> None:
        self.login_as(self.REGISTRAR_EVALUATION_ROLE)
        self.exam_center_page.approve_students(stage)

    def update_qp_codes(self, stage: Mapping[str, Any]) -> None:
        self.login_as(self.REGISTRAR_EVALUATION_ROLE)
        self.qp_code_page.update_codes(stage)

    def enter_evaluation_marks(self, stage: Mapping[str, Any]) -> None:
        self.login_as(self.REGISTRAR_EVALUATION_ROLE)
        self.evaluation_marks_page.enter_marks(stage)

    def view_hall_tickets(self, stage: Mapping[str, Any]) -> None:
        self.login_as(self.PRINCIPAL_ROLE)
        self.hall_ticket_page.view_hall_tickets(stage)

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        self.permit_students_to_exam(data["permit_exam"])
        self.approve_exam_center_students(data["exam_center_students"])
        self.update_qp_codes(data["exam_qp_codes"])
        self.view_hall_tickets(data["hall_tickets"])
        self.enter_evaluation_marks(data["evaluation_marks"])
