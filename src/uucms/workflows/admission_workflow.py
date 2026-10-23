"""Candidate admission workflow composed from screen-specific page objects."""

from collections.abc import Callable, Mapping
from typing import Any

from playwright.sync_api import Page

from config.settings import Settings
from uucms.modules.admission.pages.application_page import ApplicationPage
from uucms.modules.admission.pages.offline_payment_page import OfflinePaymentPage
from uucms.modules.admission.pages.registration_details_page import (
    RegistrationDetailsPage,
)


PREVIOUS_EDUCATION_BY_PROGRAM_LEVEL = {
    "ug": "PUC",
    "undergraduate": "PUC",
    "pg": "UG",
    "postgraduate": "UG",
    "phd": "PG",
    "phdscience": "PG",
}


class AdmissionWorkflow:
    """Orchestrates candidate steps; page objects remain screen-specific."""

    def __init__(self, page: Page, settings: Settings,
                 login_as: Callable[[str], object]) -> None:
        self.page = page
        self.settings = settings
        self.login_as = login_as
        self.application_page = ApplicationPage(page, settings.timeout_ms)
        self.registration_details_page = RegistrationDetailsPage(
            page, settings.timeout_ms
        )
        self.offline_payment_page = OfflinePaymentPage(page, settings.timeout_ms)

    def _login(self, stage: Mapping[str, Any]) -> None:
        self.login_as(str(stage["login"]))

    def candidate_creates_application(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.application_page.open_create_application(
            str(stage["menu_entry_selector"]), str(stage["menu_entry_text"]),
            str(stage["create_button"]),
        )
        self.application_page.select_program(stage["actions"])
        self.application_page.click_guarded(str(stage["ok_selector"]))
        self.application_page.expect_saved(str(stage["success_selector"]))

    def candidate_submits_previous_education_declaration_if_pending(
        self, stage: Mapping[str, Any]
    ) -> bool:
        self._login(stage)
        self.registration_details_page.open_from_user_menu(
            str(stage["user_menu_selector"]), str(stage["registration_details_text"]),
        )
        program_level = (
            str(stage["program_level"]).strip().casefold().replace(".", "").replace(" ", "")
        )
        try:
            education_level = PREVIOUS_EDUCATION_BY_PROGRAM_LEVEL[program_level]
        except KeyError as exc:
            raise ValueError(
                f"Unsupported admission program level {stage['program_level']!r}; "
                "expected UG/Undergraduate, PG/Postgraduate, or Ph.D."
            ) from exc

        declaration = stage["education_declarations"][education_level]
        if self.registration_details_page.education_declaration_submitted(
            str(declaration["submitted_check_selector"])
        ):
            return True
        self.registration_details_page.submit_education_declaration(
            str(declaration["tab"]), str(declaration["declaration_selector"]),
            self.settings.captcha, str(stage["captcha_selector"]),
            str(stage["submit_selector"]), str(stage["ok_selector"]),
            str(declaration["success_selector"]),
        )
        return False

    def candidate_completes_application(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.application_page.open_create_application(
            str(stage["menu_entry_selector"]), str(stage["menu_entry_text"]),
            str(stage["create_button"]),
        )
        self.application_page.complete_application(
            stage["actions"], str(stage["submit_selector"]),
            str(stage["discipline_selector"]), str(stage["discipline_value"]),
            str(stage["preview_submit_selector"]), str(stage["declaration_checkbox"]),
            str(stage["confirm_selector"]), str(stage["ok_selector"]),
            str(stage["success_selector"]),
        )

    def candidate_submits_offline_payment(self, stage: Mapping[str, Any]) -> None:
        self._login(stage)
        self.offline_payment_page.open_from_menu(
            str(stage["menu_entry_selector"]), str(stage["menu_entry_text"]),
        )
        self.offline_payment_page.submit_payment(stage)
