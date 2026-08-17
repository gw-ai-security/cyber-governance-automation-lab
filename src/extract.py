# json is part of Python's standard library.
# We use it to convert JSON file content into normal Python objects.
import json

# pandas is used for reading and processing tabular CSV data.
import pandas as pd

# Path provides an operating-system-independent way to work with file paths.
# This is preferable to manually building paths with strings.
from pathlib import Path


# These fields are required for every Control Catalog entry.
# A set is useful because we can efficiently compare required and available fields.
REQUIRED_CONTROL_FIELDS = {
    "control_id",
    "control_name",
    "control_statement",
    "business_unit",
    "owner_role",
    "owner_email",
    "frequency",
    "risk_level",
}


# These columns are required in the raw Evidence Submission CSV.
# The order matches the canonical raw-data contract.
EXPECTED_SUBMISSION_COLUMNS = [
    "submission_id",
    "control_id",
    "reporting_period",
    "due_date",
    "status",
    "evidence_reference",
    "submitted_at",
    "submitted_by",
    "comment",
]


# These columns are required in the raw Action CSV.
# The order matches the canonical raw-data contract.
EXPECTED_ACTION_COLUMNS = [
    "action_id",
    "control_id",
    "submission_id",
    "owner_email",
    "created_at",
    "due_date",
    "status",
    "reminder_count",
    "last_reminder_at",
    "description",
]


def load_control_catalog(file_path: Path) -> list[dict]:
    """
    Load the Control Catalog from a JSON file.

    The function reads and parses the file and checks the basic
    structural requirements of the Control Catalog.

    Business validation is handled in later pipeline stages.
    """

    # Open the JSON file in read mode using UTF-8 encoding.
    with file_path.open("r", encoding="utf-8") as file:
        # Convert the JSON content into normal Python objects.
        control_catalog = json.load(file)

    # The Control Catalog must be a JSON array.
    # json.load() converts a JSON array into a Python list.
    if not isinstance(control_catalog, list):
        raise ValueError(
            "Control Catalog must contain a top-level JSON array."
        )

    # Every item in the Control Catalog must be a JSON object.
    # JSON objects are represented as dictionaries in Python.
    if not all(isinstance(control, dict) for control in control_catalog):
        raise ValueError(
            "Every Control Catalog entry must be a JSON object."
        )

    # Check every Control entry for the required physical fields.
    for index, control in enumerate(control_catalog, start=1):
        # Determine which required fields are missing from this Control.
        missing_fields = REQUIRED_CONTROL_FIELDS.difference(
            control.keys()
        )

        # Stop the pipeline if one or more required fields are missing.
        if missing_fields:
            # Sort the field names so the error message is deterministic.
            missing_fields_text = ", ".join(
                sorted(missing_fields)
            )

            raise ValueError(
                f"Control Catalog entry {index} is missing required field(s): "
                f"{missing_fields_text}"
            )

    # Track Control IDs that have already been seen.
    # A set is useful because membership checks are simple and efficient.
    seen_control_ids = set()

    # Check that every Control ID occurs only once in the catalog.
    for control in control_catalog:
        control_id = control["control_id"]

        # Stop the pipeline if the same Control ID appears more than once.
        if control_id in seen_control_ids:
            raise ValueError(
                f"Duplicate control_id found in Control Catalog: {control_id}"
            )

        # Remember this Control ID for the following iterations.
        seen_control_ids.add(control_id)

    # Return the parsed and structurally checked Control Catalog.
    return control_catalog


def load_submissions(file_path: Path) -> pd.DataFrame:
    """
    Load the raw Evidence Submission CSV into a pandas DataFrame.

    Raw values are preserved as strings so that normalization and
    Data Quality validation can be handled explicitly in later stages.
    """

    # Read the CSV as strings and preserve empty fields and literal text values.
    submissions = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )

    # Determine whether required Submission columns are missing.
    missing_columns = set(EXPECTED_SUBMISSION_COLUMNS).difference(
        submissions.columns
    )

    # Stop the pipeline if one or more required columns are missing.
    if missing_columns:
        # Sort the column names so the error message is deterministic.
        missing_columns_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"Submission CSV is missing required column(s): "
            f"{missing_columns_text}"
        )

    # Return the raw and structurally checked tabular data to the caller.
    return submissions


def load_actions(file_path: Path) -> pd.DataFrame:
    """
    Load the raw Action CSV into a pandas DataFrame.

    Raw values are preserved as strings so that normalization and
    validation can be handled explicitly in later pipeline stages.
    """

    # Read the CSV as strings and preserve empty fields and literal text values.
    actions = pd.read_csv(
        file_path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )

    # Determine whether required Action columns are missing.
    missing_columns = set(EXPECTED_ACTION_COLUMNS).difference(
        actions.columns
    )

    # Stop the pipeline if one or more required columns are missing.
    if missing_columns:
        # Sort the column names so the error message is deterministic.
        missing_columns_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"Action CSV is missing required column(s): "
            f"{missing_columns_text}"
        )

    # Return the raw and structurally checked Action data.
    return actions