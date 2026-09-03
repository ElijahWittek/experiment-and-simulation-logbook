"""Validation functions for logbook data."""


from datetime import date

VALID_STATUSES = {"open", "completed"}

LOGBOOK_FIELDS = {
    "id",
    "title",
    "created_date",
    "parameters",
    "status",
    "result_summary",
    "data_file",
    "notes",
}


def validate_title(title: str) -> str:
    """Validate and clean a logbook entry title."""
    cleaned_title = title.strip()

    if not cleaned_title:
        raise ValueError("Title must not be empty.")

    return cleaned_title

def validate_search_term(search_term: str) -> str:
    """Validate and clean a title search term."""
    cleaned_search_term = search_term.strip()

    if not cleaned_search_term:
        raise ValueError("Search term must not be empty.")

    return cleaned_search_term

def validate_parameters(
        parameters: list[tuple[str, str]],
) -> dict[str, str]:
    """Validate and clean logbook parameters."""
    cleaned_parameters: dict[str, str] = {}
    normalized_names: set[str] = set()

    for name, value in parameters:
        cleaned_name = name.strip()
        cleaned_value = value.strip()

        if not cleaned_name:
            raise ValueError("Parameter name must not be empty.")

        if not cleaned_value:
            raise ValueError(
                f"Parameter value for '{cleaned_name}' must not be empty."
            )

        normalized_name = cleaned_name.casefold()

        if normalized_name in normalized_names:
            raise ValueError(
                f"Parameter name '{cleaned_name}' is duplicated."
            )

        normalized_names.add(normalized_name)
        cleaned_parameters[cleaned_name] = cleaned_value

    return cleaned_parameters

def validate_id_input(value: str) -> int:
    """Validate and convert a user-provided logbook entry ID."""
    cleaned_value = value.strip()

    try:
        entry_id = int(cleaned_value)
    except ValueError as error:
        raise ValueError("ID must be a positive integer.") from error

    if entry_id <= 0:
        raise ValueError("ID must be a positive integer.")

    return entry_id

def validate_status(status: str) -> str:
    """Validate and normalize a status value."""
    cleaned_status = status.strip().casefold()

    if cleaned_status not in VALID_STATUSES:
        raise ValueError(
            "Status must be either 'open' or 'completed'."
        )

    return cleaned_status

def clean_optional_text(value: str) -> str:
    """Remove leading and trailing whitespace from optional text."""
    return value.strip()

def validate_logbook_data(data: object) -> None:
    """Validate a complete stored logbook data structure."""
    if not isinstance(data, list):
        raise TypeError("Stored logbook data must be a list.")

    seen_ids: set[int] = set()

    for position, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise TypeError(
                f"Logbook entry {position} must be an object."
            )

        _validate_entry_fields(entry, position)
        _validate_stored_id(entry["id"], position, seen_ids)
        _validate_stored_title(entry["title"], position)
        _validate_stored_date(entry["created_date"], position)
        _validate_stored_parameters(entry["parameters"], position)
        _validate_stored_status(entry["status"], position)
        _validate_stored_optional_text_fields(entry, position)

def _validate_entry_fields(
        entry: dict,
        position: int,
) -> None:
    """Validate that a stored entry contains exactly the defined fields."""
    entry_fields = set(entry)

    if entry_fields == LOGBOOK_FIELDS:
        return

    missing_fields = LOGBOOK_FIELDS - entry_fields
    unexpected_fields = entry_fields - LOGBOOK_FIELDS
    details: list[str] = []

    if missing_fields:
        details.append(
            f"missing fields: {', '.join(sorted(missing_fields))}"
        )

    if unexpected_fields:
        details.append(
            f"unexpected fields: {', '.join(sorted(unexpected_fields))}"
        )

    raise ValueError(
        f"Logbook entry {position} has invalid fields "
        f"({'; '.join(details)})."
    )

def _validate_stored_id(
        entry_id: object,
        position: int,
        seen_ids: set[int],
) -> None:
    """Validate a stored entry ID and check its uniqueness."""
    if type(entry_id) is not int or entry_id <= 0:
        raise ValueError(
            f"Logbook entry {position} has an invalid ID."
        )

    if entry_id in seen_ids:
        raise ValueError(
            f"Duplicate logbook entry ID: {entry_id}."
        )

    seen_ids.add(entry_id)

def _validate_stored_title(
    title: object,
    position: int,
) -> None:
    """Validate a stored entry title."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError(
            f"Logbook entry {position} has an invalid title."
        )


def _validate_stored_date(
    created_date: object,
    position: int,
) -> None:
    """Validate a stored creation date."""
    if not isinstance(created_date, str):
        raise TypeError(
            f"Logbook entry {position} has an invalid created_date."
        )

    try:
        parsed_date = date.fromisoformat(created_date)
    except ValueError as error:
        raise ValueError(
            f"Logbook entry {position} has an invalid created_date."
        ) from error

    if parsed_date.isoformat() != created_date:
        raise ValueError(
            f"Logbook entry {position} has an invalid created_date."
        )


def _validate_stored_parameters(
    parameters: object,
    position: int,
) -> None:
    """Validate parameters stored in a logbook entry."""
    if not isinstance(parameters, dict):
        raise TypeError(
            f"Logbook entry {position} has invalid parameters."
        )

    normalized_names: set[str] = set()

    for name, value in parameters.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Logbook entry {position} has an invalid parameter name."
            )

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Logbook entry {position} has an invalid parameter value."
            )

        normalized_name = name.strip().casefold()

        if normalized_name in normalized_names:
            raise ValueError(
                f"Logbook entry {position} has duplicate parameter names."
            )

        normalized_names.add(normalized_name)


def _validate_stored_status(
    status: object,
    position: int,
) -> None:
    """Validate a status stored in a logbook entry."""
    if not isinstance(status, str) or status not in VALID_STATUSES:
        raise ValueError(
            f"Logbook entry {position} has an invalid status."
        )


def _validate_stored_optional_text_fields(
    entry: dict,
    position: int,
) -> None:
    """Validate optional text fields stored in a logbook entry."""
    for field_name in ("result_summary", "data_file", "notes"):
        if not isinstance(entry[field_name], str):
            raise TypeError(
                f"Logbook entry {position} has an invalid "
                f"{field_name} value."
            )
