"""R&D Phase-1 SYNOPSIS test cases: submission and multi-stage approval chain.

Reviewers: Guide -> Co-Guide (if assigned) -> Department Chairperson ->
Doctoral Committee Chairperson. Role logins come from the "roles"
mapping in test_data/login/LoginData.json via the login_as fixture.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.constants import roles, statuses
from uucms.modules.research_development.pages.synopsis.synopsis_review_page import SynopsisReviewPage
from uucms.modules.research_development.pages.synopsis.synopsis_submissions_page import SynopsisSubmissionsPage
from utils.json_reader import require_fields
from uucms.workflows.research_development.synopsis_workflow import SynopsisWorkflow

DATA_FILE = "rnd/synopsis.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_synopsis_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _open_role_list(page, uucms_settings, section) -> SynopsisSubmissionsPage:
    page_obj = SynopsisSubmissionsPage(page, uucms_settings.timeout_ms)
    page_obj.open_from_menu(section.get("menu_path"))
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    return page_obj


def _review_page(page, uucms_settings) -> SynopsisReviewPage:
    return SynopsisReviewPage(page, uucms_settings.timeout_ms)


@pytest.mark.rnd
def test_rnd_synopsis_submissions_list(page, uucms_settings, login_as):
    """TC-SYNOPSIS-001: Department Chairperson Synopsis Submissions list with filters."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE), "list.menu_path", "list.filters", "list.list_columns"
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    page_obj.expect_list_columns(data["list"]["list_columns"])


