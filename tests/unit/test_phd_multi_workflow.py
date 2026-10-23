"""Unit tests for the multi-candidate Ph.D admission flow."""

from unittest.mock import Mock

import pytest

from uucms.core.data_driven_form_page import DataDrivenFormPage
from uucms.workflows.phd_workflow import PhDAdmissionWorkflow
from utils.stage_merge import deep_merge


def test_deep_merge_layers_nested_dicts_and_replaces_lists() -> None:
    base = {"a": 1, "nested": {"x": 1, "y": 2}, "list": [1, 2]}
    override = {"nested": {"y": 3, "z": 4}, "list": [9]}

    merged = deep_merge(base, override)

    assert merged == {"a": 1, "nested": {"x": 1, "y": 3, "z": 4}, "list": [9]}
    assert base == {"a": 1, "nested": {"x": 1, "y": 2}, "list": [1, 2]}


def test_row_scoped_selector_scopes_to_candidate_row() -> None:
    assert (
        DataDrivenFormPage.row_scoped_selector("role=button[name='Save']", None)
        == "role=button[name='Save']"
    )
    assert (
        DataDrivenFormPage.row_scoped_selector(
            "role=button[name='View Student Details']", "Arun Kumar"
        )
        == 'tr:has-text("Arun Kumar") >> role=button[name=\'View Student Details\']'
    )
    assert (
        DataDrivenFormPage.row_scoped_selector("role=button[name='OK']", "  ")
        == "role=button[name='OK']"
    )


def _multi_data() -> dict:
    return {
        "candidate_stages": {
            "create_application": {"login": "candidate", "menu_entry_selector": "#menu"},
            "education_declaration": {"login": "candidate", "program_level": "Ph.D"},
            "application_details": {"login": "candidate", "discipline_selector": "#d"},
            "offline_payment": {"login": "candidate", "receipt_file": "f.pdf"},
            "final_payment": {"login": "candidate", "application_row_action": "tr td a"},
        },
        "groups": [
            {
                "id": "g1",
                "stages": {
                    "create_application": {
                        "actions": [{"selector": "#P", "value": "V"}]
                    },
                    "application_details": {"discipline_value": "PHYSICS"},
                    "entrance_view": {"login": "department_chairperson"},
                    "cut_off_marks": {"login": "department_chairperson"},
                    "review_approve": {
                        "login": "department_chairperson",
                        "view_student_details_selector": "role=button[name='View Student Details']",
                    },
                    "entrance_marks": {"login": "department_chairperson"},
                    "registrar_action": {"login": "registrar_admin"},
                    "interview_invite": {
                        "login": "department_chairperson",
                        "view_student_details_selector": "role=button[name='View Student Details']",
                    },
                    "interview_marks": {"login": "department_chairperson"},
                    "interview_marks_approval": {"login": "registrar_admin"},
                    "student_invite": {
                        "login": "department_chairperson",
                        "view_student_details_selector": "role=button[name='View Student Details']",
                    },
                    "document_verification": {
                        "login": "department_chairperson",
                        "phd_mapping": [{"selector": "#g", "value": "G"}],
                    },
                },
            }
        ],
        "candidates": [
            {
                "name": "Alpha",
                "login": "candidate_1",
                "group": "g1",
                "offline_payment": {"challan_value": "C1"},
                "interview_invite": {"date_day": "11"},
                "student_invite": {"date_day": "22"},
                "final_payment": {"challan_value": "F1"},
            },
            {
                "name": "Beta",
                "login": "candidate_2",
                "group": "g1",
                "offline_payment": {"challan_value": "C2"},
                "interview_invite": {"date_day": "12"},
                "student_invite": {"date_day": "23"},
                "final_payment": {"challan_value": "F2"},
            },
        ],
    }


def _mocked_workflow() -> tuple[PhDAdmissionWorkflow, list[str]]:
    workflow = PhDAdmissionWorkflow.__new__(PhDAdmissionWorkflow)
    workflow.candidate = Mock()
    order: list[str] = []
    for method in (
        "chairperson_views_entrance_candidates",
        "chairperson_sets_cut_off_marks",
        "chairperson_reviews_and_approves",
        "chairperson_enters_entrance_marks",
        "registrar_approves_or_rejects",
        "chairperson_invites_interview",
        "chairperson_enters_interview_marks",
        "registrar_approves_interview_marks",
        "chairperson_confirms_student_invite",
        "chairperson_verifies_documents",
        "candidate_submits_final_payment",
    ):
        setattr(workflow, method, Mock(side_effect=lambda *args, _m=method: order.append(_m)))
    return workflow, order


