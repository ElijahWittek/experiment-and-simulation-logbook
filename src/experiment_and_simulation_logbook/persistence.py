"""JSON persistence for logbook data."""

import json
from pathlib import Path

from experiment_and_simulation_logbook.validation import validate_logbook_data

LOGBOOK_PATH = Path("data/logbook.json")


def load_logbook(path: Path = LOGBOOK_PATH) -> list[dict]:
    """Load and validate logbook entries from a JSON file."""
    if not path.exists():
        return []

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise OSError(f"Could not read logbook file: {path}") from error

    if not content.strip():
        raise ValueError("Logbook file is empty.")

    try:
        entries = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError("Logbook file contains invalid JSON.") from error

    validate_logbook_data(entries)

    return entries

def save_logbook(
        entries: list[dict],
        path: Path = LOGBOOK_PATH,
) -> None:
    """Save the complete logbook data to a JSON file."""
    validate_logbook_data(entries)
    content = json.dumps(
        entries,
        ensure_ascii=False,
        indent=4,
    )

    try:
        path.write_text(
            f"{content}\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise OSError(f"Could not write logbook file: {path}") from error
