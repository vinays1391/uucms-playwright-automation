# Exam POM conversion prompt

Record the exam workflow with the browser automation tool, then convert the generated actions into a stable page object model under `src/uucms/modules/exam/pages` and a data-driven test under `tests/ui/exam`.

Checklist:
- use selectors from the live UI only
- replace raw hardcoded values with entries from `test_data/createNotificationData.json`
- keep waits meaningful and specific
- verify the success selector before finalizing
- do not commit sensitive data
