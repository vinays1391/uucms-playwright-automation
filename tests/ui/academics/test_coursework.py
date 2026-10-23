"""Coursework and examination module test cases: registration to evaluation marks."""

import pytest

from config.settings import load_test_data
from utils.json_reader import require_fields
from uucms.workflows.coursework_workflow import CourseworkExaminationWorkflow

DATA_FILE = "academics/coursework_examination.json"
DATA_PATH = f"test_data/{DATA_FILE}"

FULL_FLOW_STAGES = (
    "review_approve", "course_registration", "modify_student_courses",
    "ia_marks", "attendance",
)


def _require_coursework_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _workflow(page, uucms_settings, login_as) -> CourseworkExaminationWorkflow:
    return CourseworkExaminationWorkflow(page, uucms_settings, login_as)


@pytest.mark.academics
def test_coursework_chairperson_reviews_and_approves(page, uucms_settings, login_as):
    """TC-COURSEWORK-001: department chairperson reviews and approves the Ph.D candidate application and payment."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        "review_approve.login", "review_approve.menu_path",
        "review_approve.filters", "review_approve.view_student_details_selector",
        "review_approve.review_action_selector", "review_approve.confirm_selector",
        "review_approve.approve_selector", "review_approve.ok_selector",
    )
    _workflow(page, uucms_settings, login_as).chairperson_reviews_and_approves(
        data["review_approve"]
    )


@pytest.mark.academics
def test_coursework_student_registers_courses(page, uucms_settings, login_as):
    """TC-COURSEWORK-002: student selects the course-registration scheme and registers the term courses."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        "course_registration.login", "course_registration.menu_path",
        "course_registration.scheme_selector", "course_registration.scheme_value",
        "course_registration.save_selector", "course_registration.confirm_selector",
        "course_registration.ok_selector", "course_registration.course_list_selector",
        "course_registration.courses", "course_registration.submit_selector",
        "course_registration.success_selector",
    )
    _workflow(page, uucms_settings, login_as).student_registers_courses(
        data["course_registration"]
    )


@pytest.mark.academics
def test_coursework_registrar_modifies_student_courses(page, uucms_settings, login_as):
    """TC-COURSEWORK-003: registrar (evaluation) looks up the student and submits the student-course modification."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        "modify_student_courses.login", "modify_student_courses.menu_path",
        "modify_student_courses.student_reg_no_field",
        "modify_student_courses.submit_selector",
        "modify_student_courses.course_registration_selector",
        "modify_student_courses.confirm_selector", "modify_student_courses.ok_selector",
        "modify_student_courses.success_selector",
        "modify_student_courses.back_selector",
    )
    _workflow(page, uucms_settings, login_as).registrar_modifies_student_courses(
        data["modify_student_courses"]
    )


@pytest.mark.academics
def test_coursework_registrar_enters_ia_marks(page, uucms_settings, login_as):
    """TC-COURSEWORK-004: registrar (evaluation) enters and saves the internal assessment marks."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        "ia_marks.login", "ia_marks.menu_path", "ia_marks.edit_selector",
        "ia_marks.marks_fields", "ia_marks.save_selector",
        "ia_marks.confirm_selector", "ia_marks.ok_selector",
        "ia_marks.success_selector", "ia_marks.back_selector",
    )
    _workflow(page, uucms_settings, login_as).registrar_enters_ia_marks(data["ia_marks"])


@pytest.mark.academics
def test_coursework_registrar_enters_attendance(page, uucms_settings, login_as):
    """TC-COURSEWORK-005: registrar (evaluation) enters the classes conducted and attended per lecture and saves the attendance."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        "attendance.login", "attendance.menu_path", "attendance.edit_selector",
        "attendance.classes_field", "attendance.attended_field",
        "attendance.lectures", "attendance.save_selector",
        "attendance.confirm_selector", "attendance.ok_selector",
        "attendance.success_selector",
    )
    _workflow(page, uucms_settings, login_as).registrar_enters_attendance(
        data["attendance"]
    )


@pytest.mark.academics
def test_coursework_full_flow(page, uucms_settings, login_as):
    """TC-COURSEWORK-011: full coursework-to-evaluation flow from chairperson approval to evaluation marks entry."""
    data = _require_coursework_data(
        load_test_data(DATA_FILE),
        *[f"{stage}.login" for stage in FULL_FLOW_STAGES],
    )
    _workflow(page, uucms_settings, login_as).run_full_flow(data)
