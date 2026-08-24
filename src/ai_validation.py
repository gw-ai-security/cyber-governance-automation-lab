import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


def load_json_object(path: Path | str) -> dict[str, Any]:
    """Load one UTF-8 JSON document and require an object at the top level."""

    document_path = Path(path)

    with document_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    if not isinstance(document, dict):
        raise TypeError(
            f"Expected a JSON object in {document_path}, "
            f"got {type(document).__name__}."
        )

    return document


def validate_control_review_output(
    output: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate one AI-assisted review output without repairing it.

    Successful validation proves structural conformance only. It does not
    establish factual correctness or governance approval.
    """

    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(output)
    return output


def validate_control_review_correlation(
    output: dict[str, Any],
    input_record: dict[str, Any],
) -> dict[str, Any]:
    """Require the AI output to preserve the reviewed Submission and Control."""

    for field in ("submission_id", "control_id"):
        if field not in input_record:
            raise KeyError(
                f"Controlled AI input is missing required correlation field: {field}"
            )

        if output.get(field) != input_record[field]:
            raise ValueError(
                f"AI review correlation mismatch for {field}: "
                f"expected {input_record[field]!r}, got {output.get(field)!r}."
            )

    return output


def validate_control_review_result(
    output: dict[str, Any],
    input_record: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Validate structure and input/output correlation without semantic repair."""

    validate_control_review_output(output, schema)
    return validate_control_review_correlation(output, input_record)


def validate_control_review_output_file(
    output_path: Path | str,
    schema_path: Path | str,
) -> dict[str, Any]:
    """Load and validate one stored AI review output against the schema."""

    output = load_json_object(output_path)
    schema = load_json_object(schema_path)
    return validate_control_review_output(output, schema)


def parse_and_validate_control_review_output(
    raw_output: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Parse a raw model response as JSON and validate it without repair."""

    output = json.loads(raw_output)

    if not isinstance(output, dict):
        raise TypeError(
            "Controlled AI review output must be a JSON object."
        )

    return validate_control_review_output(output, schema)
