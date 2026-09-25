"""JSON helper for test-data access."""

import json
from pathlib import Path


def load_json(path: str | Path) -> dict:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
