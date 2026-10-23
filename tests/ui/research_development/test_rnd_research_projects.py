"""Research And Development > Research Projects (R&D Phase 3) test cases.

The four Research Projects screens explored live as the Department
Chairperson:

    Research Projects Details   (list + Create Research Project form)
    Submission Configuration    (member-wise submission schedule)
    Submissions                 (progress report submissions + modal)
    Progress Completion         (member completion marking)

Role logins come from the "roles" mapping in test_data/login/LoginData.json
via the login_as fixture. The screen-structure tests assert the observed
headings, breadcrumbs, filters, buttons, table columns, empty-state text
and export controls, so they stay safe in environments where the project
tables are empty; row-level checks (project information, member schedule,
View Details modal, completion marking) only run when the required data
is present and skip when the tables have no rows.
"""

import pytest
from playwright.sync_api import expect

from config.settings import load_test_data
from uucms.modules.research_development.pages.research_projects.project_progress_completion_page import ProjectProgressCompletionPage
from uucms.modules.research_development.pages.research_projects.project_submission_config_page import ProjectSubmissionConfigPage
from uucms.modules.research_development.pages.research_projects.project_submissions_page import ProjectSubmissionsPage
from uucms.modules.research_development.pages.research_projects.research_projects_details_page import ResearchProjectsDetailsPage
from utils.json_reader import require_fields

DATA_FILE = "rnd/research_projects.json"
DATA_PATH = f"test_data/{DATA_FILE}"


def _require_rp_data(data: dict, *fields: str) -> dict:
    return require_fields(data, list(fields), DATA_PATH)


def _details(page, uucms_settings) -> ResearchProjectsDetailsPage:
    return ResearchProjectsDetailsPage(page, uucms_settings.timeout_ms)


def _config(page, uucms_settings) -> ProjectSubmissionConfigPage:
    return ProjectSubmissionConfigPage(page, uucms_settings.timeout_ms)


def _submissions(page, uucms_settings) -> ProjectSubmissionsPage:
    return ProjectSubmissionsPage(page, uucms_settings.timeout_ms)


def _completion(page, uucms_settings) -> ProjectProgressCompletionPage:
    return ProjectProgressCompletionPage(page, uucms_settings.timeout_ms)


