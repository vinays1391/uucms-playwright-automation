from playwright.sync_api import Page

from uucms.core.data_driven_form_page import DataDrivenFormPage


class CreateNotificationPage(DataDrivenFormPage):
    def __init__(self, page: Page, timeout_ms: int = 15000) -> None:
        super().__init__(page, timeout_ms)

    def open_from_menu(self) -> None:
        exam_link = self.page.get_by_role("link", name="Exam", exact=True)
        exam_link.wait_for(state="visible")
        exam_link.click()

        notification_links = self.page.get_by_role(
            "link", name="Exam Notification"
        )
        notification_links.first.wait_for(state="visible")
        notification_links.first.click()
        if notification_links.count() > 1:
            notification_links.nth(1).wait_for(state="visible")
            notification_links.nth(1).click()

        add_link = self.page.get_by_role(
            "link", name="Add New Exam Notification"
        )
        add_link.wait_for(state="visible")
        add_link.click()
