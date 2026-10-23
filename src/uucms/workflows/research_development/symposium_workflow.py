"""Symposium lifecycle orchestration (R&D Phase 2).

Lifecycle:

    DCC invite (Yet to Send -> Scheduled)
        -> Edit Schedule (while Scheduled)
        -> event date & time crossed (Scheduled -> Yet to Upload Details)
        -> Upload Details + Approve (Approved)  or  Reject (Rejected)
        -> Send Re-Invitation (Rejected -> Scheduled for the next event)

After a final progress report is approved, the scholar becomes visible
in the DCC's symposium invitation list; the scholar's invitation list
mirrors the DCC status transitions.

Test-data contract (see test_data/rnd/symposium.example.json): the top
level sections "invite", "event_details" and "re_invite" are:

    invite:         login, menu_path (optional), filters (optional),
                    scholar_row, actions (panel, date & time, duration,
                    mode, venue), send_selector, success_selector (optional)
    event_details:  login, menu_path (optional), filters (optional),
                    scholar_row, upload_action, event_type_select (optional),
                    event_type (optional), media_input, media,
                    media_link_field, media_link, support_input, support,
                    approve_selector (optional), reject_selector (optional),
                    success_selector (optional)
    re_invite:      login, menu_path (optional), filters (optional),
                    scholar_row, re_invite_action, actions (panel, new
                    date & time, ...), send_selector,
                    success_selector (optional)
"""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page, expect

from config.settings import Settings
from uucms.constants import statuses
from uucms.modules.research_development.pages.symposium.symposium_event_details_page import SymposiumEventDetailsPage
from uucms.modules.research_development.pages.symposium.symposium_invitation_page import SymposiumInvitationPage


class SymposiumWorkflow:
    """Drives the DCC symposium invitation lifecycle."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], None]) -> None:
        self.page = page
        self.settings = settings
        self.login_as = login_as
        self.invitation = SymposiumInvitationPage(page, settings.timeout_ms)
        self.event_details = SymposiumEventDetailsPage(page, settings.timeout_ms)

    # -- shared steps ------------------------------------------------------

    def _open_list(self, stage: Mapping[str, Any]) -> None:
        """Log in as the DCC and open the symposium invitation list."""
        self.login_as(str(stage["login"]))
        if stage.get("menu_path"):
            self.invitation.open_from_menu(list(stage["menu_path"]))
        else:
            self.invitation.open_from_menu()
        if stage.get("filters"):
            self.invitation.apply_filters(stage["filters"])

    # -- lifecycle steps -----------------------------------------------------

    def send_invitation(self, stage: Mapping[str, Any]) -> None:
        """DCC sends the invitation: Yet to Send -> Scheduled."""
        self._open_list(stage)
        self.invitation.send_invitation(
            row_selector=str(stage["scholar_row"]),
            actions=stage["actions"],
            send_selector=str(stage["send_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self.invitation.expect_status(str(stage["scholar_row"]), statuses.SCHEDULED)

    def upload_and_approve(self, stage: Mapping[str, Any]) -> None:
        """DCC uploads the event details (after the date & time has passed)
        and approves: Yet to Upload Details -> Approved."""
        self._open_list(stage)
        self.invitation.open_event_details(
            str(stage["scholar_row"]), str(stage["upload_action"])
        )
        if stage.get("event_type_select"):
            self.event_details.choose_event_type(
                str(stage["event_type_select"]), str(stage["event_type"])
            )
        self.event_details.upload_details(
            media_input=str(stage["media_input"]),
            media_path=str(stage["media"]),
            media_link_field=str(stage["media_link_field"]),
            media_link=str(stage["media_link"]),
            support_input=str(stage["support_input"]),
            support_path=str(stage["support"]),
        )
        self.event_details.approve(
            str(stage["approve_selector"]), stage.get("success_selector")
        )
        self._open_list(stage)
        self.invitation.expect_status(str(stage["scholar_row"]), statuses.APPROVED)

    def upload_and_reject(self, stage: Mapping[str, Any]) -> None:
        """DCC uploads the event details and rejects: Rejected, with
        Send Re-Invitation and Edit Schedule available on the row."""
        self._open_list(stage)
        self.invitation.open_event_details(
            str(stage["scholar_row"]), str(stage["upload_action"])
        )
        if stage.get("event_type_select"):
            self.event_details.choose_event_type(
                str(stage["event_type_select"]), str(stage["event_type"])
            )
        self.event_details.upload_details(
            media_input=str(stage["media_input"]),
            media_path=str(stage["media"]),
            media_link_field=str(stage["media_link_field"]),
            media_link=str(stage["media_link"]),
            support_input=str(stage["support_input"]),
            support_path=str(stage["support"]),
        )
        self.event_details.reject(
            str(stage["reject_selector"]), stage.get("success_selector")
        )
        self._open_list(stage)
        self.invitation.expect_status(str(stage["scholar_row"]), statuses.REJECTED)

    def send_re_invitation(self, stage: Mapping[str, Any]) -> None:
        """DCC re-invites a Rejected scholar: back to Scheduled."""
        self._open_list(stage)
        self.invitation.send_re_invitation(
            row_selector=str(stage["scholar_row"]),
            re_invite_action=str(stage["re_invite_action"]),
            actions=stage["actions"],
            send_selector=str(stage["send_selector"]),
            success_selector=stage.get("success_selector"),
        )
        self._open_list(stage)
        self.invitation.expect_status(str(stage["scholar_row"]), statuses.SCHEDULED)

    # -- full lifecycles -------------------------------------------------------

    def run_full_lifecycle(self, data: Mapping[str, Any]) -> None:
        """Invite -> (event date & time crossed) -> upload details -> Approve."""
        self.send_invitation(data["invite"])
        self.upload_and_approve(data["event_details"])

    def run_reject_reinvite(self, data: Mapping[str, Any]) -> None:
        """Invite -> upload details -> Reject -> Send Re-Invitation."""
        self.send_invitation(data["invite"])
        self.upload_and_reject(data["event_details"])
        self.send_re_invitation(data["re_invite"])
