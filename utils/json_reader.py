"""JSON helper for test-data access."""

import json
from pathlib import Path


def load_json(path: str | Path) -> dict:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _resolve(data: dict, path: str):
    node = data
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def require_fields(data: dict, fields: list[str], file_name: str) -> dict:
    """Guard a test-data file: every dotted field must exist and carry no
    REPLACE_WITH placeholder. Raises ValueError otherwise so the test
    refuses to run until the data is filled from a recording."""
    missing = []
    for field in fields:
        value = _resolve(data, field)
        if value is None or value == "" or value == [] or value == {}:
            missing.append(field)
    if missing:
        raise ValueError(
            f"{file_name} is missing required fields: {', '.join(missing)}"
        )
    placeholder_fields = [
        field for field in fields if "REPLACE_WITH" in str(_resolve(data, field))
    ]
    if placeholder_fields:
        raise ValueError(
            f"Complete {file_name} with recorded selectors and values; "
            "REPLACE_WITH placeholders are still present for: "
            + ", ".join(placeholder_fields)
        )
    return data