@pytest.mark.rnd
def test_rnd_synopsis_eligible_students(page, uucms_settings, login_as):
    """TC-SYNOPSIS-002: only course-work passed students are listed as eligible."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "list.menu_path", "list.filters",
        "eligible_students.action", "eligible_students.present", "eligible_students.absent",
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    eligible = data["eligible_students"]
    page_obj.open_eligible_students(eligible["action"])
    page_obj.expect_students_listed(eligible["present"], eligible["absent"])


@pytest.mark.rnd
def test_rnd_synopsis_set_submission_deadline(page, uucms_settings, login_as):
    """TC-SYNOPSIS-003: Department Chairperson sets the synopsis submission deadline."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "list.menu_path", "list.filters",
        "set_deadline.student_row", "set_deadline.edit_action",
        "set_deadline.deadline_field", "set_deadline.deadline",
        "set_deadline.save_selector", "set_deadline.updated_by",
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    deadline = data["set_deadline"]
    page_obj.set_submission_deadline(
        deadline["student_row"], deadline["edit_action"],
        deadline["deadline_field"], deadline["deadline"], deadline["save_selector"],
    )
    page_obj.open_from_menu(data["list"]["menu_path"])
    page_obj.apply_filters(data["list"]["filters"])
    page_obj.expect_row_text(deadline["student_row"], deadline["deadline"])
    page_obj.expect_row_status(deadline["student_row"], statuses.YET_TO_UPLOAD)
    page_obj.expect_row_pending_with(deadline["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_row_text(deadline["student_row"], deadline["updated_by"])


@pytest.mark.rnd
def test_rnd_synopsis_student_cannot_submit_before_deadline(page, uucms_settings, login_as):
    """TC-SYNOPSIS-004: student cannot submit before the deadline is set."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters",
        "student.student_row", "student.enter_synopsis_action",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.expect_row_status(student["student_row"], statuses.DATE_NOT_SETUP)
    page_obj.expect_row_pending_with(student["student_row"], statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON)
    page_obj.expect_action_not_available(student["student_row"], student["enter_synopsis_action"])


@pytest.mark.rnd
def test_rnd_synopsis_deadline_passed(page, uucms_settings, login_as):
    """TC-SYNOPSIS-005: status becomes Deadline Passed after the deadline lapses."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "list.menu_path", "list.filters",
        "deadline_passed.student_row", "deadline_passed.reset_action",
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    lapsed = data["deadline_passed"]
    page_obj.expect_row_status(lapsed["student_row"], statuses.DEADLINE_PASSED)
    page_obj.expect_row_pending_with(lapsed["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_available(lapsed["student_row"], lapsed["reset_action"])


@pytest.mark.rnd
def test_rnd_synopsis_reset_submission_deadline(page, uucms_settings, login_as):
    """TC-SYNOPSIS-006: re-set-up the submission deadline for a Deadline Passed student."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "list.menu_path", "list.filters",
        "deadline_passed.student_row", "deadline_passed.reset_action",
        "deadline_passed.deadline_field", "deadline_passed.new_deadline",
        "deadline_passed.save_selector",
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    reset = data["deadline_passed"]
    page_obj.set_submission_deadline(
        reset["student_row"], reset["reset_action"],
        reset["deadline_field"], reset["new_deadline"], reset["save_selector"],
    )
    page_obj.open_from_menu(data["list"]["menu_path"])
    page_obj.apply_filters(data["list"]["filters"])
    page_obj.expect_row_text(reset["student_row"], reset["new_deadline"])
    page_obj.expect_row_status(reset["student_row"], statuses.YET_TO_UPLOAD)
    page_obj.expect_row_pending_with(reset["student_row"], statuses.PENDING_WITH_STUDENT)


@pytest.mark.rnd
def test_rnd_synopsis_student_submits(page, uucms_settings, login_as):
    """TC-SYNOPSIS-007: student submits the synopsis within the deadline."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "pending_after_student",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.submit_synopsis(
        student["student_row"], student["enter_synopsis_action"],
        student["brief_details_field"], student["brief_details"],
        student["synopsis_document_input"], student["synopsis_document"],
        student["submit_selector"],
    )
    if student.get("success_selector"):
        expect(page.locator(student["success_selector"])).to_be_visible()
    page_obj.open_from_menu(student["menu_path"])
    page_obj.apply_filters(student["filters"])
    page_obj.expect_row_status(student["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(student["student_row"], data["pending_after_student"])


@pytest.mark.rnd
def test_rnd_synopsis_student_submit_blank_brief(page, uucms_settings, login_as):
    """TC-SYNOPSIS-008: submission with blank Brief details shows required-field validation."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "student.blank_brief_message",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.attempt_submit_blank_brief(
        student["student_row"], student["enter_synopsis_action"],
        student["synopsis_document_input"], student["synopsis_document"],
        student["submit_selector"], student["blank_brief_message"],
    )
    page_obj.open_from_menu(student["menu_path"])
    page_obj.apply_filters(student["filters"])
    page_obj.expect_row_status(student["student_row"], statuses.YET_TO_UPLOAD)


@pytest.mark.rnd
def test_rnd_synopsis_student_submit_without_document(page, uucms_settings, login_as):
    """TC-SYNOPSIS-009: submission without the synopsis document shows required-field validation."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.submit_selector",
        "student.missing_document_message",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.attempt_submit_without_document(
        student["student_row"], student["enter_synopsis_action"],
        student["brief_details_field"], student["brief_details"],
        student["submit_selector"], student["missing_document_message"],
    )
    page_obj.open_from_menu(student["menu_path"])
    page_obj.apply_filters(student["filters"])
    page_obj.expect_row_status(student["student_row"], statuses.YET_TO_UPLOAD)


@pytest.mark.rnd
def test_rnd_synopsis_student_submit_after_deadline(page, uucms_settings, login_as):
    """TC-SYNOPSIS-010: synopsis cannot be submitted after the deadline has passed."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.expect_row_status(student["student_row"], statuses.DEADLINE_PASSED)
    page_obj.expect_row_pending_with(student["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_not_available(student["student_row"], student["enter_synopsis_action"])


@pytest.mark.rnd
def test_rnd_synopsis_student_reenter_after_send_back(page, uucms_settings, login_as):
    """TC-SYNOPSIS-011: student re-enters the synopsis after a send back."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.reenter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "student.view_old_action", "pending_after_student",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.submit_synopsis(
        student["student_row"], student["reenter_synopsis_action"],
        student["brief_details_field"], student["brief_details"],
        student["synopsis_document_input"], student["synopsis_document"],
        student["submit_selector"],
    )
    page_obj.open_from_menu(student["menu_path"])
    page_obj.apply_filters(student["filters"])
    page_obj.expect_row_status(student["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(student["student_row"], data["pending_after_student"])
    page_obj.expect_action_available(student["student_row"], student["view_old_action"])


@pytest.mark.rnd
def test_rnd_synopsis_view_old_details(page, uucms_settings, login_as):
    """TC-SYNOPSIS-012: View Old Synopsis Details lists the latest sent-back submission first."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "old_synopsis_details.student_row", "old_synopsis_details.view_old_action",
        "old_synopsis_details.previous_dropdown", "old_synopsis_details.latest_marker",
        "old_synopsis_details.detail_sections",
        "old_synopsis_details.document_view_selector",
        "old_synopsis_details.document_download_selector",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    old = data["old_synopsis_details"]
    page_obj.open_old_synopsis_details(old["student_row"], old["view_old_action"])
    page_obj.expect_first_previous_submission(old["previous_dropdown"], old["latest_marker"])
    page_obj.select_first_previous_submission(old["previous_dropdown"])
    page_obj.expect_old_submission_details(
        old["detail_sections"],
        old["document_view_selector"], old["document_download_selector"],
    )


@pytest.mark.rnd
def test_rnd_synopsis_guide_approves(page, uucms_settings, login_as):
    """TC-SYNOPSIS-013: Guide approves the synopsis with review remarks."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.document_view_selector",
        "guide.document_download_selector", "guide.remarks_field",
        "guide.approve_remarks", "guide.approve_selector", "guide.success_selector",
        "guide.next_pending_with",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_document_available(
        guide["document_view_selector"], guide["document_download_selector"]
    )
    review.approve(
        guide["remarks_field"], guide["approve_remarks"],
        guide["approve_selector"], guide["success_selector"],
    )
    page_obj.open_from_menu(guide["menu_path"])
    page_obj.apply_filters(guide["filters"])
    page_obj.expect_row_status(guide["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(guide["student_row"], guide["next_pending_with"])
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review.expect_remarks_visible([guide["approve_remarks"]])


@pytest.mark.rnd
def test_rnd_synopsis_guide_sends_back(page, uucms_settings, login_as):
    """TC-SYNOPSIS-014: Guide sends the synopsis back with remarks."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.remarks_field",
        "guide.send_back_remarks", "guide.send_back_selector", "guide.success_selector",
        "student.student_row", "student.reenter_synopsis_action",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(
        guide["remarks_field"], guide["send_back_remarks"],
        guide["send_back_selector"], guide["success_selector"],
    )
    page_obj.open_from_menu(guide["menu_path"])
    page_obj.apply_filters(guide["filters"])
    page_obj.expect_row_status(guide["student_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(guide["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_available(
        guide["student_row"], data["student"]["reenter_synopsis_action"]
    )


@pytest.mark.rnd
def test_rnd_synopsis_guide_rejects(page, uucms_settings, login_as):
    """TC-SYNOPSIS-015: Guide rejects the synopsis with remarks."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.remarks_field",
        "guide.reject_remarks", "guide.reject_selector", "guide.success_selector",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review = _review_page(page, uucms_settings)
    review.reject(
        guide["remarks_field"], guide["reject_remarks"],
        guide["reject_selector"], guide["success_selector"],
    )
    page_obj.open_from_menu(guide["menu_path"])
    page_obj.apply_filters(guide["filters"])
    page_obj.expect_row_status(guide["student_row"], statuses.REJECTED)
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review.expect_remarks_visible([guide["reject_remarks"]])


@pytest.mark.rnd
def test_rnd_synopsis_guide_no_action_before_upload(page, uucms_settings, login_as):
    """TC-SYNOPSIS-016: Guide has no review action before the student uploads."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.expect_row_status(guide["student_row"], statuses.YET_TO_UPLOAD)
    page_obj.expect_row_pending_with(guide["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_not_available(guide["student_row"], guide["review_action"])


@pytest.mark.rnd
def test_rnd_synopsis_coguide_sees_guide_review(page, uucms_settings, login_as):
    """TC-SYNOPSIS-017: Co-Guide sees the Guide's review before acting."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action", "coguide.guide_review_section",
        "coguide.guide_review_remarks",
    )
    login_as(data["coguide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["coguide"])
    coguide = data["coguide"]
    page_obj.open_row_action(coguide["student_row"], coguide["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections([coguide["guide_review_section"]])
    review.expect_remarks_visible([coguide["guide_review_remarks"]])


@pytest.mark.rnd
def test_rnd_synopsis_guide_sees_coguide_review(page, uucms_settings, login_as):
    """TC-SYNOPSIS-018: Guide sees the Co-Guide's review (cross-display both directions)."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.coguide_review_section",
        "guide.coguide_review_remarks",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections([guide["coguide_review_section"]])
    review.expect_remarks_visible([guide["coguide_review_remarks"]])


@pytest.mark.rnd
def test_rnd_synopsis_coguide_approves(page, uucms_settings, login_as):
    """TC-SYNOPSIS-019: Co-Guide approves the synopsis."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action", "coguide.remarks_field",
        "coguide.approve_remarks", "coguide.approve_selector",
        "coguide.success_selector", "coguide.next_pending_with",
    )
    login_as(data["coguide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["coguide"])
    coguide = data["coguide"]
    page_obj.open_row_action(coguide["student_row"], coguide["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(
        coguide["remarks_field"], coguide["approve_remarks"],
        coguide["approve_selector"], coguide["success_selector"],
    )
    page_obj.open_from_menu(coguide["menu_path"])
    page_obj.apply_filters(coguide["filters"])
    page_obj.expect_row_status(coguide["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(coguide["student_row"], coguide["next_pending_with"])


@pytest.mark.rnd
def test_rnd_synopsis_coguide_sends_back(page, uucms_settings, login_as):
    """TC-SYNOPSIS-020: Co-Guide sends the synopsis back to the student."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action", "coguide.remarks_field",
        "coguide.send_back_remarks", "coguide.send_back_selector",
        "coguide.success_selector",
        "student.student_row", "student.reenter_synopsis_action",
    )
    login_as(data["coguide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["coguide"])
    coguide = data["coguide"]
    page_obj.open_row_action(coguide["student_row"], coguide["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(
        coguide["remarks_field"], coguide["send_back_remarks"],
        coguide["send_back_selector"], coguide["success_selector"],
    )
    page_obj.open_from_menu(coguide["menu_path"])
    page_obj.apply_filters(coguide["filters"])
    page_obj.expect_row_status(coguide["student_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(coguide["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_available(
        coguide["student_row"], data["student"]["reenter_synopsis_action"]
    )


@pytest.mark.rnd
def test_rnd_synopsis_chairperson_sees_reviews(page, uucms_settings, login_as):
    """TC-SYNOPSIS-021: Department Chairperson sees the Guide and Co-Guide reviews."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action",
        "department_chairperson.expected_sections", "department_chairperson.expected_remarks",
    )
    login_as(data["department_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["department_chairperson"])
    chair = data["department_chairperson"]
    page_obj.open_row_action(chair["student_row"], chair["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections(chair["expected_sections"])
    review.expect_remarks_visible(chair["expected_remarks"])


@pytest.mark.rnd
def test_rnd_synopsis_chairperson_approves(page, uucms_settings, login_as):
    """TC-SYNOPSIS-022: Department Chairperson approves the synopsis."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action", "department_chairperson.remarks_field",
        "department_chairperson.approve_remarks", "department_chairperson.approve_selector",
        "department_chairperson.success_selector", "department_chairperson.next_pending_with",
    )
    login_as(data["department_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["department_chairperson"])
    chair = data["department_chairperson"]
    page_obj.open_row_action(chair["student_row"], chair["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(
        chair["remarks_field"], chair["approve_remarks"],
        chair["approve_selector"], chair["success_selector"],
    )
    page_obj.open_from_menu(chair["menu_path"])
    page_obj.apply_filters(chair["filters"])
    page_obj.expect_row_status(chair["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(chair["student_row"], chair["next_pending_with"])


@pytest.mark.rnd
def test_rnd_synopsis_chairperson_sends_back(page, uucms_settings, login_as):
    """TC-SYNOPSIS-023: Department Chairperson sends the synopsis back."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action", "department_chairperson.remarks_field",
        "department_chairperson.send_back_remarks",
        "department_chairperson.send_back_selector", "department_chairperson.success_selector",
    )
    login_as(data["department_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["department_chairperson"])
    chair = data["department_chairperson"]
    page_obj.open_row_action(chair["student_row"], chair["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(
        chair["remarks_field"], chair["send_back_remarks"],
        chair["send_back_selector"], chair["success_selector"],
    )
    page_obj.open_from_menu(chair["menu_path"])
    page_obj.apply_filters(chair["filters"])
    page_obj.expect_row_status(chair["student_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(chair["student_row"], statuses.PENDING_WITH_STUDENT)


@pytest.mark.rnd
def test_rnd_synopsis_dcc_sees_all_reviews(page, uucms_settings, login_as):
    """TC-SYNOPSIS-024: Doctoral Committee Chairperson sees all preceding reviews."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login", "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.expected_sections",
        "doctoral_committee_chairperson.expected_remarks",
    )
    login_as(data["doctoral_committee_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["doctoral_committee_chairperson"])
    dcc = data["doctoral_committee_chairperson"]
    page_obj.open_row_action(dcc["student_row"], dcc["review_action"])
    review = _review_page(page, uucms_settings)
    review.expect_review_sections(dcc["expected_sections"])
    review.expect_remarks_visible(dcc["expected_remarks"])


@pytest.mark.rnd
def test_rnd_synopsis_dcc_approves(page, uucms_settings, login_as):
    """TC-SYNOPSIS-025: Doctoral Committee Chairperson approves - status Approved, no pending action."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login", "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.approve_remarks",
        "doctoral_committee_chairperson.approve_selector",
        "doctoral_committee_chairperson.success_selector",
        "doctoral_committee_chairperson.final_status",
        "doctoral_committee_chairperson.final_pending_with",
    )
    login_as(data["doctoral_committee_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["doctoral_committee_chairperson"])
    dcc = data["doctoral_committee_chairperson"]
    page_obj.open_row_action(dcc["student_row"], dcc["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(
        dcc["remarks_field"], dcc["approve_remarks"],
        dcc["approve_selector"], dcc["success_selector"],
    )
    page_obj.open_from_menu(dcc["menu_path"])
    page_obj.apply_filters(dcc["filters"])
    page_obj.expect_row_status(dcc["student_row"], dcc["final_status"])
    page_obj.expect_row_pending_with(dcc["student_row"], dcc["final_pending_with"])


@pytest.mark.rnd
def test_rnd_synopsis_dcc_sends_back(page, uucms_settings, login_as):
    """TC-SYNOPSIS-026: Doctoral Committee Chairperson sends back - re-routed to the student."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login", "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.send_back_remarks",
        "doctoral_committee_chairperson.send_back_selector",
        "doctoral_committee_chairperson.success_selector",
        "student.student_row", "student.reenter_synopsis_action",
    )
    login_as(data["doctoral_committee_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["doctoral_committee_chairperson"])
    dcc = data["doctoral_committee_chairperson"]
    page_obj.open_row_action(dcc["student_row"], dcc["review_action"])
    review = _review_page(page, uucms_settings)
    review.send_back(
        dcc["remarks_field"], dcc["send_back_remarks"],
        dcc["send_back_selector"], dcc["success_selector"],
    )
    page_obj.open_from_menu(dcc["menu_path"])
    page_obj.apply_filters(dcc["filters"])
    page_obj.expect_row_status(dcc["student_row"], statuses.SENT_BACK)
    page_obj.expect_row_pending_with(dcc["student_row"], statuses.PENDING_WITH_STUDENT)
    page_obj.expect_action_available(
        dcc["student_row"], data["student"]["reenter_synopsis_action"]
    )


@pytest.mark.rnd
def test_rnd_synopsis_upload_pre_register_colloquium(page, uucms_settings, login_as):
    """TC-SYNOPSIS-027: Doctoral Committee Chairperson uploads Pre-Register Colloquium details."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "doctoral_committee_chairperson.login", "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.colloquium_input",
        "doctoral_committee_chairperson.colloquium_document",
        "doctoral_committee_chairperson.colloquium_submit_selector",
    )
    login_as(data["doctoral_committee_chairperson"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["doctoral_committee_chairperson"])
    dcc = data["doctoral_committee_chairperson"]
    page_obj.open_row_action(dcc["student_row"], dcc["review_action"])
    review = _review_page(page, uucms_settings)
    review.upload_pre_register_colloquium(
        dcc["colloquium_input"], dcc["colloquium_document"],
        dcc["colloquium_submit_selector"], dcc.get("success_selector"),
    )


@pytest.mark.rnd
def test_rnd_synopsis_hierarchy_order_enforced(page, uucms_settings, login_as):
    """TC-SYNOPSIS-028: no reviewer can act ahead of the approval hierarchy."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action",
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action",
        "doctoral_committee_chairperson.login",
        "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
    )
    for role in ("coguide", "department_chairperson", "doctoral_committee_chairperson"):
        section = data[role]
        login_as(section["login"])
        page_obj = _open_role_list(page, uucms_settings, section)
        page_obj.expect_row_status(section["student_row"], statuses.AWAITING_APPROVAL)
        page_obj.expect_row_pending_with(section["student_row"], statuses.PENDING_WITH_GUIDE)
        page_obj.expect_action_not_available(section["student_row"], section["review_action"])


@pytest.mark.rnd
def test_rnd_synopsis_communication_trail_visible_to_all(page, uucms_settings, login_as):
    """TC-SYNOPSIS-029: the complete communication trail is visible to every user."""
    data = load_test_data(DATA_FILE)
    trail = data.get("communication_trail") or {}
    fields = [
        "communication_trail.view_action", "communication_trail.roles",
        "communication_trail.expected_entries",
    ]
    for role in trail.get("roles", []):
        fields += [
            f"{role}.login", f"{role}.menu_path", f"{role}.filters", f"{role}.student_row",
        ]
    _require_synopsis_data(data, *fields)
    for role in trail["roles"]:
        section = data[role]
        login_as(section["login"])
        page_obj = _open_role_list(page, uucms_settings, section)
        page_obj.open_row_action(section["student_row"], trail["view_action"])
        review = _review_page(page, uucms_settings)
        review.expect_communication_trail(trail["expected_entries"])


@pytest.mark.rnd
def test_rnd_synopsis_send_back_reenters(page, uucms_settings, login_as):
    """TC-SYNOPSIS-030: send back at any stage re-directs to the student for re-entry."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "pending_after_student", "pending_after_guide",
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "student.reenter_synopsis_action",
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.remarks_field", "guide.approve_remarks",
        "guide.approve_selector",
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action", "coguide.remarks_field", "coguide.approve_remarks",
        "coguide.approve_selector",
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action", "department_chairperson.remarks_field",
        "department_chairperson.send_back_remarks",
        "department_chairperson.send_back_selector",
    )
    workflow = SynopsisWorkflow(page, uucms_settings, login_as)
    workflow.run_send_back_chain({**data, "send_back_stage": "department_chairperson"})


@pytest.mark.rnd
def test_rnd_synopsis_status_master_table(page, uucms_settings, login_as):
    """TC-SYNOPSIS-031: status and Action Pending With values match the master table."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "list.menu_path", "list.filters",
        "master_table.status_cells", "master_table.pending_cells",
    )
    login_as("department_chairperson")
    page_obj = _open_role_list(page, uucms_settings, data["list"])
    allowed_statuses = {
        statuses.DATE_NOT_SETUP, statuses.YET_TO_UPLOAD, statuses.AWAITING_APPROVAL,
        statuses.APPROVED, statuses.SENT_BACK, statuses.REJECTED, statuses.DEADLINE_PASSED,
    }
    allowed_pending = {
        statuses.PENDING_WITH_STUDENT, roles.GUIDE, roles.CO_GUIDE,
        statuses.PENDING_WITH_GUIDE_AND_CO_GUIDE, roles.DEPARTMENT_CHAIRPERSON,
        roles.DOCTORAL_COMMITTEE_CHAIRPERSON, statuses.PENDING_WITH_NONE, "--",
    }
    statuses_seen = set(page_obj.collect_cell_texts(data["master_table"]["status_cells"]))
    unexpected_statuses = statuses_seen - allowed_statuses
    assert not unexpected_statuses, (
        f"Unexpected synopsis statuses observed: {sorted(unexpected_statuses)}"
    )
    pending_seen = set(page_obj.collect_cell_texts(data["master_table"]["pending_cells"]))
    unexpected_pending = pending_seen - allowed_pending
    assert not unexpected_pending, (
        f"Unexpected Action Pending With values observed: {sorted(unexpected_pending)}"
    )


@pytest.mark.rnd
def test_rnd_synopsis_pending_guide_and_coguide(page, uucms_settings, login_as):
    """TC-SYNOPSIS-032: Action Pending With shows Guide & Co-Guide when both are assigned."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "pending_after_student",
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
    )
    login_as(data["student"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["student"])
    student = data["student"]
    page_obj.submit_synopsis(
        student["student_row"], student["enter_synopsis_action"],
        student["brief_details_field"], student["brief_details"],
        student["synopsis_document_input"], student["synopsis_document"],
        student["submit_selector"],
    )
    login_as(data["guide"]["login"])
    guide_page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide_page_obj.expect_row_status(student["student_row"], statuses.AWAITING_APPROVAL)
    guide_page_obj.expect_row_pending_with(student["student_row"], data["pending_after_student"])


@pytest.mark.rnd
def test_rnd_synopsis_chain_skips_coguide(page, uucms_settings, login_as):
    """TC-SYNOPSIS-033: after Guide approval the chain skips the Co-Guide when none is assigned."""
    data = _require_synopsis_data(
        load_test_data(DATA_FILE),
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.remarks_field", "guide.approve_remarks",
        "guide.approve_selector", "guide.success_selector",
        "pending_after_guide_no_coguide",
    )
    login_as(data["guide"]["login"])
    page_obj = _open_role_list(page, uucms_settings, data["guide"])
    guide = data["guide"]
    page_obj.open_row_action(guide["student_row"], guide["review_action"])
    review = _review_page(page, uucms_settings)
    review.approve(
        guide["remarks_field"], guide["approve_remarks"],
        guide["approve_selector"], guide["success_selector"],
    )
    page_obj.open_from_menu(guide["menu_path"])
    page_obj.apply_filters(guide["filters"])
    page_obj.expect_row_status(guide["student_row"], statuses.AWAITING_APPROVAL)
    page_obj.expect_row_pending_with(
        guide["student_row"], data["pending_after_guide_no_coguide"]
    )


@pytest.mark.rnd
def test_rnd_synopsis_full_approval_chain(page, uucms_settings, login_as):
    """TC-SYNOPSIS-013/019/022/025: full Student -> Guide -> Co-Guide ->
    Department Chairperson -> Doctoral Committee Chairperson chain ends Approved."""
    _require_synopsis_data(
        load_test_data(DATA_FILE),
        "pending_after_student", "pending_after_guide",
        "student.login", "student.menu_path", "student.filters", "student.student_row",
        "student.enter_synopsis_action", "student.brief_details_field",
        "student.brief_details", "student.synopsis_document_input",
        "student.synopsis_document", "student.submit_selector",
        "guide.login", "guide.menu_path", "guide.filters", "guide.student_row",
        "guide.review_action", "guide.remarks_field", "guide.approve_remarks",
        "guide.approve_selector",
        "coguide.login", "coguide.menu_path", "coguide.filters", "coguide.student_row",
        "coguide.review_action", "coguide.remarks_field", "coguide.approve_remarks",
        "coguide.approve_selector",
        "department_chairperson.login", "department_chairperson.menu_path",
        "department_chairperson.filters", "department_chairperson.student_row",
        "department_chairperson.review_action", "department_chairperson.remarks_field",
        "department_chairperson.approve_remarks", "department_chairperson.approve_selector",
        "doctoral_committee_chairperson.login", "doctoral_committee_chairperson.menu_path",
        "doctoral_committee_chairperson.filters",
        "doctoral_committee_chairperson.student_row",
        "doctoral_committee_chairperson.review_action",
        "doctoral_committee_chairperson.remarks_field",
        "doctoral_committee_chairperson.approve_remarks",
        "doctoral_committee_chairperson.approve_selector",
    )
    data = load_test_data(DATA_FILE)
    workflow = SynopsisWorkflow(page, uucms_settings, login_as)
    workflow.run_approval_chain(data)
