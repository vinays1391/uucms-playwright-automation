"""Research And Development > Set-up > Create Committees screen
(University Admin). Selectors and values come from
test_data/rnd/phd_setup.json.
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CommitteeSetupPage(DataDrivenFormPage):
    def open_from_menu(self, menu_path: Sequence[str]) -> None:
        for item in menu_path:
            link = self.page.get_by_role("link", name=item, exact=True)
            link.first.wait_for(state="visible")
            link.first.click()

    def create_committee(self, stage: Mapping[str, object]) -> None:
        self.click_control(str(stage["create_committees_button"]))
        self.page.locator(str(stage["committee_type_selector"])).select_option(
            str(stage["committee_type_value"])
        )
        self.click_guarded(str(stage["create_committee_button"]))
        self.fill_field(str(stage["committee_name_field"]), str(stage["committee_name"]))
        kannada = str(stage.get("committee_name_kannada", "")).strip()
        if kannada:
            self.fill_field(str(stage["committee_name_kannada_field"]), kannada)
        self.fill_field(str(stage["committee_purpose_field"]), str(stage["committee_purpose"]))
        self.click_guarded(str(stage["add_selector"]))
        self.click_guarded(str(stage["ok_selector"]))
        self.expect_saved(str(stage["success_selector"]))
