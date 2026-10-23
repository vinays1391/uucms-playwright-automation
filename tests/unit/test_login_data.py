"""Unit tests for loading the shared login registry."""

import json
from pathlib import Path

import pytest

from uucms.auth.login_data import load_login_data


def _write_workbook(path: Path, rows: list[tuple[str, str, str]]) -> None:
    from openpyxl import Workbook

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Roles"
    worksheet.append(("role_key", "username", "password_env"))
    for row in rows:
        worksheet.append(row)
    workbook.save(path)
    workbook.close()


def test_load_login_data_falls_back_to_json_when_excel_is_absent(
    tmp_path: Path,
) -> None:
    login_dir = tmp_path / "test_data" / "login"
    login_dir.mkdir(parents=True)
    expected = {
        "username": "json-default",
        "password_env": "UUCMS_TEST_PASSWORD",
        "roles": {"student": {"username": "json-student"}},
    }
    (login_dir / "LoginData.json").write_text(
        json.dumps(expected), encoding="utf-8"
    )

    assert load_login_data(tmp_path) == expected


def test_load_login_data_prefers_excel_when_both_files_exist(
    tmp_path: Path,
) -> None:
    login_dir = tmp_path / "test_data" / "login"
    login_dir.mkdir(parents=True)
    (login_dir / "LoginData.json").write_text(
        json.dumps({"username": "json-default"}), encoding="utf-8"
    )
    _write_workbook(
        login_dir / "LoginData.xlsx",
        [
            ("default", "excel-default", "UUCMS_TEST_PASSWORD"),
            ("candidate_1", "excel-candidate", "UUCMS_TEST_PASSWORD"),
        ],
    )

    assert load_login_data(tmp_path) == {
        "username": "excel-default",
        "password_env": "UUCMS_TEST_PASSWORD",
        "roles": {
            "candidate_1": {
                "username": "excel-candidate",
                "password_env": "UUCMS_TEST_PASSWORD",
            }
        },
    }


def test_load_login_data_requires_default_row_in_excel(tmp_path: Path) -> None:
    login_dir = tmp_path / "test_data" / "login"
    login_dir.mkdir(parents=True)
    _write_workbook(
        login_dir / "LoginData.xlsx",
        [("candidate_1", "candidate-user", "UUCMS_TEST_PASSWORD")],
    )

    with pytest.raises(ValueError, match="role_key 'default'"):
        load_login_data(tmp_path)


def test_load_login_data_rejects_duplicate_excel_roles(tmp_path: Path) -> None:
    login_dir = tmp_path / "test_data" / "login"
    login_dir.mkdir(parents=True)
    _write_workbook(
        login_dir / "LoginData.xlsx",
        [
            ("default", "default-user", "UUCMS_TEST_PASSWORD"),
            ("student", "student-one", "UUCMS_TEST_PASSWORD"),
            ("student", "student-two", "UUCMS_TEST_PASSWORD"),
        ],
    )

    with pytest.raises(ValueError, match="Duplicate login role key 'student'"):
        load_login_data(tmp_path)
