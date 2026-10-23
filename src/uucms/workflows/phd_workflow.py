"""Ph.D admission orchestration across roles and screen page objects.

Flow: candidate application -> (conditional) previous-education
declaration -> application details -> offline payment, then Department
Chairperson entrance view / cut-off marks / review & approve / entrance
marks, then Registrar (Admin) approves the entrance marks, the
chairperson invites candidates for the interview and enters the
interview marks, the Registrar (Admin) approves the interview marks,
the chairperson confirms the student invites and verifies the admission
documents, and finally the candidate submits the final offline payment.
Stage data comes from test_data/admission/phd_admission.json.

Multi-candidate runs use test_data/admission/phd_admission_multi.json
(candidate_stages + groups + candidates) and drive the same flow for
every candidate, grouped by program/cycle/department.
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.admission.pages.chairperson_approval_page import (
    ChairpersonApprovalPage,
)
from uucms.modules.admission.pages.document_verification_page import (
    DocumentVerificationPage,
)
from uucms.modules.admission.pages.entrance_exam_page import EntranceExamPage
from uucms.modules.admission.pages.phd_interview_page import PhdInterviewPage
from uucms.modules.admission.pages.registrar_approval_page import RegistrarApprovalPage
from uucms.modules.admission.pages.student_invite_page import StudentInvitePage
from uucms.workflows.admission_workflow import AdmissionWorkflow
from utils.stage_merge import deep_merge


class PhDAdmissionWorkflow:
    """Drives the Ph.D offline admission flow from application to approval."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.login_as = login_as
        self.candidate = AdmissionWorkflow(page, settings, login_as)
        self.entrance = EntranceExamPage(page, settings.timeout_ms)
        self.chairperson_approval = ChairpersonApprovalPage(page, settings.timeout_ms)
        self.registrar_approval = RegistrarApprovalPage(page, settings.timeout_ms)
        self.interview = PhdInterviewPage(page, settings.timeout_ms)
        self.student_invite = StudentInvitePage(page, settings.timeout_ms)
        self.document_verification = DocumentVerificationPage(page, settings.timeout_ms)

    def _login(self, stage: Mapping[str, Any]) -> None:
        self.login_as(str(stage["login"]))

    def chairperson_views_entrance_candidates(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.entrance.open_from_menu(stage["menu_path"])
        self.entrance.apply_filters(stage["filters"])
        self.entrance.view_student_details(
            str(stage["view_student_details_selector"]), stage.get("row_text")
        )

    def chairperson_sets_cut_off_marks(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.entrance.set_cut_off_marks(stage)

    def chairperson_reviews_and_approves(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.chairperson_approval.open_from_menu(
            stage["menu_path"], int(stage.get("menu_index", 0))
        )
        self.chairperson_approval.apply_filters(stage["filters"])
        self.chairperson_approval.view_student_details(
            str(stage["view_student_details_selector"]), stage.get("row_text")
        )
        self.chairperson_approval.review_and_approve(stage)

    def chairperson_enters_entrance_marks(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.entrance.open_from_menu(stage["menu_path"])
        self.entrance.apply_filters(stage["filters"])
        self.entrance.view_student_details(
            str(stage["view_student_details_selector"]), stage.get("row_text")
        )
        self.entrance.edit_entrance_marks(stage)
        self.entrance.send_for_registrar_approval(str(stage["send_registrar_selector"]))
        self.entrance.click_guarded(str(stage["ok_selector"]))
        self.entrance.expect_saved(str(stage["success_selector"]))

    def registrar_approves_or_rejects(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.registrar_approval.open_request(stage)
        self.registrar_approval.approve_or_reject(stage)

    def chairperson_invites_interview(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.interview.open_from_menu(stage["menu_path"])
        self.interview.apply_filters(stage["filters"])
        view_selector = stage.get("view_student_details_selector")
        if view_selector:
            self.interview.view_student_details(
                str(view_selector), stage.get("row_text")
            )
        self.interview.send_interview_invites(stage)

    def chairperson_enters_interview_marks(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.interview.open_from_menu(stage["menu_path"])
        self.interview.apply_filters(stage["filters"])
        self.interview.view_student_details(
            str(stage["view_student_details_selector"]), stage.get("row_text")
        )
        self.interview.enter_interview_marks(stage)

    def registrar_approves_interview_marks(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.registrar_approval.open_request(stage)
        self.registrar_approval.approve_or_reject(stage)

    def chairperson_confirms_student_invite(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.student_invite.open_from_menu(stage["menu_path"])
        self.student_invite.apply_filters(stage["filters"])
        view_selector = stage.get("view_student_details_selector")
        if view_selector:
            self.student_invite.view_student_details(
                str(view_selector), stage.get("row_text")
            )
        self.student_invite.confirm_invites(stage)

    def chairperson_verifies_documents(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.document_verification.open_from_menu(stage["menu_path"])
        self.document_verification.apply_filters(stage["filters"])
        self.document_verification.verify_documents(stage)

    def candidate_submits_final_payment(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.candidate.offline_payment_page.open_from_menu(
            str(stage["menu_entry_selector"]), str(stage["menu_entry_text"]),
        )
        self.candidate.offline_payment_page.submit_payment_for_application_row(stage)

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        self.candidate.candidate_creates_application(data["create_application"])
        self.candidate.candidate_submits_previous_education_declaration_if_pending(
            data["education_declaration"]
        )
        self.candidate.candidate_completes_application(data["application_details"])
        self.candidate.candidate_submits_offline_payment(data["offline_payment"])
        self.chairperson_views_entrance_candidates(data["entrance_view"])
        self.chairperson_sets_cut_off_marks(data["cut_off_marks"])
        self.chairperson_reviews_and_approves(data["review_approve"])
        self.chairperson_enters_entrance_marks(data["entrance_marks"])
        self.registrar_approves_or_rejects(data["registrar_action"])
        self.chairperson_invites_interview(data["interview_invite"])
        self.chairperson_enters_interview_marks(data["interview_marks"])
        self.registrar_approves_interview_marks(data["interview_marks_approval"])
        self.chairperson_confirms_student_invite(data["student_invite"])
        self.chairperson_verifies_documents(data["document_verification"])
        self.candidate_submits_final_payment(data["final_payment"])

    def run_multi_candidate_flow(self, data: Mapping[str, Any]) -> None:
        """Run the full Ph.D admission flow for every candidate in the roster.

        ``data`` holds ``candidate_stages`` (shared templates), ``groups``
        (per program/cycle/department stage data) and ``candidates``
        (per-candidate overrides). Candidates apply as themselves; the
        chairperson and registrar screens are driven once per group and
        per candidate row (row targeted by the candidate name).
        """
        candidates = list(data.get("candidates") or [])
        if not candidates:
            raise ValueError(
                "Multi-candidate data must contain at least one entry "
                "under 'candidates'"
            )
        groups = {str(group["id"]): group for group in data.get("groups") or []}
        for candidate in candidates:
            group_id = str(candidate.get("group", "")).strip()
            if group_id not in groups:
                raise ValueError(
                    f"Unknown group {group_id!r} for candidate "
                    f"{candidate.get('name', candidate.get('login', '?'))!r}; "
                    f"configured groups: {', '.join(groups) or '(none)'}"
                )
            if not str(candidate.get("name", "")).strip():
                raise ValueError(
                    f"Candidate {candidate.get('login', '?')!r} is missing "
                    "a 'name' (used to target the candidate's grid row)"
                )
            if not str(candidate.get("login", "")).strip():
                raise ValueError(
                    f"Candidate {candidate['name']!r} is missing a 'login' role"
                )

        for candidate in candidates:
            group = groups[str(candidate["group"]).strip()]
            self.candidate.candidate_creates_application(
                self._candidate_stage(data, group, candidate, "create_application")
            )
            self.candidate.candidate_submits_previous_education_declaration_if_pending(
                self._candidate_stage(data, group, candidate, "education_declaration")
            )
            self.candidate.candidate_completes_application(
                self._candidate_stage(data, group, candidate, "application_details")
            )
            self.candidate.candidate_submits_offline_payment(
                self._candidate_stage(data, group, candidate, "offline_payment")
            )

        for group_id in groups:
            group = groups[group_id]
            members = [
                candidate for candidate in candidates
                if str(candidate["group"]).strip() == group_id
            ]
            if not members:
                continue
            self.chairperson_views_entrance_candidates(
                self._group_stage(data, group, "entrance_view")
            )
            self.chairperson_sets_cut_off_marks(
                self._group_stage(data, group, "cut_off_marks")
            )
            for candidate in members:
                self.chairperson_reviews_and_approves(
                    self._group_stage(data, group, "review_approve", candidate)
                )
                self.chairperson_enters_entrance_marks(
                    self._group_stage(data, group, "entrance_marks", candidate)
                )
                self.registrar_approves_or_rejects(
                    self._group_stage(data, group, "registrar_action", candidate)
                )
            self.chairperson_invites_interview(
                self._batch_stage(data, group, members, "interview_invite")
            )
            for candidate in members:
                self.chairperson_enters_interview_marks(
                    self._group_stage(data, group, "interview_marks", candidate)
                )
                self.registrar_approves_interview_marks(
                    self._group_stage(
                        data, group, "interview_marks_approval", candidate
                    )
                )
            self.chairperson_confirms_student_invite(
                self._batch_stage(data, group, members, "student_invite")
            )
            for candidate in members:
                self.chairperson_verifies_documents(
                    self._group_stage(
                        data, group, "document_verification", candidate
                    )
                )

        for candidate in candidates:
            group = groups[str(candidate["group"]).strip()]
            self.candidate_submits_final_payment(
                self._candidate_stage(data, group, candidate, "final_payment")
            )

    @staticmethod
    def _candidate_row_text(candidate: Mapping[str, Any]) -> str:
        return (
            str(candidate.get("row_text", "")).strip()
            or str(candidate.get("name", "")).strip()
        )

    def _group_stage(
        self,
        data: Mapping[str, Any],
        group: Mapping[str, Any],
        stage_name: str,
        candidate: Mapping[str, Any] | None = None,
    ) -> dict:
        stage: dict = {}
        for layer in (
            data.get("candidate_stages", {}).get(stage_name, {}),
            group.get("stages", {}).get(stage_name, {}),
            (candidate or {}).get(stage_name, {}),
        ):
            stage = deep_merge(stage, layer)
        row_text = (
            self._candidate_row_text(candidate) if candidate is not None else ""
        )
        if row_text:
            stage["row_text"] = row_text
        return stage

    def _candidate_stage(
        self,
        data: Mapping[str, Any],
        group: Mapping[str, Any],
        candidate: Mapping[str, Any],
        stage_name: str,
    ) -> dict:
        stage = self._group_stage(data, group, stage_name, candidate)
        stage["login"] = str(candidate["login"])
        return stage

    def _batch_stage(
        self,
        data: Mapping[str, Any],
        group: Mapping[str, Any],
        members: list,
        stage_name: str,
    ) -> dict:
        stage = self._group_stage(data, group, stage_name)
        students = []
        for member in members:
            override = member.get(stage_name) or {}
            date_day = str(override.get("date_day", "")).strip()
            students.append({"row_text": self._candidate_row_text(member),
                             "date_day": date_day})
        stage["students"] = students
        stage.pop("view_student_details_selector", None)
        return stage
