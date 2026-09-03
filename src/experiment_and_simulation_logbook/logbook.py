"""Business logic for managing logbook entries."""

from datetime import UTC, datetime

from experiment_and_simulation_logbook.validation import (
    clean_optional_text,
    validate_logbook_data,
    validate_parameters,
    validate_search_term,
    validate_status,
    validate_title,
)


def get_next_id(entries: list[dict]) -> int:
    """Return the next available logbook entry ID."""
    if not entries:
        return 1

    highest_id = max(entry["id"] for entry in entries)

    return highest_id + 1

def create_logbook_entry(
        entries: list[dict],
        title: str,
        parameters: list[tuple[str, str]] | None = None,
        result_summary: str = "",
        data_file: str = "",
        notes: str = "",
) -> dict:
    """Create and return a validated logbook entry."""
    parameter_input = [] if parameters is None else parameters

    entry = {
        "id": get_next_id(entries),
        "title": validate_title(title),
        "created_date": datetime.now(UTC).astimezone().date().isoformat(),
        "parameters": validate_parameters(parameter_input),
        "status": "open",
        "result_summary": clean_optional_text(result_summary),
        "data_file": clean_optional_text(data_file),
        "notes": clean_optional_text(notes),
    }

    validate_logbook_data([entry])

    return entry

def sort_entries_by_id(entries: list[dict]) -> list[dict]:
    """Return logbook entries sorted by ID in descending order."""
    return sorted(
        entries,
        key=lambda entry: entry["id"],
        reverse=True,
    )

def filter_entries_by_status(
        entries: list[dict],
        status: str,
) -> list[dict]:
    """Return logbook entries matching the requested status."""
    normalized_status = validate_status(status)

    matching_entries = [
        entry
        for entry in entries
        if entry["status"] == normalized_status
    ]

    return sort_entries_by_id(matching_entries)

def filter_entries_by_title(
        entries: list[dict],
        search_term: str,
) -> list[dict]:
    """Return logbook entries whose titles contain the search term."""
    cleaned_search_term = validate_search_term(search_term)
    normalized_search_term = cleaned_search_term.casefold()

    matching_entries = [
        entry
        for entry in entries
        if normalized_search_term in entry["title"].casefold()
    ]

    return sort_entries_by_id(matching_entries)

def complete_logbook_entry(
        entries: list[dict],
        entry_id: int,
) -> bool:
    """Mark an open logbook entry as completed."""
    for entry in entries:
        if entry["id"] != entry_id:
            continue

        if entry["status"] == "completed":
            return False

        entry["status"] = "completed"
        return True

    raise ValueError(f"Logbook entry with ID {entry_id} does not exist.")