@pytest.mark.rnd
def test_rnd_rp_details_list_screen(page, uucms_settings, login_as):
    """TC-RESEARCHPROJECT-001: the Research Projects list offers the Area of Research filter and Create a New Research Project."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "details_list.login", "details_list.menu_path",
        "details_list.heading", "details_list.create_link",
        "details_list.view_button",
    )
    section = data["details_list"]
    login_as(section["login"])
    page_obj = _details(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_list_screen(section["heading"], section["create_link"],
                                section["view_button"])


@pytest.mark.rnd
def test_rnd_rp_details_aor_filter_lists_projects(page, uucms_settings, login_as):
    """TC-RESEARCHPROJECT-001: filtering by Area of Research lists only the matching projects."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "details_list.login", "details_list.menu_path",
        "details_list.aor_filter", "details_list.aor_filter_value",
        "details_list.view_button", "details_list.list_columns",
    )
    section = data["details_list"]
    login_as(section["login"])
    page_obj = _details(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_projects(
        [{"type": "select_labels", "selector": section["aor_filter"],
          "value": section["aor_filter_value"]}],
        section["view_button"],
    )
    page_obj.expect_list_columns(section["list_columns"])


@pytest.mark.rnd
def test_rnd_rp_create_form_smoke(page, uucms_settings, login_as):
    """TC-RESEARCHPROJECT-002: the Create Research Project form shows every documented field."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "details_list.heading",
        "create_form.login", "create_form.menu_path", "create_form.create_link",
        "create_form.heading", "create_form.breadcrumb",
        "create_form.field_labels", "create_form.known_fields",
        "create_form.upload_hint", "create_form.submit_selector",
        "create_form.back_selector",
    )
    section = data["create_form"]
    login_as(section["login"])
    page_obj = _details(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_create_form(section["create_link"])
    page_obj.expect_create_form(
        section["heading"], section["breadcrumb"], section["field_labels"],
        section["known_fields"], section["upload_hint"],
        section["submit_selector"], section["back_selector"],
    )
    page_obj.click_control(section["back_selector"])
    expect(page.get_by_text(data["details_list"]["heading"],
                            exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_rp_create_external_funding_project(page, uucms_settings, login_as):
    """TC-RESEARCHPROJECT-002: an External/Funding project is created with both proposal documents."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "create_project.login", "create_project.menu_path",
        "create_project.create_link", "create_project.actions",
        "create_project.submit_selector", "create_project.success_selector",
        "create_project.project_name",
        "details_list.heading", "details_list.view_button",
        "details_list.aor_filter", "details_list.aor_filter_value",
    )
    section = data["create_project"]
    details = data["details_list"]
    login_as(section["login"])
    page_obj = _details(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_create_form(section["create_link"])
    page_obj.fill_create_form(section["actions"])
    page_obj.submit_project(section["submit_selector"],
                            section["success_selector"])
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_projects(
        [{"type": "select_labels", "selector": details["aor_filter"],
          "value": details["aor_filter_value"]}],
        details["view_button"],
    )
    expect(page.get_by_text(section["project_name"],
                            exact=True)).to_be_visible()


@pytest.mark.rnd
def test_rnd_rp_internal_type_no_funding_agency(page, uucms_settings, login_as):
    """TC-RESEARCHPROJECT-003: an Internal project does not load the external funding agency list."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "internal_no_funding_agency.login",
        "internal_no_funding_agency.menu_path",
        "internal_no_funding_agency.create_link",
        "internal_no_funding_agency.project_type_select",
        "internal_no_funding_agency.project_type",
        "internal_no_funding_agency.funding_agency_select",
    )
    section = data["internal_no_funding_agency"]
    login_as(section["login"])
    page_obj = _details(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.open_create_form(section["create_link"])
    page_obj.execute_actions([
        {"type": "select_label",
         "selector": section["project_type_select"],
         "value": section["project_type"]}
    ])
    page_obj.expect_funding_agency_not_loaded(section["funding_agency_select"])


@pytest.mark.rnd
def test_rnd_rp_submission_config_screen(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-001: the Submission Configuration screen offers the cascaded Area of Research / project selects."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "submission_configuration.login",
        "submission_configuration.menu_path",
        "submission_configuration.heading",
        "submission_configuration.breadcrumb",
        "submission_configuration.area_select",
        "submission_configuration.area_options",
        "submission_configuration.project_select",
        "submission_configuration.view_button",
        "submission_configuration.back_link",
    )
    section = data["submission_configuration"]
    login_as(section["login"])
    page_obj = _config(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_screen(
        section["heading"], section["breadcrumb"], section["area_select"],
        section["project_select"], section["view_button"],
        section["back_link"],
    )
    page_obj.expect_select_options(section["area_select"],
                                   section["area_options"])


@pytest.mark.rnd
def test_rnd_rp_submission_config_project_members(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-001: View shows the project information card and the member schedule table."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "submission_configuration_project.login",
        "submission_configuration_project.menu_path",
        "submission_configuration_project.filters",
        "submission_configuration_project.view_button",
        "submission_configuration_project.info_card_heading",
        "submission_configuration_project.project_info_labels",
        "submission_configuration_project.member_columns",
        "submission_configuration_project.member_row",
        "submission_configuration_project.edit_action",
        "submission_configuration_project.frequency_select",
        "submission_configuration_project.frequency_options",
    )
    section = data["submission_configuration_project"]
    login_as(section["login"])
    page_obj = _config(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_project(section["filters"], section["view_button"])
    expect(page.get_by_text(section["info_card_heading"],
                            exact=True)).to_be_visible()
    page_obj.expect_project_info(section["project_info_labels"])
    page_obj.expect_list_columns(section["member_columns"])
    if page_obj.row_count(section["member_row"]) == 0:
        pytest.skip("no project members configured under the selected project")
    page_obj.expect_action_available(section["member_row"],
                                     section["edit_action"])
    options = page_obj.collect_select_options(section["frequency_select"])
    missing = [option for option in section["frequency_options"]
               if option not in options]
    assert not missing, (
        f"Frequency of submission options missing: {missing}; "
        f"available: {options}"
    )


@pytest.mark.rnd
def test_rnd_rp_edit_submission_configuration(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-002: a saved member submission configuration is edited and saved."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "edit_submission_configuration.login",
        "edit_submission_configuration.menu_path",
        "edit_submission_configuration.filters",
        "edit_submission_configuration.view_button",
        "edit_submission_configuration.member_row",
        "edit_submission_configuration.edit_action",
        "edit_submission_configuration.actions",
        "edit_submission_configuration.save_selector",
        "edit_submission_configuration.success_selector",
        "edit_submission_configuration.expected_row_text",
    )
    section = data["edit_submission_configuration"]
    login_as(section["login"])
    page_obj = _config(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_project(section["filters"], section["view_button"])
    page_obj.edit_configuration(
        section["member_row"], section["edit_action"], section["actions"],
        section["save_selector"], section["success_selector"],
    )
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_project(section["filters"], section["view_button"])
    page_obj.expect_row_text(section["member_row"],
                             section["expected_row_text"])


@pytest.mark.rnd
def test_rnd_rp_project_submissions_screen(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-005: the Project Submissions screen offers the filters, exports and the master columns."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "project_submissions.login", "project_submissions.menu_path",
        "project_submissions.heading", "project_submissions.breadcrumb",
        "project_submissions.aor_filter",
        "project_submissions.aor_default_option",
        "project_submissions.project_filter", "project_submissions.view_button",
        "project_submissions.export_buttons", "project_submissions.list_columns",
    )
    section = data["project_submissions"]
    login_as(section["login"])
    page_obj = _submissions(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_screen(
        section["heading"], section["breadcrumb"], section["aor_filter"],
        section["project_filter"], section["view_button"],
        section["export_buttons"],
    )
    page_obj.expect_list_columns(section["list_columns"])
    options = page_obj.collect_select_options(section["aor_filter"])
    assert section["aor_default_option"] in options, (
        f"Default area option {section['aor_default_option']!r} "
        f"not offered: {options}"
    )


@pytest.mark.rnd
def test_rnd_rp_view_report_details_modal(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-012: View Details opens the review modal for the submission (only when rows exist)."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "view_details_modal.login", "view_details_modal.menu_path",
        "view_details_modal.row_selector", "view_details_modal.report_id_cell",
        "view_details_modal.view_action", "view_details_modal.modal",
        "view_details_modal.title_prefix", "view_details_modal.field_labels",
        "view_details_modal.section_title", "view_details_modal.detail_labels",
        "view_details_modal.close_selector",
    )
    section = data["view_details_modal"]
    login_as(section["login"])
    page_obj = _submissions(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    if section.get("filters"):
        page_obj.apply_filters(section["filters"])
    if page_obj.row_count(section["row_selector"]) == 0:
        pytest.skip("no project progress submissions to review in this environment")
    report_id = page_obj.read_cell_text(section["report_id_cell"])
    page_obj.view_report_details(section["row_selector"],
                                 section["view_action"])
    page_obj.expect_review_modal(
        section["modal"], section["title_prefix"] + report_id,
        section["field_labels"], section["section_title"],
        section["detail_labels"],
    )
    page_obj.close_modal(section["close_selector"], section["modal"])


@pytest.mark.rnd
def test_rnd_rp_progress_completion_screen(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-016: the Progress Completion screen offers the project selects and View Project Members."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "progress_completion.login", "progress_completion.menu_path",
        "progress_completion.heading", "progress_completion.breadcrumb",
        "progress_completion.area_select", "progress_completion.project_select",
        "progress_completion.view_members_button",
        "progress_completion.back_link",
    )
    section = data["progress_completion"]
    login_as(section["login"])
    page_obj = _completion(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.expect_screen(
        section["heading"], section["breadcrumb"], section["area_select"],
        section["project_select"], section["view_members_button"],
        section["back_link"],
    )


@pytest.mark.rnd
def test_rnd_rp_progress_completion_members(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-016: View Project Members lists the member table or the documented empty state."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "progress_completion_members.login",
        "progress_completion_members.menu_path",
        "progress_completion_members.filters",
        "progress_completion_members.view_members_button",
        "progress_completion_members.member_columns",
        "progress_completion_members.empty_state",
    )
    section = data["progress_completion_members"]
    login_as(section["login"])
    page_obj = _completion(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_project_members(section["filters"],
                                  section["view_members_button"])
    page_obj.expect_list_columns(section["member_columns"])
    page_obj.expect_members_or_empty(section["empty_state"],
                                     section.get("member_row"))


@pytest.mark.rnd
def test_rnd_rp_mark_member_completion(page, uucms_settings, login_as):
    """TC-PROJECTPROGRESS-016: selected PI-approved members are marked as completion."""
    data = _require_rp_data(
        load_test_data(DATA_FILE),
        "mark_completion.login", "mark_completion.menu_path",
        "mark_completion.filters", "mark_completion.view_members_button",
        "mark_completion.member_row", "mark_completion.completion_checkboxes",
        "mark_completion.mark_button", "mark_completion.success_selector",
    )
    section = data["mark_completion"]
    login_as(section["login"])
    page_obj = _completion(page, uucms_settings)
    page_obj.open_from_menu(section["menu_path"])
    page_obj.view_project_members(section["filters"],
                                  section["view_members_button"])
    if page_obj.row_count(section["member_row"]) == 0:
        pytest.skip("no PI-approved project members to mark as completion")
    page_obj.mark_completion(
        section["completion_checkboxes"], section["mark_button"],
        section["success_selector"],
    )
