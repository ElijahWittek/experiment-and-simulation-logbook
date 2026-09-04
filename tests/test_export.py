import csv

from experiment_and_simulation_logbook.export import (
    export_logbook,
    format_parameters,
)


def make_export_entries():
    return [
        {
            "id": 2,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {
                "particles": "500",
                "duration": "60 s",
                "method": "Euler",
            },
            "status": "completed",
            "result_summary": "Simulation completed without runtime errors.",
            "data_file": "",
            "notes": "Used as a completed example entry.",
        },
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {
                "grid_size": "100 x 100",
                "time_step": "0.01 s",
                "iterations": "1000",
            },
            "status": "open",
            "result_summary": "",
            "data_file": "data/heat_diffusion_input.csv",
            "notes": "Initial test with default boundary conditions.",
        },
    ]

def test_format_parameters_returns_readable_text():
    parameters = {
        "grid_size": "100 x 100",
        "time_step": "0.01 s",
        "iterations": "1000",
    }

    result = format_parameters(parameters)

    assert result == (
        "grid_size=100 x 100; "
        "time_step=0.01 s; "
        "iterations=1000"
    )

def test_format_parameters_returns_empty_text_for_no_parameters():
    assert format_parameters({}) == ""

def test_export_logbook_creates_csv_file(tmp_path):
    path = tmp_path / "logbook_export.csv"

    export_logbook(make_export_entries(), path)

    assert path.exists()

def test_export_logbook_uses_expected_columns(tmp_path):
    path = tmp_path / "logbook_export.csv"

    export_logbook([], path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader)

    assert header == [
        "id",
        "title",
        "created_date",
        "status",
        "parameters",
        "result_summary",
        "data_file",
        "notes",
    ]

def test_export_logbook_sorts_entries_by_id_ascending(tmp_path):
    path = tmp_path / "logbook_export.csv"

    export_logbook(make_export_entries(), path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert [row["id"] for row in rows] == ["1", "2"]

def test_export_logbook_formats_parameters(tmp_path):
    path = tmp_path / "logbook_export.csv"

    export_logbook(make_export_entries(), path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(csv.DictReader(csv_file))

    assert rows[0]["parameters"] == (
        "grid_size=100 x 100; "
        "time_step=0.01 s; "
        "iterations=1000"
    )

def test_export_empty_logbook_contains_only_header(tmp_path):
    path = tmp_path / "logbook_export.csv"

    export_logbook([], path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(csv.reader(csv_file))

    assert len(rows) == 1

def test_export_logbook_overwrites_existing_file(tmp_path):
    path = tmp_path / "logbook_export.csv"
    path.write_text(
        "old content that must disappear",
        encoding="utf-8",
    )

    export_logbook([], path)

    with path.open(
        encoding="utf-8",
        newline="",
    ) as csv_file:
        rows = list(csv.reader(csv_file))

    assert rows == [
        [
            "id",
            "title",
            "created_date",
            "status",
            "parameters",
            "result_summary",
            "data_file",
            "notes",
        ]
    ]

def test_export_logbook_creates_missing_parent_directory(tmp_path):
    path = tmp_path / "output" / "logbook_export.csv"

    export_logbook([], path)

    assert path.parent.exists()
    assert path.exists()