def test_multi_candidate_flow_runs_candidate_stages_per_candidate() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()

    workflow.run_multi_candidate_flow(data)

    create_calls = workflow.candidate.candidate_creates_application.call_args_list
    assert create_calls[0].args[0] == {
        "login": "candidate_1",
        "menu_entry_selector": "#menu",
        "actions": [{"selector": "#P", "value": "V"}],
        "row_text": "Alpha",
    }
    assert create_calls[1].args[0]["login"] == "candidate_2"
    payment_calls = workflow.candidate.candidate_submits_offline_payment.call_args_list
    assert payment_calls[0].args[0]["challan_value"] == "C1"
    assert payment_calls[1].args[0]["challan_value"] == "C2"
    final_calls = workflow.candidate_submits_final_payment.call_args_list
    assert final_calls[0].args[0]["login"] == "candidate_1"
    assert final_calls[0].args[0]["challan_value"] == "F1"
    assert final_calls[1].args[0]["login"] == "candidate_2"
    assert final_calls[1].args[0]["application_row_action"] == "tr td a"


def test_multi_candidate_flow_targets_candidate_rows_in_group_stages() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()

    workflow.run_multi_candidate_flow(data)

    review_calls = workflow.chairperson_reviews_and_approves.call_args_list
    assert review_calls[0].args[0]["row_text"] == "Alpha"
    assert review_calls[0].args[0]["login"] == "department_chairperson"
    assert review_calls[1].args[0]["row_text"] == "Beta"
    entrance_calls = workflow.chairperson_enters_entrance_marks.call_args_list
    assert entrance_calls[0].args[0]["row_text"] == "Alpha"
    assert entrance_calls[1].args[0]["row_text"] == "Beta"
    registrar_calls = workflow.registrar_approves_or_rejects.call_args_list
    assert registrar_calls[0].args[0]["row_text"] == "Alpha"
    assert registrar_calls[0].args[0]["login"] == "registrar_admin"
    document_calls = workflow.chairperson_verifies_documents.call_args_list
    assert document_calls[0].args[0]["row_text"] == "Alpha"
    assert document_calls[1].args[0]["phd_mapping"] == [{"selector": "#g", "value": "G"}]


def test_multi_candidate_flow_builds_batch_invite_stages() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()

    workflow.run_multi_candidate_flow(data)

    invite_stage = workflow.chairperson_invites_interview.call_args.args[0]
    assert invite_stage["students"] == [
        {"row_text": "Alpha", "date_day": "11"},
        {"row_text": "Beta", "date_day": "12"},
    ]
    assert "view_student_details_selector" not in invite_stage
    student_invite_stage = workflow.chairperson_confirms_student_invite.call_args.args[0]
    assert student_invite_stage["students"] == [
        {"row_text": "Alpha", "date_day": "22"},
        {"row_text": "Beta", "date_day": "23"},
    ]


def test_multi_candidate_flow_preserves_stage_order() -> None:
    workflow, order = _mocked_workflow()
    data = _multi_data()

    workflow.run_multi_candidate_flow(data)

    assert order == [
        "chairperson_views_entrance_candidates",
        "chairperson_sets_cut_off_marks",
        "chairperson_reviews_and_approves",
        "chairperson_enters_entrance_marks",
        "registrar_approves_or_rejects",
        "chairperson_reviews_and_approves",
        "chairperson_enters_entrance_marks",
        "registrar_approves_or_rejects",
        "chairperson_invites_interview",
        "chairperson_enters_interview_marks",
        "registrar_approves_interview_marks",
        "chairperson_enters_interview_marks",
        "registrar_approves_interview_marks",
        "chairperson_confirms_student_invite",
        "chairperson_verifies_documents",
        "chairperson_verifies_documents",
        "candidate_submits_final_payment",
        "candidate_submits_final_payment",
    ]


def test_multi_candidate_flow_rejects_empty_roster() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()
    data["candidates"] = []

    with pytest.raises(ValueError, match="at least one entry"):
        workflow.run_multi_candidate_flow(data)


def test_multi_candidate_flow_rejects_unknown_group() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()
    data["candidates"][0]["group"] = "nope"

    with pytest.raises(ValueError, match="Unknown group"):
        workflow.run_multi_candidate_flow(data)


def test_multi_candidate_flow_requires_candidate_name() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()
    data["candidates"][0]["name"] = "   "

    with pytest.raises(ValueError, match="missing a 'name'"):
        workflow.run_multi_candidate_flow(data)


def test_multi_candidate_flow_skips_groups_without_candidates() -> None:
    workflow, _ = _mocked_workflow()
    data = _multi_data()
    data["groups"].append({"id": "g2", "stages": {}})

    workflow.run_multi_candidate_flow(data)

    assert workflow.chairperson_views_entrance_candidates.call_count == 1
    assert workflow.chairperson_sets_cut_off_marks.call_count == 1
