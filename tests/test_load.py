import csv
import json
from datetime import date

import pandas as pd
import pytest

from src.load import (
    AI_REVIEW_QUEUE_FILENAME,
    CURATED_CONTROL_STATUS_FILENAME,
    DATA_QUALITY_ISSUES_FILENAME,
    write_ai_review_queue,
    write_pipeline_outputs,
)
from src.transform import CURATED_COLUMNS
from src.validate import DQ_ISSUE_COLUMNS


def _prepared_outputs():
    curated = pd.DataFrame(
        [
            {
                "source_row_number": 1,
                "submission_id": "SUB-001",
                "control_id": "CTRL-001",
                "control_name": "Control",
                "business_unit": "IT Operations",
                "owner_role": "Owner",
                "owner_email": pd.NA,
                "frequency": "Monthly",
                "risk_level": "High",
                "reporting_period": "2026-07",
                "due_date": date(2026, 8, 10),
                "submission_status": "Not Submitted",
                "evidence_present": False,
                "submitted_at": pd.NaT,
                "comment": None,
                "overdue_flag": True,
                "submission_late": False,
                "days_overdue": 5.0,
                "days_late": pd.NA,
                "data_quality_status": "Valid",
                "active_action_id": pd.NA,
                "active_action_status": pd.NA,
                "active_action_due_date": pd.NaT,
                "reminder_count": 2.0,
                "last_reminder_at": date(2026, 8, 15),
            }
        ],
        columns=CURATED_COLUMNS,
    )
    dq_issues = pd.DataFrame(
        [
            {
                "issue_id": "DQI-0001",
                "submission_id": None,
                "control_id": pd.NA,
                "source_row_number": 1,
                "rule": "DQ-001 Missing Required Field",
                "severity": "High",
                "field": "submission_id",
                "message": "Required field(s) missing: submission_id.",
            }
        ],
        columns=DQ_ISSUE_COLUMNS,
    )
    queue = {
        "as_of_date": "2026-08-15",
        "items": [
            {
                "submission_id": "SUB-001",
                "review_reasons": ["Overdue"],
            }
        ],
    }
    return curated, dq_issues, queue


def test_pipeline_output_serialization_contract(tmp_path):
    curated, dq_issues, queue = _prepared_outputs()
    output_directory = tmp_path / "nested" / "curated"

    paths = write_pipeline_outputs(
        curated,
        dq_issues,
        queue,
        output_directory,
    )

    assert output_directory.is_dir()
    assert paths == {
        "curated_control_status": (
            output_directory / CURATED_CONTROL_STATUS_FILENAME
        ),
        "data_quality_issues": (
            output_directory / DATA_QUALITY_ISSUES_FILENAME
        ),
        "ai_review_queue": (
            output_directory / AI_REVIEW_QUEUE_FILENAME
        ),
    }

    with paths["curated_control_status"].open(
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        assert reader.fieldnames == CURATED_COLUMNS

    assert len(rows) == 1
    row = rows[0]
    assert row["due_date"] == "2026-08-10"
    assert row["evidence_present"] == "False"
    assert row["overdue_flag"] == "True"
    assert row["submission_late"] == "False"
    assert row["days_overdue"] == "5"
    assert row["days_late"] == ""
    assert row["reminder_count"] == "2"
    assert row["owner_email"] == ""
    assert row["submitted_at"] == ""
    assert row["last_reminder_at"] == "2026-08-15"
    assert "Unnamed: 0" not in row

    with paths["data_quality_issues"].open(
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        issue_rows = list(reader)
        assert reader.fieldnames == DQ_ISSUE_COLUMNS

    assert issue_rows[0]["submission_id"] == ""
    assert issue_rows[0]["control_id"] == ""

    forbidden_missing_text = {"NaN", "nan", "NaT", "<NA>", "None"}
    csv_text = paths["curated_control_status"].read_text(encoding="utf-8")
    assert all(token not in csv_text for token in forbidden_missing_text)

    parsed_queue = json.loads(
        paths["ai_review_queue"].read_text(encoding="utf-8")
    )
    assert parsed_queue == queue
    assert list(parsed_queue) == ["as_of_date", "items"]


def test_ai_queue_serialization_rejects_non_standard_nan(tmp_path):
    output_path = tmp_path / AI_REVIEW_QUEUE_FILENAME

    with pytest.raises(ValueError, match="Out of range float values"):
        write_ai_review_queue(
            {
                "as_of_date": "2026-08-15",
                "items": [{"days_overdue": float("nan")}],
            },
            output_path,
        )

    assert not output_path.exists()
