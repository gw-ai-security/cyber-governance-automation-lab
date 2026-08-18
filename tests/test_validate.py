from copy import deepcopy

import pandas as pd
import pytest

from src.validate import DQ_ISSUE_COLUMNS, validate_submissions


CONTROL_CATALOG = pd.DataFrame(
    [
        {
            "control_id": "CTRL-001",
            "frequency": "Quarterly",
        }
    ]
)

VALID_SUBMISSION = {
    "source_row_number": 1,
    "submission_id": "SUB-001",
    "control_id": "CTRL-001",
    "reporting_period": "2026-Q1",
    "due_date": "2026-04-10",
    "status": "Compliant",
    "evidence_reference": "EVID-001",
    "submitted_at": "2026-04-10",
    "submitted_by": "reviewer@example.com",
    "comment": "Complete",
}


def _issues_for(changes):
    row = deepcopy(VALID_SUBMISSION)
    row.update(changes)
    return validate_submissions(
        pd.DataFrame([row]),
        CONTROL_CATALOG,
    )


@pytest.mark.parametrize(
    ("changes", "expected_rule", "expected_severity"),
    [
        (
            {"control_id": pd.NA},
            "DQ-001 Missing Required Field",
            "High",
        ),
        (
            {"control_id": "CTRL-999"},
            "DQ-002 Unknown Control ID",
            "High",
        ),
        (
            {"status": "Pending"},
            "DQ-003 Invalid Status",
            "High",
        ),
        (
            {"evidence_reference": pd.NA},
            "DQ-004 Missing Evidence",
            "High",
        ),
        (
            {"reporting_period": "2026-01"},
            "DQ-006 Invalid Reporting Period",
            "Medium",
        ),
        (
            {"due_date": "2026-04-11"},
            "DQ-007 Invalid Due Date",
            "High",
        ),
        (
            {
                "status": "Not Submitted",
                "evidence_reference": pd.NA,
            },
            "DQ-008 Invalid Submission State",
            "High",
        ),
        (
            {
                "status": "Not Submitted",
                "submitted_at": pd.NA,
                "submitted_by": pd.NA,
            },
            "DQ-009 Invalid Evidence State",
            "Medium",
        ),
        (
            {"submitted_by": "invalid-email"},
            "DQ-010 Invalid Submitter Email",
            "Medium",
        ),
    ],
)
def test_individual_submission_rules(
    changes,
    expected_rule,
    expected_severity,
):
    issues = _issues_for(changes)

    assert expected_rule in set(issues["rule"])
    issue = issues.loc[issues["rule"] == expected_rule].iloc[0]
    assert issue["severity"] == expected_severity


def test_duplicate_business_key_flags_every_participating_row():
    first = deepcopy(VALID_SUBMISSION)
    second = deepcopy(VALID_SUBMISSION)
    second["source_row_number"] = 2
    second["submission_id"] = "SUB-002"

    issues = validate_submissions(
        pd.DataFrame([first, second]),
        CONTROL_CATALOG,
    )

    duplicates = issues.loc[
        issues["rule"] == "DQ-005 Duplicate Submission"
    ]
    assert duplicates["source_row_number"].tolist() == [1, 2]
    assert duplicates["field"].tolist() == [
        "control_id,reporting_period",
        "control_id,reporting_period",
    ]


def test_unknown_control_skips_frequency_dependent_rules():
    issues = _issues_for(
        {
            "control_id": "CTRL-999",
            "reporting_period": "bad-period",
            "due_date": "bad-date",
        }
    )

    assert issues["rule"].tolist() == [
        "DQ-002 Unknown Control ID"
    ]


def test_valid_submission_returns_exact_empty_schema():
    issues = _issues_for({})

    assert issues.empty
    assert list(issues.columns) == DQ_ISSUE_COLUMNS


def test_issue_ids_follow_source_row_and_rule_order():
    first = deepcopy(VALID_SUBMISSION)
    first.update(
        {
            "status": "Not Submitted",
            "evidence_reference": "EVID-001",
        }
    )
    second = deepcopy(VALID_SUBMISSION)
    second["source_row_number"] = 2
    second["control_id"] = "CTRL-999"

    issues = validate_submissions(
        pd.DataFrame([second, first]),
        CONTROL_CATALOG,
    )

    assert issues["issue_id"].tolist() == [
        f"DQI-{index:04d}"
        for index in range(1, len(issues) + 1)
    ]
    assert issues["source_row_number"].tolist() == sorted(
        issues["source_row_number"].tolist()
    )
