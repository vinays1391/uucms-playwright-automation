"""Registration Details screen and previous-education declarations."""

from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class RegistrationDetailsPage(DataDrivenFormPage):
    def open_from_user_menu(self, user_menu_selector: str, action_text: str) -> None:
        user_menu = self.page.locator(user_menu_selector)
        user_menu.first.wait_for(state="visible")
        user_menu.first.click()
        self.page.get_by_role("link", name=action_text).first.click()

    def education_declaration_submitted(self, check_selector: str) -> bool:
        marker = self.page.locator(check_selector)
        return marker.count() > 0 and marker.first.is_visible()

    def submit_education_declaration(self, tab: str, declaration_selector: str,
                                     captcha: str | None, captcha_selector: str,
                                     submit_selector: str, ok_selector: str,
                                     success_selector: str) -> None:
        self.page.get_by_role("tab", name=tab).first.click()
        self.page.locator(declaration_selector).check()
        if captcha:
            field = self.page.locator(captcha_selector)
            field.first.wait_for(state="visible")
            field.first.fill(captcha)
        self.submit(submit_selector)
        self.click_guarded(ok_selector)
        self.expect_saved(success_selector)
