import pytest

from experiment_and_simulation_logbook.validation import (
    clean_optional_text,
    validate_id_input,
    validate_logbook_data,
    validate_parameters,
    validate_status,
    validate_title,
)


def test_validate_title_returns_cleaned_title():
    title = validate_title(" Heat diffusion test run ")

    assert title == "Heat diffusion test run"

def test_validate_title_rejects_empty_title():
    with pytest.raises(ValueError, match="Title must not be empty."):
        validate_title("   ")

def test_validate_parameters_returns_cleaned_parameters():
    parameters = [
        (" grid_size ", " 100 x 100 "),
        ("time_step", " 0.01 s "),
    ]

    result = validate_parameters(parameters)

    assert result == {
        "grid_size": "100 x 100",
        "time_step": "0.01 s",
    }

def test_validate_parameters_allows_empty_parameter_list():
    assert validate_parameters([]) == {}

def test_validate_parameters_rejects_empty_name():
    parameters = [("   ", "1000")]

    with pytest.raises(ValueError, match="Parameter name must not be empty."):
        validate_parameters(parameters)

def test_validate_parameters_rejects_empty_value():
    parameters = [("iterations", "   ")]

    with pytest.raises(
        ValueError,
        match="Parameter value for 'iterations' must not be empty.",
    ):
        validate_parameters(parameters)

def test_validate_parameters_rejects_duplicate_names_case_insensitively():
    parameters = [
        ("Method", "Euler"),
        ("method", "RK4"),
    ]

    with pytest.raises(
        ValueError,
        match="Parameter name 'method' is duplicated.",
    ):
        validate_parameters(parameters)

def test_validate_id_input_returns_positive_integer():
    assert validate_id_input(" 12 ") == 12

@pytest.mark.parametrize(
    "value",
    ["", "abc", "3.5", "0", "-4"],
)
def test_validate_id_input_rejects_invalid_values(value):
    with pytest.raises(
        ValueError,
        match="ID must be a positive integer",
    ):
        validate_id_input(value)

@pytest.mark.parametrize(
    ("status", "expected"),
    [
        ("open", "open"),
        ("OPEN", "open"),
        (" Completed ", "completed"),
    ],
)
def test_validate_status_returns_normalized_status(status, expected):
    assert validate_status(status) == expected

def test_validate_status_rejects_invalid_status():
    with pytest.raises(
        ValueError,
        match="Status must be either 'open' or 'completed'",
    ):
        validate_status("running")

def test_clean_optional_text_returns_cleaned_text():
    assert clean_optional_text("  Test notes.  ") == "Test notes."

def test_clean_optional_text_allows_empty_text():
    assert clean_optional_text("   ") == ""

def make_valid_stored_entry(entry_id=1):
    return {
        "id": entry_id,
        "title": "Heat diffusion test run",
        "created_date": "2026-09-14",
        "parameters": {
            "grid_size": "100 x 100",
            "time_step": "0.01 s",
        },
        "status": "open",
        "result_summary": "",
        "data_file": "data/input.csv",
        "notes": "Test entry.",
    }

def test_validate_logbook_data_accepts_valid_data():
    data = [make_valid_stored_entry()]

    validate_logbook_data(data)

    assert data == [make_valid_stored_entry()]

def test_validate_logbook_data_accepts_empty_logbook():
    validate_logbook_data([])

def test_validate_logbook_data_rejects_non_list_structure():
    with pytest.raises(
        TypeError,
        match="Stored logbook data must be a list",
    ):
        validate_logbook_data({})

def test_validate_logbook_data_rejects_missing_field():
    entry = make_valid_stored_entry()
    del entry["notes"]

    with pytest.raises(
        ValueError,
        match="missing fields",
    ):
        validate_logbook_data([entry])

def test_validate_logbook_data_rejects_unexpected_field():
    entry = make_valid_stored_entry()
    entry["unexpected_field"] = "unexpected"

    with pytest.raises(
        ValueError,
        match="unexpected fields",
    ):
        validate_logbook_data([entry])


@pytest.mark.parametrize(
    "entry_id",
    [0, -1, "1", True],
)
def test_validate_logbook_data_rejects_invalid_id(entry_id):
    entry = make_valid_stored_entry()
    entry["id"] = entry_id

    with pytest.raises(
        ValueError,
        match="invalid ID",
    ):
        validate_logbook_data([entry])


def test_validate_logbook_data_rejects_duplicate_ids():
    first_entry = make_valid_stored_entry(1)
    second_entry = make_valid_stored_entry(1)

    with pytest.raises(
        ValueError,
        match="Duplicate logbook entry ID",
    ):
        validate_logbook_data([first_entry, second_entry])


@pytest.mark.parametrize(
    "created_date",
    [
        "2026-02-30",
        "2026-9-14",
        "14.09.2026",
    ],
)
def test_validate_logbook_data_rejects_invalid_created_date(
    created_date,
):
    entry = make_valid_stored_entry()
    entry["created_date"] = created_date

    with pytest.raises(
        ValueError,
        match="invalid created_date",
    ):
        validate_logbook_data([entry])


def test_validate_logbook_data_rejects_invalid_parameters_structure():
    entry = make_valid_stored_entry()
    entry["parameters"] = []

    with pytest.raises(
        TypeError,
        match="invalid parameters",
    ):
        validate_logbook_data([entry])


def test_validate_logbook_data_rejects_duplicate_parameter_names():
    entry = make_valid_stored_entry()
    entry["parameters"] = {
        "Method": "Euler",
        "method": "RK4",
    }

    with pytest.raises(
        ValueError,
        match="duplicate parameter names",
    ):
        validate_logbook_data([entry])


def test_validate_logbook_data_rejects_non_lowercase_status():
    entry = make_valid_stored_entry()
    entry["status"] = "OPEN"

    with pytest.raises(
        ValueError,
        match="invalid status",
    ):
        validate_logbook_data([entry])


@pytest.mark.parametrize(
    "field_name",
    ["result_summary", "data_file", "notes"],
)
def test_validate_logbook_data_rejects_non_text_optional_field(
    field_name,
):
    entry = make_valid_stored_entry()
    entry[field_name] = None

    with pytest.raises(
        TypeError,
        match=f"invalid {field_name} value",
    ):
        validate_logbook_data([entry])
