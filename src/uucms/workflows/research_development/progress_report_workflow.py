"""Multi-stage progress report approval orchestration (R&D Phase 2).

Approval chain:

    Scholar -> Guide -> Co-Guide (if assigned) -> Department
            Chairperson -> Doctoral Committee Chairperson

Send back at any stage re-routes the report to the Scholar for
correction and resubmission (the chain restarts at the Guide); reject
terminates the report as Rejected. Reviewers see the "Progress Report
Review Remarks" of every preceding reviewer before they act, and the
Doctoral Committee Chairperson can attach Symposium Details (If held)
before approving.

Test-data contract (see test_data/rnd/progress_report.example.json): the
top-level sections "scholar", "guide", "coguide",
"department_chairperson" and "doctoral_committee_chairperson" share one
shape:

    login                 role key in test_data/login/LoginData.json["roles"]
    menu_path             (optional) menu path for this role's list screen
    filters               (optional) list filter actions
    report_row            selector of the report's row in the list
    remarks_field         Enter Remarks field on the review screen
    approve_remarks       remarks recorded when approving
    approve_selector      Approve action

plus, per role:

    scholar:               submit_action, brief_field, brief,
                           document_input, document, submit_selector,
                           success_selector (optional)
    guide / coguide /     send_back_selector, send_back_remarks,
    department_chairperson / doctoral_committee_chairperson:
                           reject_selector (optional), reject_remarks,
                           success_selector (optional)
    doctoral_committee_chairperson additionally:
                           symposium_input (optional), symposium_document

plus the chain expectations:

    pending_after_scholar   e.g. "Guide & Co-Guide"
    pending_after_guide     e.g. "Co-Guide"
    send_back_stage         section name where the send back happens
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page, expect

from config.settings import Settings
from uucms.constants import statuses
from uucms.modules.research_development.pages.progress_report.progress_review_page import ProgressReviewPage
from uucms.modules.research_development.pages.progress_report.progress_submissions_page import ProgressSubmissionsPage


class ProgressReportWorkflow:
    """Drives the progress report submission and approval chain across roles."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], None]) -> None:
        self.page = page
        self.settings = settings
        self.login_as = login_as
        self.submissions = ProgressSubmissionsPage(page, settings.timeout_ms)
        self.review = ProgressReviewPage(page, settings.timeout_ms)

    # -- shared steps ------------------------------------------------------

    def _open_list(self, stage: Mapping[str, Any]) -> None:
        """Log in as the stage role and open its progress submissions list."""
        self.login_as(str(stage["login"]))
        if stage.get("menu_path"):
            self.submissions.open_from_menu(list(stage["menu_path"]))
        else:
            self.submissions.open_from_menu()
        if stage.get("filters"):
            self.submissions.apply_filters(stage["filters"])

    def _expect_row(self, stage: Mapping[str, Any], status: str | None,
                    pending_with: str | None) -> None:
        row = str(stage["report_row"])
        if status is not None:
            self.submissions.expect_row_status(row, status)
        if pending_with is not None:
            self.submissions.expect_row_pending_with(row, pending_with)

    def _open_review_screen(self, stage: Mapping[str, Any]) -> None:
        self._open_list(stage)
        self.submissions.open_row_action(
            str(stage["report_row"]), str(stage["review_action"])
        )

    # -- stage actions -----------------------------------------------------

    def scholar_submits(self, stage: Mapping[str, Any], pending_with: str) -> None:
        """Scholar submits the report: status Awaiting approval, pending Guide."""
        self._open_list(stage)
        self.submissions.submit_report(
            row_selector=str(stage["report_row"]),
            action_selector=str(stage["submit_action"]),
            brief_field=str(stage["brief_field"]),
            brief=str(stage["brief"]),
            doc_input=str(stage["document_input"]),
            doc_path=str(stage["document"]),
            submit_selector=str(stage["submit_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self._expect_row(stage, statuses.AWAITING_APPROVAL, pending_with)

    def scholar_resubmits(self, stage: Mapping[str, Any], pending_with: str) -> None:
        """Scholar resubmits a sent-back report; the chain restarts at the Guide."""
        self._open_list(stage)
        self.submissions.submit_report(
            row_selector=str(stage["report_row"]),
            action_selector=str(stage["resubmit_action"]),
            brief_field=str(stage["brief_field"]),
            brief=str(stage["brief"]),
            doc_input=str(stage["document_input"]),
            doc_path=str(stage["document"]),
            submit_selector=str(stage["submit_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self._expect_row(stage, statuses.AWAITING_APPROVAL, pending_with)

    def approve(self, stage: Mapping[str, Any], next_pending_with: str) -> None:
        """A reviewer approves the report with remarks and Date & Time."""
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
        """A reviewer sends the report back to the Scholar with remarks."""
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
        """A reviewer rejects the report with remarks (terminates it)."""
        self._open_review_screen(stage)
        self.review.reject(
            remarks_field=str(stage["remarks_field"]),
            remarks=str(stage["reject_remarks"]),
            reject_selector=str(stage["reject_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self.submissions.expect_row_status(str(stage["report_row"]), statuses.REJECTED)

    def dcc_uploads_symposium_details(self, stage: Mapping[str, Any]) -> None:
        """Doctoral Committee Chairperson attaches Symposium Details (If held)."""
        self._open_review_screen(stage)
        self.review.upload_symposium_details(
            file_input=str(stage["symposium_input"]),
            file_path=str(stage["symposium_document"]),
        )

    # -- full chains ---------------------------------------------------------

    def run_approval_chain(self, data: Mapping[str, Any]) -> None:
        """Happy path: Scholar -> Guide -> Co-Guide (if assigned) ->
        Department Chairperson -> Doctoral Committee Chairperson (Approved)."""
        self.scholar_submits(data["scholar"], str(data["pending_after_scholar"]))
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
        dcc = data["doctoral_committee_chairperson"]
        if dcc.get("symposium_input"):
            self.dcc_uploads_symposium_details(dcc)
        self.approve(dcc, statuses.PENDING_WITH_NONE)
        self._open_list(dcc)
        self.submissions.expect_row_status(
            str(dcc["report_row"]), statuses.APPROVED
        )

    def run_send_back_chain(self, data: Mapping[str, Any]) -> None:
        """Submit, approve up to the configured stage, send back there, then
        resubmit as the Scholar so the chain restarts at the Guide."""
        self.scholar_submits(data["scholar"], str(data["pending_after_scholar"]))
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
        self.scholar_resubmits(data["scholar"], str(data["pending_after_scholar"]))

    def run_reject_chain(self, data: Mapping[str, Any]) -> None:
        """Submit, approve up to the configured stage and reject there."""
        self.scholar_submits(data["scholar"], str(data["pending_after_scholar"]))
        self.approve(
            data["guide"],
            str(data.get("pending_after_guide", statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON)),
        )
        if data.get("coguide"):
            self.approve(
                data["coguide"], statuses.PENDING_WITH_DEPARTMENT_CHAIRPERSON
            )
        stage = str(data["reject_stage"])
        self.reject(data[stage])
