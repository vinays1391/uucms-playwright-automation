"""Unit tests for scripts/generate_phd_multi_data.py."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "generate_phd_multi_data.py"

spec = importlib.util.spec_from_file_location("generate_phd_multi_data", SCRIPT_PATH)
generate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate)


def _template() -> dict:
    return {
        "candidate_stages": {
            "create_application": {"login": "candidate"},
            "education_declaration": {"login": "candidate", "program_level": "Ph.D"},
            "application_details": {"login": "candidate"},
            "offline_payment": {"login": "candidate"},
            "final_payment": {"login": "candidate"},
        },
        "groups": [
            {
                "id": "physics",
                "stages": {
                    "create_application": {
                        "actions": [{"selector": "#P", "value": "PL"}]
                    },
                    "entrance_view": {"login": "department_chairperson"},
                    "cut_off_marks": {"login": "department_chairperson"},
                    "review_approve": {"login": "department_chairperson"},
                    "entrance_marks": {"login": "department_chairperson"},
                    "registrar_action": {"login": "registrar_admin"},
                    "interview_invite": {"login": "department_chairperson"},
                    "interview_marks": {"login": "department_chairperson"},
                    "interview_marks_approval": {"login": "registrar_admin"},
                    "student_invite": {"login": "department_chairperson"},
                    "document_verification": {
                        "login": "department_chairperson",
                        "phd_mapping": [
                            {"selector": "#phdDisciplineID", "value": "PHYSICS"},
                            {"selector": "#phdareaofResearchID", "value": "REPLACE_AOR"},
                            {"selector": "#phdGuideNameID", "value": "REPLACE_GUIDE"},
                            {"selector": "#phdCategoryID", "value": "REPLACE_CAT"},
                            {"selector": "#phdQuotaType", "value": "REPLACE_QUOTA"},
                            {"selector": "#phdResearchStudentTypeID", "value": "REPLACE_TYPE"},
                        ],
                    },
                },
            }
        ],
    }


ROW = {
    "name": "Arun Kumar",
    "login_id": "2200494727",
    "group": "physics",
    "password": "",
    "entrance_mark_1": "70",
    "entrance_mark_2": "65",
    "interview_mark_1": "60",
    "interview_mark_2": "62",
    "challan_no": "CH1",
    "amount_paid": "1000",
    "payment_date_day": "10",
    "final_challan_no": "CH2",
    "final_amount": "20000",
    "final_payment_date_day": "20",
    "guide": "Dr. G",
    "area_of_research": "Astrophysics",
    "category": "GEN",
    "quota_type": "OPEN",
    "research_student_type": "FULL_TIME",
    "interview_date_day": "15",
    "invite_date_day": "18",
    "verification_date_day": "25",
    "_line": 2,
}


def test_check_required_flags_empty_fields() -> None:
    row = dict(ROW)
    row["guide"] = "   "
    row["final_amount"] = ""

    missing = generate.check_required(row)

    assert "guide" in missing
    assert "final_amount" in missing
    assert "name" not in missing


def test_build_candidate_layers_values_over_group_mapping() -> None:
    template = _template()
    groups = {group["id"]: group for group in template["groups"]}

    candidate = generate.build_candidate(dict(ROW), groups)

    assert candidate["name"] == "Arun Kumar"
    assert candidate["login"] == "candidate_2200494727"
    assert candidate["row_text"] == "Arun Kumar"
    assert candidate["group"] == "physics"
    assert candidate["offline_payment"] == {
        "challan_value": "CH1",
        "amount_value": "1000",
        "payment_date_day": "10",
    }
    assert candidate["entrance_marks"] == {
        "marks_fields": [
            {"selector": "#Exammarks_1", "value": "70"},
            {"selector": "#Exammarks_2", "value": "65"},
        ]
    }
    assert candidate["interview_invite"] == {"date_day": "15"}
    assert candidate["student_invite"] == {"date_day": "18"}
    assert candidate["final_payment"] == {
        "challan_value": "CH2",
        "amount_value": "20000",
        "payment_date_day": "20",
    }
    mapping = {
        entry["selector"]: entry["value"]
        for entry in candidate["document_verification"]["phd_mapping"]
    }
    assert mapping["#phdDisciplineID"] == "PHYSICS"
    assert mapping["#phdareaofResearchID"] == "Astrophysics"
    assert mapping["#phdGuideNameID"] == "Dr. G"
    assert mapping["#phdCategoryID"] == "GEN"
    assert mapping["#phdQuotaType"] == "OPEN"
    assert mapping["#phdResearchStudentTypeID"] == "FULL_TIME"
    assert candidate["document_verification"]["verification_date_day"] == "25"


def test_select_rows_limit_and_line_numbers() -> None:
    rows = [dict(ROW, _line=line) for line in (2, 3, 4, 5)]

    limited = generate.select_rows(
        rows, type("Args", (), {"limit": 2, "rows": ""})()
    )
    assert [row["_line"] for row in limited] == [2, 3]

    picked = generate.select_rows(
        rows, type("Args", (), {"limit": 0, "rows": "3,5"})()
    )
    assert [row["_line"] for row in picked] == [3, 5]


def test_generate_writes_multi_data_file(tmp_path: Path) -> None:
    roster = tmp_path / "roster.csv"
    roster.write_text(
        "name,login_id,group,password,entrance_mark_1,entrance_mark_2,"
        "interview_mark_1,interview_mark_2,challan_no,amount_paid,"
        "payment_date_day,final_challan_no,final_amount,final_payment_date_day,"
        "guide,area_of_research,category,quota_type,research_student_type,"
        "interview_date_day,invite_date_day,verification_date_day\n"
        "Arun Kumar,2200494727,physics,,70,65,60,62,CH1,1000,10,CH2,20000,20,"
        "Dr. G,Astrophysics,GEN,OPEN,FULL_TIME,15,18,25\n",
        encoding="utf-8",
    )
    template = tmp_path / "template.json"
    template.write_text(json.dumps(_template()), encoding="utf-8")
    out = tmp_path / "multi.json"

    with patch.object(
        sys,
        "argv",
        ["prog", "--roster", str(roster), "--template", str(template), "--out", str(out)],
    ):
        generate.main()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["candidate_stages"] == _template()["candidate_stages"]
    assert [group["id"] for group in data["groups"]] == ["physics"]
    assert len(data["candidates"]) == 1
    assert data["candidates"][0]["login"] == "candidate_2200494727"


def test_generate_rejects_incomplete_roster(tmp_path: Path) -> None:
    roster = tmp_path / "roster.csv"
    roster.write_text(
        "name,login_id,group,entrance_mark_1\n"
        "Arun Kumar,2200494727,physics,70\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit):
        generate.load_roster(roster)


def test_generate_rejects_unknown_group(tmp_path: Path) -> None:
    roster = tmp_path / "roster.csv"
    roster.write_text(
        "name,login_id,group,password,entrance_mark_1,entrance_mark_2,"
        "interview_mark_1,interview_mark_2,challan_no,amount_paid,"
        "payment_date_day,final_challan_no,final_amount,final_payment_date_day,"
        "guide,area_of_research,category,quota_type,research_student_type,"
        "interview_date_day,invite_date_day,verification_date_day\n"
        "Arun Kumar,2200494727,astro,,70,65,60,62,CH1,1000,10,CH2,20000,20,"
        "Dr. G,Astrophysics,GEN,OPEN,FULL_TIME,15,18,25\n",
        encoding="utf-8",
    )
    template = tmp_path / "template.json"
    template.write_text(json.dumps(_template()), encoding="utf-8")
    out = tmp_path / "multi.json"

    with patch.object(
        sys,
        "argv",
        ["prog", "--roster", str(roster), "--template", str(template), "--out", str(out)],
    ):
        with pytest.raises(SystemExit):
            generate.main()

    assert not out.exists()
