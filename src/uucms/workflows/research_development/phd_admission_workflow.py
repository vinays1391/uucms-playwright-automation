"""Permanent USN approval orchestration (R&D Phase 1).

Approval chain:

    University Admin -> Superintendent -> Registrar (Admin)

The Registrar (Admin) approval assigns the permanent USN; the student is
then notified and treated as a Ph.D scholar for the subsequent R&D
workflows. A Superintendent rejection stops the chain: the student keeps
the provisional USN.

Test-data contract (see test_data/rnd/permanent_usn.example.json): the
top-level sections "university_admin", "superintendent",
"registrar_admin", "usn_verification" and "student" share the keys
"login", "menu_path" (optional) and "filters" (optional), plus
per-section selectors and values.
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.research_development.pages.permusn.permanent_usn_page import PermanentUsnPage


class PermanentUsnWorkflow:
    """Drives the provisional -> permanent USN approval chain across roles."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], None]) -> None:
        self.page = page
        self.settings = settings
        self.login_as = login_as
        self.usn = PermanentUsnPage(page, settings.timeout_ms)

    def _open(self, stage: Mapping[str, Any]) -> None:
        """Log in as the stage role and open its permanent USN screen."""
        self.login_as(str(stage["login"]))
        if stage.get("menu_path"):
            self.usn.open_from_menu(list(stage["menu_path"]))
        if stage.get("filters"):
            self.usn.apply_filters(stage["filters"])

    def university_admin_sends(self, stage: Mapping[str, Any]) -> None:
        """University Admin forwards the provisional USN for approval."""
        self._open(stage)
        self.usn.send_for_approval(
            row_selector=str(stage["student_row"]),
            send_selector=str(stage["send_selector"]),
            success_selector=str(stage["success_selector"]),
        )

    def superintendent_approves(self, stage: Mapping[str, Any]) -> None:
        """Superintendent approves and forwards the request to Registrar (Admin)."""
        self._open(stage)
        self.usn.approve_request(
            row_selector=str(stage["request_row"]),
            action_selector=str(stage["review_action"]),
            approve_selector=str(stage["approve_selector"]),
            success_selector=stage.get("success_selector"),
        )

    def superintendent_rejects(self, stage: Mapping[str, Any], remarks: str) -> None:
        """Superintendent rejects the request with remarks."""
        self._open(stage)
        self.usn.reject_request(
            row_selector=str(stage["request_row"]),
            action_selector=str(stage["review_action"]),
            remarks_field=str(stage["remarks_field"]),
            remarks=remarks,
            reject_selector=str(stage["reject_selector"]),
            success_selector=stage.get("success_selector"),
        )

    def registrar_approves(self, stage: Mapping[str, Any]) -> None:
        """Registrar (Admin) approves: the permanent USN is assigned."""
        self._open(stage)
        self.usn.approve_request(
            row_selector=str(stage["request_row"]),
            action_selector=str(stage["review_action"]),
            approve_selector=str(stage["approve_selector"]),
            success_selector=stage.get("success_selector"),
        )

    def verify_permanent_usn(self, stage: Mapping[str, Any]) -> str:
        """Check format, uniqueness and difference from the provisional USN."""
        self._open(stage)
        usn = self.usn.read_permanent_usn(str(stage["permanent_usn_selector"]))
        self.usn.expect_usn_format(usn, str(stage["usn_format"]))
        self.usn.expect_usn_different_from(usn, str(stage["provisional_usn"]))
        if stage.get("all_usn_cells_selector"):
            usns = self.usn.collect_usns(str(stage["all_usn_cells_selector"]))
            if len(set(usns)) != len(usns):
                raise ValueError(f"Permanent USN is not unique across students: {usns}")
        return usn

    def student_verified_notified(self, stage: Mapping[str, Any],
                                  permanent_usn: str | None = None) -> None:
        """Student receives the notification and is treated as a Ph.D scholar."""
        self._open(stage)
        self.usn.expect_notification(
            str(stage["notification_selector"]), permanent_usn
        )
        self.usn.expect_scholar_status(
            str(stage["profile_selector"]), str(stage["scholar_status_text"])
        )

    def run_full_flow(self, data: Mapping[str, Any]) -> None:
        """University Admin -> Superintendent -> Registrar (Admin) ->
        USN verified -> student notified and treated as Ph.D scholar."""
        self.university_admin_sends(data["university_admin"])
        self.superintendent_approves(data["superintendent"])
        self.registrar_approves(data["registrar_admin"])
        usn = self.verify_permanent_usn(data["usn_verification"])
        self.student_verified_notified(data["student"], usn)
