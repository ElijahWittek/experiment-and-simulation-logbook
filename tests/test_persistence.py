import json

import pytest

from experiment_and_simulation_logbook.persistence import (
    load_logbook,
    save_logbook,
)


def make_valid_entry():
    return {
        "id": 1,
        "title": "Heat diffusion test run",
        "created_date": "2026-09-14",
        "parameters": {
            "grid_size": "100 x 100",
            "time_step": "0.01 s",
        },
        "status": "open",
        "result_summary": "",
        "data_file": "data/heat_diffusion_input.csv",
        "notes": "Initial test with default boundary conditions.",
    }

def test_save_and_load_logbook_preserves_data(tmp_path):
    path = tmp_path / "logbook.json"
    entries = [make_valid_entry()]

    save_logbook(entries, path)

    loaded_entries = load_logbook(path)

    assert loaded_entries == entries

def test_save_logbook_creates_json_file(tmp_path):
    path = tmp_path / "logbook.json"

    save_logbook([], path)

    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == []

def test_load_logbook_returns_empty_list_for_missing_file(tmp_path):
    path = tmp_path / "logbook.json"

    loaded_entries = load_logbook(path)

    assert loaded_entries == []

def test_load_logbook_rejects_empty_file(tmp_path):
    path = tmp_path / "logbook.json"
    path.write_text("", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Logbook file is empty",
    ):
        load_logbook(path)

def test_load_logbook_rejects_invalid_json(tmp_path):
    path = tmp_path / "logbook.json"
    path.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Logbook file contains invalid JSON",
    ):
        load_logbook(path)

def test_load_logbook_rejects_invalid_logbook_structure(tmp_path):
    path = tmp_path / "logbook.json"
    path.write_text(
        "{}",
        encoding="utf-8",
    )

    with pytest.raises(
        TypeError,
        match="Stored logbook data must be a list",
    ):
        load_logbook(path)

def test_save_logbook_rejects_invalid_data(tmp_path):
    path = tmp_path / "logbook.json"
    invalid_entries = [
        {
            "id": 1,
            "title": "",
        }
    ]

    with pytest.raises(ValueError):
        save_logbook(invalid_entries, path)

    assert not path.exists()