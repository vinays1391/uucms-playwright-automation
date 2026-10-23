"""Multi-stage synopsis approval orchestration (R&D Phase 1).

Approval chain:

    Student -> Guide -> Co-Guide (if assigned) -> Department Chairperson
            -> Doctoral Committee Chairperson

Send back at any stage re-routes the submission to the Student for
re-entry (the chain restarts at the Guide); reject terminates the
submission as Rejected. Reviewers see the "Synopsis Review Remarks" of
every preceding reviewer before they act.

Test-data contract (see test_data/rnd/synopsis.example.json): the
top-level sections "student", "guide", "coguide",
"department_chairperson" and "doctoral_committee_chairperson" share one
shape:

    login                 role key in test_data/login/LoginData.json["roles"]
    menu_path             (optional) menu path for this role's list screen
    filters               (optional) list filter actions
    student_row           selector of the student's row in the list
    remarks               review remarks recorded for any review action

plus, per role:

    student:               enter_synopsis_action / reenter_synopsis_action,
                           brief_details_field, brief_details,
                           synopsis_document_input, synopsis_document,
                           submit_selector, success_selector (optional)
    guide / coguide /     review_action, remarks_field, approve_selector,
    department_chairperson / doctoral_committee_chairperson:
                           send_back_selector, reject_selector (optional),
                           approve_remarks, send_back_remarks,
                           reject_remarks (Guide), success_selector (optional)

plus the chain expectations:

    pending_after_student   e.g. "Guide & Co-Guide"
    pending_after_guide     e.g. "Co-Guide"
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page, expect

from config.settings import Settings
from uucms.constants import statuses
from uucms.modules.research_development.pages.synopsis.synopsis_review_page import SynopsisReviewPage
from uucms.modules.research_development.pages.synopsis.synopsis_submissions_page import SynopsisSubmissionsPage


class SynopsisWorkflow:
    """Drives the synopsis submission and approval chain across roles."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], None]) -> None:
        self.page = page
        self.settings = settings
        self.login_as = login_as
        self.submissions = SynopsisSubmissionsPage(page, settings.timeout_ms)
        self.review = SynopsisReviewPage(page, settings.timeout_ms)

    # -- shared steps ------------------------------------------------------

    def _open_list(self, stage: Mapping[str, Any]) -> None:
        """Log in as the stage role and open its synopsis submissions list."""
        self.login_as(str(stage["login"]))
        if stage.get("menu_path"):
            self.submissions.open_from_menu(list(stage["menu_path"]))
        else:
            self.submissions.open_from_menu()
        if stage.get("filters"):
            self.submissions.apply_filters(stage["filters"])

    def _expect_row(self, stage: Mapping[str, Any], status: str | None,
                    pending_with: str | None) -> None:
        row = str(stage["student_row"])
        if status is not None:
            self.submissions.expect_row_status(row, status)
        if pending_with is not None:
            self.submissions.expect_row_pending_with(row, pending_with)

    def _open_review_screen(self, stage: Mapping[str, Any]) -> None:
        self._open_list(stage)
        self.submissions.open_row_action(
            str(stage["student_row"]), str(stage["review_action"])
        )

    # -- stage actions -----------------------------------------------------

    def student_submits(self, stage: Mapping[str, Any], pending_with: str) -> None:
        """Student submits the synopsis: status becomes Awaiting Approval."""
        self._open_list(stage)
        self.submissions.submit_synopsis(
            row_selector=str(stage["student_row"]),
            action_selector=str(stage["enter_synopsis_action"]),
            brief_field=str(stage["brief_details_field"]),
            brief=str(stage["brief_details"]),
            doc_input=str(stage["synopsis_document_input"]),
            doc_path=str(stage["synopsis_document"]),
            submit_selector=str(stage["submit_selector"]),
        )
        if stage.get("success_selector"):
            expect(self.page.locator(str(stage["success_selector"]))).to_be_visible()
        self._open_list(stage)
        self._expect_row(stage, statuses.AWAITING_APPROVAL, pending_with)

    def student_reenters(self, stage: Mapping[str, Any], pending_with: str) -> None:
        """Student re-enters a sent-back synopsis; the chain restarts at the Guide."""
        self._open_list(stage)
        self.submissions.submit_synopsis(
            row_selector=str(stage["student_row"]),
            action_selector=str(stage["reenter_synopsis_action"]),
            brief_field=str(stage["brief_details_field"]),
            brief=str(stage["brief_details"]),
            doc_input=str(stage["synopsis_document_input"]),
            doc_path=str(stage["synopsis_document"]),
            submit_selector=str(stage["submit_selector"]),
        )
        self._open_list(stage)
        self._expect_row(stage, statuses.AWAITING_APPROVAL, pending_with)

    def approve(self, stage: Mapping[str, Any], next_pending_with: str) -> None:
        """A reviewer approves the synopsis with remarks and Date & Time."""
        self._open_review_screen(stage)
        self.review.approve(
            remarks_field=str(stage["remarks_field"]),
            remarks=str(stage["approve_remarks"]),
            approve_selector=str(stage["approve_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self._expect_row(stage, statuses.AWAITING_APPROVAL, next_pending_with)

    def send_back(self, stage: Mapping[str, Any]) -> None:
        """A reviewer sends the synopsis back to the Student with remarks."""
        self._open_review_screen(stage)
        self.review.send_back(
            remarks_field=str(stage["remarks_field"]),
            remarks=str(stage["send_back_remarks"]),
            send_back_selector=str(stage["send_back_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self._expect_row(stage, statuses.SENT_BACK, statuses.PENDING_WITH_STUDENT)

    def reject(self, stage: Mapping[str, Any]) -> None:
        """Guide rejects the synopsis with remarks (terminates the submission)."""
        self._open_review_screen(stage)
        self.review.reject(
            remarks_field=str(stage["remarks_field"]),
            remarks=str(stage["reject_remarks"]),
            reject_selector=str(stage["reject_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self.submissions.expect_row_status(str(stage["student_row"]), statuses.REJECTED)

    def upload_pre_register_colloquium(self, stage: Mapping[str, Any]) -> None:
        """Doctoral Committee Chairperson attaches Pre-Register Colloquium details."""
        self._open_review_screen(stage)
        self.review.upload_pre_register_colloquium(
            file_input=str(stage["colloquium_input"]),
            file_path=str(stage["colloquium_document"]),
            submit_selector=str(stage["colloquium_submit_selector"]),
            success_selector=stage.get("success_selector"),
        )

    # -- full chains ---------------------------------------------------------

    def run_approval_chain(self, data: Mapping[str, Any]) -> None:
        """Happy path: Student -> Guide -> Co-Guide (if assigned) ->
        Department Chairperson -> Doctoral Committee Chairperson (Approved)."""
        self.student_submits(data["student"], str(data["pending_after_student"]))
        self.approve(
            data["guide"],
            str(data.get("pending_after_guide", statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON)),
        )
        if data.get("coguide"):
            self.approve(
                data["coguide"], statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON
            )
        self.approve(
            data["department_chairperson"],
            statuses.PENDING_WITH_DOCTORAL_COMMITTEE_CHAIRPERSON,
        )
        self.approve(
            data["doctoral_committee_chairperson"], statuses.PENDING_WITH_NONE
        )
        self._open_list(data["doctoral_committee_chairperson"])
        self.submissions.expect_row_status(
            str(data["doctoral_committee_chairperson"]["student_row"]),
            statuses.APPROVED,
        )

    def run_send_back_chain(self, data: Mapping[str, Any]) -> None:
        """Submit, approve up to the configured stage, send back there, then
        re-enter as the Student so the chain restarts at the Guide."""
        self.student_submits(data["student"], str(data["pending_after_student"]))
        self.approve(
            data["guide"],
            str(data.get("pending_after_guide", statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON)),
        )
        if data.get("coguide"):
            self.approve(
                data["coguide"], statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON
            )
        stage = str(data["send_back_stage"])
        self.send_back(data[stage])
        self.student_reenters(data["student"], str(data["pending_after_student"]))
