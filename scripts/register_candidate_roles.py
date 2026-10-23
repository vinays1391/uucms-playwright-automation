"""Register roster candidates as login roles in the login registry.

Usage:
    set UUCMS_CANDIDATE_PASSWORD=shared_password
    python scripts/register_candidate_roles.py

Adds one role per roster row to test_data/login/LoginData.json:
    role key: candidate_<login_id>, username: <login_id>

The password comes from the roster 'password' column when present,
otherwise from the UUCMS_CANDIDATE_PASSWORD environment variable
(one shared password for all candidates). Rows without either are
skipped with a warning. The registry file is git-ignored; never share
it.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = REPOSITORY_ROOT / "test_data" / "admission" / "candidates_roster.csv"
DEFAULT_REGISTRY = REPOSITORY_ROOT / "test_data" / "login" / "LoginData.json"
PASSWORD_ENV = "UUCMS_CANDIDATE_PASSWORD"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()

    if not args.roster.exists():
        fail(f"Roster not found: {args.roster}")
    if not args.registry.exists():
        fail(f"Login registry not found: {args.registry}")

    with args.roster.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = [
            row for row in csv.DictReader(handle)
            if str(row.get("login_id", "") or "").strip()
        ]
    if not rows:
        fail(f"No rows with a login_id in {args.roster.name}")

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    roles = registry.setdefault("roles", {})

    added, updated, skipped = [], [], []
    for row in rows:
        line = row.get("_line", "?")
        login_id = str(row["login_id"]).strip()
        role_key = f"candidate_{login_id}"
        password = str(row.get("password", "") or "").strip() or os.getenv(PASSWORD_ENV, "").strip()
        if not password:
            skipped.append(f"{role_key} (no password in roster or {PASSWORD_ENV})")
            continue
        entry = {"username": login_id, "password": password}
        if role_key in roles and roles[role_key] == entry:
            continue
        if role_key in roles:
            updated.append(role_key)
        else:
            added.append(role_key)
        roles[role_key] = entry

    args.registry.write_text(
        json.dumps(registry, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    try:
        registry_display = args.registry.relative_to(REPOSITORY_ROOT)
    except ValueError:
        registry_display = args.registry
    print(f"Registry: {registry_display}")
    print(f"Added roles:   {len(added)}" + (f" ({', '.join(added)})" if added else ""))
    print(f"Updated roles: {len(updated)}" + (f" ({', '.join(updated)})" if updated else ""))
    if skipped:
        print("Skipped (no password):")
        for entry in skipped:
            print(f"  - {entry}")
        print(f"Set {PASSWORD_ENV} or fill the roster 'password' column, then re-run.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
