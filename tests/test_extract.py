import json

import pytest

from src.extract import (
    EXPECTED_ACTION_COLUMNS,
    EXPECTED_SUBMISSION_COLUMNS,
    load_actions,
    load_control_catalog,
    load_submissions,
)


def _write_csv(path, columns, row):
    path.write_text(
        ",".join(columns) + "\n" + ",".join(row) + "\n",
        encoding="utf-8",
    )


def test_csv_extract_preserves_literal_null_tokens(tmp_path):
    path = tmp_path / "submissions.csv"
    row = [
        "SUB-001",
        "CTRL-001",
        "2026-Q1",
        "2026-04-10",
        "Not Submitted",
        "NULL",
        "",
        "",
        "N/A",
    ]
    _write_csv(path, EXPECTED_SUBMISSION_COLUMNS, row)

    submissions = load_submissions(path)

    assert list(submissions.columns) == EXPECTED_SUBMISSION_COLUMNS
    assert submissions.loc[0, "evidence_reference"] == "NULL"
    assert submissions.loc[0, "submitted_at"] == ""
    assert submissions.loc[0, "comment"] == "N/A"


@pytest.mark.parametrize(
    ("loader", "columns", "dataset_name"),
    [
        (load_submissions, EXPECTED_SUBMISSION_COLUMNS, "Submission"),
        (load_actions, EXPECTED_ACTION_COLUMNS, "Action"),
    ],
)
def test_csv_extract_rejects_wrong_column_order(
    tmp_path,
    loader,
    columns,
    dataset_name,
):
    path = tmp_path / "input.csv"
    reordered = columns[1:] + columns[:1]
    _write_csv(path, reordered, [""] * len(reordered))

    with pytest.raises(
        ValueError,
        match=f"{dataset_name} CSV header.*wrong order",
    ):
        loader(path)


@pytest.mark.parametrize(
    ("loader", "columns", "dataset_name"),
    [
        (load_submissions, EXPECTED_SUBMISSION_COLUMNS, "Submission"),
        (load_actions, EXPECTED_ACTION_COLUMNS, "Action"),
    ],
)
def test_csv_extract_rejects_missing_or_unexpected_columns(
    tmp_path,
    loader,
    columns,
    dataset_name,
):
    path = tmp_path / "input.csv"
    changed = columns[:-1] + ["unexpected_column"]
    _write_csv(path, changed, [""] * len(changed))

    with pytest.raises(
        ValueError,
        match=f"{dataset_name} CSV header.*missing:.*unexpected:",
    ):
        loader(path)


def test_control_catalog_rejects_duplicate_ids(tmp_path):
    control = {
        "control_id": "CTRL-001",
        "control_name": "Control",
        "control_statement": "Statement",
        "business_unit": "IT",
        "owner_role": "Owner",
        "owner_email": "owner@example.com",
        "frequency": "Quarterly",
        "risk_level": "High",
    }
    path = tmp_path / "controls.json"
    path.write_text(
        json.dumps([control, control]),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate control_id"):
        load_control_catalog(path)


def test_csv_extract_rejects_row_with_extra_field(tmp_path):
    path = tmp_path / "submissions.csv"
    row = [
        "SUB-001",
        "CTRL-001",
        "2026-Q1",
        "2026-04-10",
        "Compliant",
        "EVID-001",
        "2026-04-10",
        "reviewer@example.com",
        "Complete",
        "unexpected",
    ]
    _write_csv(path, EXPECTED_SUBMISSION_COLUMNS, row)

    with pytest.raises(
        ValueError,
        match=r"Submission CSV row 2 has 10 field\(s\); expected 9",
    ):
        load_submissions(path)
