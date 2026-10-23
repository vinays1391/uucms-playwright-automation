"""Generate multi-candidate Ph.D admission data from the roster CSV.

Usage:
    python scripts/generate_phd_multi_data.py
    python scripts/generate_phd_multi_data.py --limit 2            # pilot run
    python scripts/generate_phd_multi_data.py --rows 1,3,5         # specific rows

Reads test_data/admission/candidates_roster.csv and
test_data/admission/phd_admission_multi.template.json, layers each
candidate's values over the group stage templates, and writes
test_data/admission/phd_admission_multi.json (consumed by
test_phd_admission_multi_candidate_full_flow and
PhDAdmissionWorkflow.run_multi_candidate_flow).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = REPOSITORY_ROOT / "test_data" / "admission" / "candidates_roster.csv"
DEFAULT_TEMPLATE = (
    REPOSITORY_ROOT / "test_data" / "admission" / "phd_admission_multi.template.json"
)
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT / "test_data" / "admission" / "phd_admission_multi.json"
)

REQUIRED_COLUMNS = [
    "name", "login_id", "group",
    "entrance_mark_1", "entrance_mark_2",
    "interview_mark_1", "interview_mark_2",
    "challan_no", "amount_paid", "payment_date_day",
    "final_challan_no", "final_amount", "final_payment_date_day",
    "guide", "area_of_research", "category", "quota_type",
    "research_student_type",
    "interview_date_day", "invite_date_day", "verification_date_day",
]

PHD_MAPPING_FIELDS = {
    "#phdareaofResearchID": "area_of_research",
    "#phdGuideNameID": "guide",
    "#phdCategoryID": "category",
    "#phdQuotaType": "quota_type",
    "#phdResearchStudentTypeID": "research_student_type",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_roster(path: Path) -> list[dict]:
    if not path.exists():
        fail(
            f"Roster not found: {path}\n"
            "Copy candidates_roster.example.csv to candidates_roster.csv "
            "and fill it in."
        )
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [
            column for column in REQUIRED_COLUMNS if column not in (reader.fieldnames or [])
        ]
        if missing_columns:
            fail(f"Roster {path.name} is missing columns: {', '.join(missing_columns)}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if not any(str(value or "").strip() for value in row.values()):
                continue
            row["_line"] = line_number
            rows.append(row)
    if not rows:
        fail(f"Roster {path.name} contains no data rows")
    return rows


def check_required(row: dict) -> list[str]:
    missing = []
    for column in REQUIRED_COLUMNS:
        if not str(row.get(column, "") or "").strip():
            missing.append(column)
    return missing


def marks_fields(row: dict, prefix: str) -> list[dict]:
    return [
        {"selector": f"#Exammarks_{index}", "value": str(row[f"{prefix}_{index}"]).strip()}
        for index in (1, 2)
    ]


def build_candidate(row: dict, groups: dict) -> dict:
    group_id = str(row["group"]).strip()
    group = groups[group_id]
    phd_mapping = []
    for action in group["stages"]["document_verification"].get("phd_mapping", []):
        entry = dict(action)
        csv_field = PHD_MAPPING_FIELDS.get(str(entry.get("selector", "")))
        if csv_field and csv_field in row:
            entry["value"] = str(row[csv_field]).strip()
        phd_mapping.append(entry)

    return {
        "name": str(row["name"]).strip(),
        "login": f"candidate_{str(row['login_id']).strip()}",
        "group": group_id,
        "row_text": str(row["name"]).strip(),
        "offline_payment": {
            "challan_value": str(row["challan_no"]).strip(),
            "amount_value": str(row["amount_paid"]).strip(),
            "payment_date_day": str(row["payment_date_day"]).strip(),
        },
        "entrance_marks": {"marks_fields": marks_fields(row, "entrance_mark")},
        "interview_invite": {
            "date_day": str(row["interview_date_day"]).strip()
        },
        "interview_marks": {"marks_fields": marks_fields(row, "interview_mark")},
        "student_invite": {
            "date_day": str(row["invite_date_day"]).strip()
        },
        "document_verification": {
            "verification_date_day": str(row["verification_date_day"]).strip(),
            "phd_mapping": phd_mapping,
        },
        "final_payment": {
            "challan_value": str(row["final_challan_no"]).strip(),
            "amount_value": str(row["final_amount"]).strip(),
            "payment_date_day": str(row["final_payment_date_day"]).strip(),
        },
    }


def select_rows(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    selected = rows
    if args.rows:
        wanted = set()
        for part in args.rows.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                wanted.add(int(part))
            except ValueError:
                fail(f"--rows expects comma-separated line numbers, got {args.rows!r}")
        selected = [row for row in rows if row["_line"] in wanted]
        if not selected:
            fail(f"No roster rows match --rows {args.rows!r}")
    if args.limit and args.limit > 0:
        selected = selected[: args.limit]
    if not selected:
        fail("No roster rows selected")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Only use the first N roster rows (for a pilot run)",
    )
    parser.add_argument(
        "--rows", default="",
        help="Comma-separated roster line numbers (CSV line, header = 1)",
    )
    args = parser.parse_args()

    if not args.template.exists():
        fail(f"Template not found: {args.template}")
    template = json.loads(args.template.read_text(encoding="utf-8"))
    groups = {}
    for group in template.get("groups") or []:
        group_id = str(group.get("id", "")).strip()
        if not group_id:
            fail("Every template group needs an 'id'")
        groups[group_id] = group
    if not groups:
        fail(f"No groups defined in {args.template.name}")

    rows = select_rows(load_roster(args.roster), args)

    problems = []
    candidates = []
    for row in rows:
        missing = check_required(row)
        if missing:
            problems.append(
                f"line {row['_line']} ({row.get('login_id', '?')}): "
                f"missing {', '.join(missing)}"
            )
            continue
        group_id = str(row["group"]).strip()
        if group_id not in groups:
            problems.append(
                f"line {row['_line']} ({row.get('login_id', '?')}): "
                f"unknown group {group_id!r}; available: {', '.join(groups)}"
            )
            continue
        candidates.append(build_candidate(row, groups))

    if problems:
        fail("Fix the roster and re-run:\n  - " + "\n  - ".join(problems))

    output = {
        "candidate_stages": template.get("candidate_stages", {}),
        "groups": template.get("groups", []),
        "candidates": candidates,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate["group"]] = counts.get(candidate["group"], 0) + 1
    summary = ", ".join(f"{group}: {count}" for group, count in counts.items())
    try:
        display_path = args.out.relative_to(REPOSITORY_ROOT)
    except ValueError:
        display_path = args.out
    print(f"Wrote {display_path}")
    print(f"Candidates: {len(candidates)} ({summary})")


if __name__ == "__main__":
    main()
