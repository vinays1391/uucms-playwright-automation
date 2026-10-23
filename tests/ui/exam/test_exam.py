import pytest

from config.settings import load_test_data
from uucms.modules.exam.pages.notification_page import CreateNotificationPage


def _require_exam_data(data: dict) -> None:
    required = ("actions", "success_selector")
    missing = [name for name in required if not data.get(name)]
    placeholders = "REPLACE_WITH" in str(data)
    if missing or placeholders:
        raise ValueError(
            "Complete test_data/createNotificationData.json with recorded "
            "selectors, values, and a valid file path."
        )


@pytest.mark.exam
def test_exam_functionality(authenticated_page, uucms_settings) -> None:
    exam_data = load_test_data("createNotificationData.json")
    _require_exam_data(exam_data)

    notification_page = CreateNotificationPage(
        authenticated_page, uucms_settings.timeout_ms
    )
    notification_page.open_from_menu()
    notification_page.execute_actions(exam_data["actions"])
    notification_page.expect_saved(exam_data["success_selector"])