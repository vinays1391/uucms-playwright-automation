"""Coursework and examination orchestration across roles.

Flow: chairperson review & approve of the candidate application, student
course registration, Registrar (Evaluation) course modification, internal
assessment marks and attendance, exam permission / exam-center approval /
QP-code update, Principal hall-ticket view, and Registrar (Evaluation)
evaluation marks direct entry. Stage data comes from
test_data/academics/coursework_examination.json.
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.academics.pages.attendance_page import AttendancePage
from uucms.modules.academics.pages.course_modification_page import (
    CourseModificationPage,
)
from uucms.modules.academics.pages.course_registration_page import (
    CourseRegistrationPage,
)
from uucms.modules.academics.pages.ia_marks_page import IaMarksPage
from uucms.modules.admission.pages.chairperson_approval_page import (
    ChairpersonApprovalPage,
)
from uucms.workflows.examination_workflow import ExamWorkflow


class CourseworkExaminationWorkflow:
    """Drives the Ph.D coursework-to-evaluation examination cycle."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.login_as = login_as
        self.chairperson_approval = ChairpersonApprovalPage(page, settings.timeout_ms)
        self.course_registration = CourseRegistrationPage(page, settings.timeout_ms)
        self.course_modification = CourseModificationPage(page, settings.timeout_ms)
        self.ia_marks = IaMarksPage(page, settings.timeout_ms)
        self.attendance = AttendancePage(page, settings.timeout_ms)
        self.exam_workflow = ExamWorkflow(page, settings, login_as)

    def _login(self, stage: Mapping[str, Any]) -> None:
        self.login_as(str(stage["login"]))

    def chairperson_reviews_and_approves(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.chairperson_approval.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.chairperson_approval.apply_filters(stage["filters"])
        self.chairperson_approval.view_student_details(
            str(stage["view_student_details_selector"])
        )
        self.chairperson_approval.review_and_approve(stage)

    def student_registers_courses(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.course_registration.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.course_registration.select_scheme(stage)
        self.course_registration.register_courses(stage)

    def registrar_modifies_student_courses(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.course_modification.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.course_modification.modify_student_courses(stage)

    def registrar_enters_ia_marks(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.ia_marks.open_from_menu(stage["menu_path"])
        self.ia_marks.enter_marks(stage)

    def registrar_enters_attendance(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.attendance.open_from_menu(stage["menu_path"])
        self.attendance.enter_attendance(stage)

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        self.chairperson_reviews_and_approves(data["review_approve"])
        self.student_registers_courses(data["course_registration"])
        self.registrar_modifies_student_courses(data["modify_student_courses"])
        self.registrar_enters_ia_marks(data["ia_marks"])
        self.registrar_enters_attendance(data["attendance"])
        self.exam_workflow.run_full_flow(data)
