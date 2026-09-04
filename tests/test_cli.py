import pytest

import experiment_and_simulation_logbook.cli as cli_module
from experiment_and_simulation_logbook.cli import (
    build_parser,
    format_logbook_entry,
    handle_add_command,
    handle_complete_command,
    handle_export_command,
    handle_filter_status_command,
    handle_filter_title_command,
    handle_list_command,
    prompt_for_parameters,
    run_cli,
)


def make_display_entry():
    return {
        "id": 2,
        "title": "Particle movement simulation",
        "created_date": "2026-09-15",
        "parameters": {
            "particles": "500",
            "method": "Euler",
        },
        "status": "completed",
        "result_summary": "Simulation completed without runtime errors.",
        "data_file": "",
        "notes": "",
    }

def test_parser_recognizes_add_command():
    parser = build_parser()

    arguments = parser.parse_args(["add"])

    assert arguments.command == "add"

def test_parser_recognizes_list_command():
    parser = build_parser()

    arguments = parser.parse_args(["list"])

    assert arguments.command == "list"


def test_parser_reads_status_filter_argument():
    parser = build_parser()

    arguments = parser.parse_args(
        ["filter-status", "COMPLETED"]
    )

    assert arguments.command == "filter-status"
    assert arguments.status == "COMPLETED"


def test_parser_reads_title_filter_argument():
    parser = build_parser()

    arguments = parser.parse_args(
        ["filter-title", "heat diffusion"]
    )

    assert arguments.command == "filter-title"
    assert arguments.search_term == "heat diffusion"


def test_parser_reads_complete_id_argument_as_text():
    parser = build_parser()

    arguments = parser.parse_args(
        ["complete", "7"]
    )

    assert arguments.command == "complete"
    assert arguments.entry_id == "7"


def test_parser_recognizes_export_command():
    parser = build_parser()

    arguments = parser.parse_args(["export"])

    assert arguments.command == "export"

def test_format_logbook_entry_display_all_fields():
    result = format_logbook_entry(make_display_entry())

    assert "ID: 2" in result
    assert "Title: Particle movement simulation" in result
    assert "Created date: 2026-09-15" in result
    assert "Status: completed" in result
    assert "Parameters:" in result
    assert "  particles: 500" in result
    assert "  method: Euler" in result
    assert (
        "Result summary: Simulation completed without runtime errors."
        in result
    )
    assert "Data file: Not specified" in result
    assert "Notes: Not specified" in result

def test_format_logbook_entry_displays_missing_parameters():
    entry = make_display_entry()
    entry["parameters"] = {}

    result = format_logbook_entry(entry)

    assert "Parameters:\n  Not specified" in result

def test_handle_list_command_displays_entries_sorted_descending(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
        {
            "id": 3,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {},
            "status": "completed",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
    ]

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        lambda: entries,
    )

    handle_list_command()

    output = capsys.readouterr().out

    assert output.index("ID: 3") < output.index("ID: 1")


def test_handle_list_command_reports_empty_logbook(
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        list,
    )

    handle_list_command()

    output = capsys.readouterr().out

    assert output == "Info: No logbook entries found.\n"


def test_handle_filter_status_command_displays_matching_entries(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
        {
            "id": 2,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {},
            "status": "completed",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
    ]

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        lambda: entries,
    )

    handle_filter_status_command("COMPLETED")

    output = capsys.readouterr().out

    assert "ID: 2" in output
    assert "Particle movement simulation" in output
    assert "ID: 1" not in output


def test_handle_filter_title_command_displays_matching_entries(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
        {
            "id": 2,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {},
            "status": "completed",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        },
    ]

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        lambda: entries,
    )

    handle_filter_title_command(" heat ")

    output = capsys.readouterr().out

    assert "ID: 1" in output
    assert "Heat diffusion test run" in output
    assert "ID: 2" not in output


def test_filter_commands_report_no_matches(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        }
    ]

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        lambda: entries,
    )

    handle_filter_title_command("particle")

    output = capsys.readouterr().out

    assert output == "Info: No matching logbook entries found.\n"

def test_handle_complete_command_changes_and_saves_entry(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 2,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        }
    ]
    saved_data = []

    def fake_load_logbook():
        return entries

    def fake_save_logbook(updated_entries):
        saved_data.extend(updated_entries)

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        fake_load_logbook,
    )
    monkeypatch.setattr(
        cli_module,
        "save_logbook",
        fake_save_logbook,
    )

    handle_complete_command("2")

    output = capsys.readouterr().out

    assert entries[0]["status"] == "completed"
    assert saved_data == entries
    assert output == (
        "Success: Logbook entry with ID 2 marked as completed.\n"
    )


def test_handle_complete_command_does_not_save_completed_entry(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 2,
            "title": "Particle movement simulation",
            "created_date": "2026-09-15",
            "parameters": {},
            "status": "completed",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        }
    ]
    save_called = False

    def fake_load_logbook():
        return entries

    def fake_save_logbook(updated_entries):
        nonlocal save_called
        save_called = True

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        fake_load_logbook,
    )
    monkeypatch.setattr(
        cli_module,
        "save_logbook",
        fake_save_logbook,
    )

    handle_complete_command("2")

    output = capsys.readouterr().out

    assert save_called is False
    assert output == (
        "Info: Logbook entry with ID 2 is already completed.\n"
    )

