"""R&D Ph.D admission: Map New Program screen.

Maps Teaching Mode, Medium of Instruction, Evaluation System, Language
and Open Elective for a newly offered program. Field selectors and
values come from the test-data file (reached via the Map New Program
row action on the Program Details list).
"""

from collections.abc import Mapping, Sequence

from playwright.sync_api import expect

from uucms.core.data_driven_form_page import DataDrivenFormPage


class MapNewProgramPage(DataDrivenFormPage):
    def fill_mapping_fields(self, actions: Sequence[Mapping[str, object]]) -> None:
        """Fill the mapping fields (teaching mode, medium, evaluation, ...)."""
        self.execute_actions(list(actions))

    def submit_mapping(self, submit_selector: str, success_selector: str) -> None:
        self.submit(submit_selector)
        expect(self.page.locator(success_selector)).to_be_visible()

    def submit_blank_expect_validation(self, submit_selector: str, message: str) -> None:
        """Submit with all mapping fields blank and expect the validation."""
        self.submit_expect_validation(submit_selector, message)

    def expect_mapping_displayed(self, success_selector: str, values: Sequence[str]) -> None:
        expect(self.page.locator(success_selector)).to_be_visible()
        display = self.page.locator(success_selector).first
        for value in values:
            expect(display).to_contain_text(str(value))
