"""CSV export for logbook data."""

import csv
from pathlib import Path

from experiment_and_simulation_logbook.validation import validate_logbook_data

EXPORT_PATH = Path("output/logbook_export.csv")

EXPORT_FIELDS = [
    "id",
    "title",
    "created_date",
    "status",
    "parameters",
    "result_summary",
    "data_file",
    "notes",
]


def format_parameters(parameters: dict[str, str]) -> str:
    """Format logbook parameters for CSV output."""
    return "; ".join(
        f"{name}={value}"
        for name, value in parameters.items()
    )

def export_logbook(
        entries: list[dict],
        path: Path = EXPORT_PATH,
) -> None:
    """Export all logbook entries to a CSV file."""
    validate_logbook_data(entries)

    sorted_entries = sorted(
        entries,
        key=lambda entry: entry["id"],
    )

    try:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file,
                fieldnames=EXPORT_FIELDS,
            )

            writer.writeheader()

            for entry in sorted_entries:
                export_entry = {
                    "id": entry["id"],
                    "title": entry["title"],
                    "created_date": entry["created_date"],
                    "status": entry["status"],
                    "parameters": format_parameters(entry["parameters"]),
                    "result_summary": entry["result_summary"],
                    "data_file": entry["data_file"],
                    "notes": entry["notes"],
                }

                writer.writerow(export_entry)

    except OSError as error:
        raise OSError(f"Could not write CSV export: {path}") from error