def test_handle_export_command_loads_and_exports_entries(
    monkeypatch,
    capsys,
):
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        }
    ]
    exported_data = []

    def fake_load_logbook():
        return entries

    def fake_export_logbook(export_entries):
        exported_data.extend(export_entries)

    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        fake_load_logbook,
    )
    monkeypatch.setattr(
        cli_module,
        "export_logbook",
        fake_export_logbook,
    )

    handle_export_command()

    output = capsys.readouterr().out

    assert exported_data == entries
    assert output == (
        f"Success: Logbook exported to {cli_module.EXPORT_PATH}.\n"
    )

def test_prompt_for_parameters_collects_multiple_parameters(
    monkeypatch,
):
    answers = iter(
        [
            "grid_size",
            "100 x 100",
            "time_step",
            "0.01 s",
            "",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(answers),
    )

    parameters = prompt_for_parameters()

    assert parameters == [
        ("grid_size", "100 x 100"),
        ("time_step", "0.01 s"),
    ]


def test_prompt_for_parameters_allows_no_parameters(
    monkeypatch,
):
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "",
    )

    assert prompt_for_parameters() == []

def test_handle_add_command_creates_and_saves_entry(
    monkeypatch,
    capsys,
):
    existing_entries = [
        {
            "id": 3,
            "title": "Existing simulation",
            "created_date": "2026-09-14",
            "parameters": {},
            "status": "open",
            "result_summary": "",
            "data_file": "",
            "notes": "",
        }
    ]
    saved_data = []

    answers = iter(
        [
            "  Heat diffusion test run  ",
            "grid_size",
            "100 x 100",
            "time_step",
            "0.01 s",
            "",
            "  Initial result.  ",
            "  data/input.csv  ",
            "  First test run.  ",
        ]
    )

    def fake_load_logbook():
        return existing_entries.copy()

    def fake_save_logbook(entries):
        saved_data.extend(entries)

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: next(answers),
    )
    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        fake_load_logbook,
    )
    monkeypatch.setattr(
        cli_module,
        "save_logbook",
        fake_save_logbook,
    )

    handle_add_command()

    output = capsys.readouterr().out

    assert len(saved_data) == 2

    new_entry = saved_data[1]

    assert new_entry["id"] == 4
    assert new_entry["title"] == "Heat diffusion test run"
    assert new_entry["parameters"] == {
        "grid_size": "100 x 100",
        "time_step": "0.01 s",
    }
    assert new_entry["status"] == "open"
    assert new_entry["result_summary"] == "Initial result."
    assert new_entry["data_file"] == "data/input.csv"
    assert new_entry["notes"] == "First test run."

    assert output == (
        "Success: Logbook entry with ID 4 created.\n"
    )

def test_handle_add_command_does_not_save_invalid_title(
    monkeypatch,
):
    save_called = False

    def fake_load_logbook():
        return []

    def fake_save_logbook(entries):
        nonlocal save_called
        save_called = True

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt: "   ",
    )
    monkeypatch.setattr(
        cli_module,
        "load_logbook",
        fake_load_logbook,
    )
    monkeypatch.setattr(
        cli_module,
        "save_logbook",
        fake_save_logbook,
    )

    with pytest.raises(
        ValueError,
        match="Title must not be empty",
    ):
        handle_add_command()

    assert save_called is False

def test_run_cli_dispatches_list_command(
    monkeypatch,
):
    list_called = False

    def fake_handle_list_command():
        nonlocal list_called
        list_called = True

    monkeypatch.setattr(
        cli_module,
        "handle_list_command",
        fake_handle_list_command,
    )

    run_cli(["list"])

    assert list_called is True

def test_run_cli_passes_status_argument(
    monkeypatch,
):
    received_status = None

    def fake_handle_filter_status_command(status):
        nonlocal received_status
        received_status = status

    monkeypatch.setattr(
        cli_module,
        "handle_filter_status_command",
        fake_handle_filter_status_command,
    )

    run_cli(
        [
            "filter-status",
            "COMPLETED",
        ]
    )

    assert received_status == "COMPLETED"

def test_run_cli_handles_expected_error(
    monkeypatch,
    capsys,
):
    def fake_handle_list_command():
        raise ValueError("Test error.")

    monkeypatch.setattr(
        cli_module,
        "handle_list_command",
        fake_handle_list_command,
    )

    run_cli(["list"])

    output = capsys.readouterr().out

    assert output == "Error: Test error.\n"

def test_run_cli_passes_complete_id(
    monkeypatch,
):
    received_id = None

    def fake_handle_complete_command(entry_id):
        nonlocal received_id
        received_id = entry_id

    monkeypatch.setattr(
        cli_module,
        "handle_complete_command",
        fake_handle_complete_command,
    )

    run_cli(
        [
            "complete",
            "7",
        ]
    )

    assert received_id == "7"
