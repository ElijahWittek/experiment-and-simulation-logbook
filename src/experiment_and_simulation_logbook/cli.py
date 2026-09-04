"""Command-line interface for the logbook application."""

import argparse

from experiment_and_simulation_logbook.export import (
    EXPORT_PATH,
    export_logbook,
)
from experiment_and_simulation_logbook.logbook import (
    complete_logbook_entry,
    create_logbook_entry,
    filter_entries_by_status,
    filter_entries_by_title,
    sort_entries_by_id,
)
from experiment_and_simulation_logbook.persistence import (
    load_logbook,
    save_logbook,
)
from experiment_and_simulation_logbook.validation import (
    validate_id_input,
    validate_title,
)


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="experiment-and-simulation-logbook",
        description="Manage experiment and simulation logbook entries.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "add",
        help="Add a new logbook entry.",
    )

    subparsers.add_parser(
        "list",
        help="List all logbook entries.",
    )

    status_parser = subparsers.add_parser(
        "filter-status",
        help="Filter logbook entries by status.",
    )
    status_parser.add_argument(
        "status",
        help="Status to filter by: open or completed.",
    )

    title_parser = subparsers.add_parser(
        "filter-title",
        help="Filter logbook entries by title.",
    )
    title_parser.add_argument(
        "search_term",
        help="Search term for the entry title.",
    )

    complete_parser = subparsers.add_parser(
        "complete",
        help="Mark a logbook entry as completed.",
    )
    complete_parser.add_argument(
        "entry_id",
        help="ID of the logbook entry to complete.",
    )

    subparsers.add_parser(
        "export",
        help="Export all logbook entries to CSV.",
    )

    return parser

def format_logbook_entry(entry: dict) -> str:
    """Format one logbook entry for terminal output."""
    parameters = entry["parameters"]

    if parameters:
        parameter_lines = [
            f"  {name}: {value}"
            for name, value in parameters.items()
        ]
    else:
        parameter_lines = ["  Not specified"]

    result_summary = entry["result_summary"] or "Not specified"
    data_file = entry["data_file"] or "Not specified"
    notes = entry["notes"] or "Not specified"

    lines = [
        f"ID: {entry['id']}",
        f"Title: {entry['title']}",
        f"Created date: {entry['created_date']}",
        f"Status: {entry['status']}",
        "Parameters:",
        *parameter_lines,
        f"Result summary: {result_summary}",
        f"Data file: {data_file}",
        f"Notes: {notes}",
    ]

    return "\n".join(lines)

def print_logbook_entries(
        entries: list[dict],
        empty_message: str,
) -> None:
    """Print logbook entries or an informational message."""
    if not entries:
        print(f"Info: {empty_message}")
        return

    formatted_entries = [
        format_logbook_entry(entry)
        for entry in entries
    ]

    print("\n\n".join(formatted_entries))

def prompt_for_parameters() -> list[tuple[str, str]]:
    """Prompt the user for optional parameter name-value pairs."""
    parameters = []

    while True:
        name = input(
            "Parameter name (leave empty to finish): "
        )

        if not name.strip():
            break

        value = input("Parameter value: ")
        parameters.append((name, value))

    return parameters

def handle_list_command() -> None:
    """Load and display all logbook entries."""
    entries = load_logbook()
    sorted_entries = sort_entries_by_id(entries)

    print_logbook_entries(
        sorted_entries,
        "No logbook entries found.",
    )


def handle_filter_status_command(status: str) -> None:
    """Load and display logbook entries matching a status."""
    entries = load_logbook()
    matching_entries = filter_entries_by_status(
        entries,
        status,
    )

    print_logbook_entries(
        matching_entries,
        "No matching logbook entries found.",
    )


def handle_filter_title_command(search_term: str) -> None:
    """Load and display logbook entries matching a title search."""
    entries = load_logbook()
    matching_entries = filter_entries_by_title(
        entries,
        search_term,
    )

    print_logbook_entries(
        matching_entries,
        "No matching logbook entries found.",
    )

def handle_complete_command(entry_id: str) -> None:
    """Mark a logbook entry as completed and save the change."""
    validated_id = validate_id_input(entry_id)
    entries = load_logbook()

    changed = complete_logbook_entry(
        entries,
        validated_id,
    )

    if not changed:
        print(
            f"Info: Logbook entry with ID {validated_id} "
            "is already completed."
        )
        return

    save_logbook(entries)

    print(
        f"Success: Logbook entry with ID {validated_id} "
        "marked as completed."
    )

def handle_export_command() -> None:
    """Export all logbook entries to the configured CSV file."""
    entries = load_logbook()

    export_logbook(entries)

    print(
        f"Success: Logbook exported to {EXPORT_PATH}."
    )

def handle_add_command() -> None:
    """Interactively create and save a new logbook entry."""
    entries = load_logbook()

    title = input("Title: ")
    cleaned_title = validate_title(title)

    parameters = prompt_for_parameters()

    result_summary = input(
        "Result summary (optional): "
    )
    data_file = input(
        "Data file (optional): "
    )
    notes = input(
        "Notes (optional): "
    )

    entry = create_logbook_entry(
        entries=entries,
        title=cleaned_title,
        parameters=parameters,
        result_summary=result_summary,
        data_file=data_file,
        notes=notes,
    )

    entries.append(entry)
    save_logbook(entries)

    print(
        f"Success: Logbook entry with ID {entry['id']} created."
    )

def run_cli(arguments: list[str] | None = None) -> None:
    """Parse command-line arguments and execute the selected command."""
    parser = build_parser()
    parsed_arguments = parser.parse_args(arguments)

    try:
        if parsed_arguments.command == "add":
            handle_add_command()

        elif parsed_arguments.command == "list":
            handle_list_command()

        elif parsed_arguments.command == "filter-status":
            handle_filter_status_command(
                parsed_arguments.status,
            )

        elif parsed_arguments.command == "filter-title":
            handle_filter_title_command(
                parsed_arguments.search_term,
            )

        elif parsed_arguments.command == "complete":
            handle_complete_command(
                parsed_arguments.entry_id,
            )

        elif parsed_arguments.command == "export":
            handle_export_command()

    except (ValueError, TypeError, OSError) as error:
        print(f"Error: {error}")
