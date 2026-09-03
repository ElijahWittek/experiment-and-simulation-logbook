from datetime import UTC, datetime

import pytest

import experiment_and_simulation_logbook
from experiment_and_simulation_logbook.logbook import (
    complete_logbook_entry,
    create_logbook_entry,
    filter_entries_by_status,
    filter_entries_by_title,
    get_next_id,
    sort_entries_by_id,
)


def test_package_can_be_imported() -> None:
    assert experiment_and_simulation_logbook is not None

def test_get_next_id_returns_one_for_empty_logbook():
    assert get_next_id([]) == 1

def test_get_next_id_uses_highest_existing_id():
    entries = [
        {"id": 2},
        {"id": 7},
        {"id": 4},
    ]

    assert get_next_id(entries) == 8

def test_create_logbook_entry_creates_complete_entry():
    entries = [
        {"id": 3},
        {"id": 5},
    ]

    entry = create_logbook_entry(
        entries=entries,
        title="  Heat diffusion test run  ",
        parameters=[
            (" grid_size ", " 100 x 100 "),
            ("time_step", " 0.01 s "),
        ],
        result_summary="  Initial result.  ",
        data_file="  data/input.csv  ",
        notes="  First test run.  ",
    )

    assert entry == {
        "id": 6,
        "title": "Heat diffusion test run",
        "created_date": datetime.now(UTC).astimezone().date().isoformat(),
        "parameters": {
            "grid_size": "100 x 100",
            "time_step": "0.01 s",
        },
        "status": "open",
        "result_summary": "Initial result.",
        "data_file": "data/input.csv",
        "notes": "First test run.",
    }

def test_create_logbook_entry_uses_empty_optional_values():
    entry = create_logbook_entry(
        entries=[],
        title="Particle movement simulation",
    )

    assert entry["id"] == 1
    assert entry["parameters"] == {}
    assert entry["status"] == "open"
    assert entry["result_summary"] == ""
    assert entry["data_file"] == ""
    assert entry["notes"] == ""

def test_create_logbook_entry_rejects_empty_title():
    with pytest.raises(
        ValueError,
        match="Title must not be empty",
    ):
        create_logbook_entry(
            entries=[],
            title="   ",
        )

def test_create_logbook_entry_rejects_invalid_parameters():
    with pytest.raises(
        ValueError,
        match="Parameter name 'method' is duplicated",
    ):
        create_logbook_entry(
            entries=[],
            title="Particle movement simulation",
            parameters=[
                ("Method", "Euler"),
                ("method", "RK4"),
            ],
        )

def make_filter_test_entries():
    return [
        {
            "id": 2,
            "title": "Particle movement simulation",
            "status": "completed",
        },
        {
            "id": 5,
            "title": "Heat diffusion test run",
            "status": "open",
        },
        {
            "id": 3,
            "title": "Repeated HEAT simulation",
            "status": "completed",
        },
    ]

def test_sort_entries_by_id_returns_descending_order():
    entries = make_filter_test_entries()

    result = sort_entries_by_id(entries)

    assert [entry["id"] for entry in result] == [5, 3, 2]

def test_sort_entries_by_id_does_not_modify_original_order():
    entries = make_filter_test_entries()

    sort_entries_by_id(entries)

    assert [entry["id"] for entry in entries] == [2, 5, 3]

def test_filter_entries_by_status_returns_matching_entries():
    entries = make_filter_test_entries()

    result = filter_entries_by_status(entries, " COMPLETED ")

    assert [entry["id"] for entry in result] == [3, 2]

def test_filter_entries_by_status_returns_empty_list_without_matches():
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "status": "open",
        }
    ]

    result = filter_entries_by_status(entries, "completed")

    assert result == []

def test_filter_entries_by_status_rejects_invalid_status():
    entries = make_filter_test_entries()

    with pytest.raises(
        ValueError,
        match="Status must be either 'open' or 'completed'",
    ):
        filter_entries_by_status(entries, "running")

def test_filter_entries_by_title_uses_case_insensitive_partial_search():
    entries = make_filter_test_entries()

    result = filter_entries_by_title(entries, " heat ")

    assert [entry["id"] for entry in result] == [5, 3]

def test_filter_entries_by_title_returns_empty_list_without_matches():
    entries = make_filter_test_entries()

    result = filter_entries_by_title(entries, "climate")

    assert result == []

def test_filter_entries_by_title_rejects_empty_search_term():
    entries = make_filter_test_entries()

    with pytest.raises(
        ValueError,
        match="Search term must not be empty",
    ):
        filter_entries_by_title(entries, "   ")

def test_complete_logbook_entry_changes_open_entry():
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "status": "open",
        },
        {
            "id": 2,
            "title": "Particle movement simulation",
            "status": "open",
        },
    ]

    changed = complete_logbook_entry(entries, 2)

    assert changed is True
    assert entries == [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "status": "open",
        },
        {
            "id": 2,
            "title": "Particle movement simulation",
            "status": "completed",
        },
    ]

def test_complete_logbook_entry_leaves_completed_entry_unchanged():
    entries = [
        {
            "id": 2,
            "title": "Particle movement simulation",
            "status": "completed",
        }
    ]

    original_entries = [entry.copy() for entry in entries]

    changed = complete_logbook_entry(entries, 2)

    assert changed is False
    assert entries == original_entries

def test_complete_logbook_entry_rejects_nonexistent_id():
    entries = [
        {
            "id": 1,
            "title": "Heat diffusion test run",
            "status": "open",
        }
    ]

    original_entries = [entry.copy() for entry in entries]

    with pytest.raises(
        ValueError,
        match="Logbook entry with ID 7 does not exist",
    ):
        complete_logbook_entry(entries, 7)

    assert entries == original_entries
